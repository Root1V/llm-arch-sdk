import pytest
import httpx
import os
from unittest.mock import Mock, patch
from llm_arch_sdk.auth.token_manager import TokenManager, AuthError


class TestTokenManager:
    @patch.dict(os.environ, {
        'LLM_BASE_URL': 'http://localhost:8000',
        'LLM_USERNAME': 'testuser',
        'LLM_PASSWORD': 'testpass'
    })
    def test_init_success(self):
        manager = TokenManager()
        assert manager.base_url == 'http://localhost:8000'
        assert manager.username == 'testuser'
        assert manager.password == 'testpass'
        assert manager.token is None
        assert manager.timeout == 10.0

    @patch.dict(os.environ, {}, clear=True)
    def test_init_missing_env_vars(self):
        with pytest.raises(RuntimeError, match="LLM_BASE_URL no configurada"):
            TokenManager()

    @patch.dict(os.environ, {'LLM_BASE_URL': 'http://localhost:8000'}, clear=True)
    def test_init_missing_username(self):
        with pytest.raises(RuntimeError, match="LLM_USERNAME no configurado"):
            TokenManager()

    @patch.dict(os.environ, {
        'LLM_BASE_URL': 'http://localhost:8000',
        'LLM_USERNAME': 'testuser'
    }, clear=True)
    def test_init_missing_password(self):
        with pytest.raises(RuntimeError, match="LLM_PASSWORD no configurado"):
            TokenManager()

    @patch.dict(os.environ, {
        'LLM_BASE_URL': 'http://localhost:8000',
        'LLM_USERNAME': 'testuser',
        'LLM_PASSWORD': 'testpass'
    })
    @patch('llm_arch_sdk.auth.token_manager.HttpClientFactory')
    def test_login_success(self, mock_factory):
        mock_client = Mock()
        mock_factory.create.return_value = mock_client
        mock_response = Mock()
        mock_response.json.return_value = {'token': 'test_token'}
        mock_client.post.return_value = mock_response

        manager = TokenManager()
        token = manager._login()

        assert token == 'test_token'
        mock_client.post.assert_called_once_with(
            'http://localhost:8000/llm/login',
            auth=('testuser', 'testpass')
        )

    @patch.dict(os.environ, {
        'LLM_BASE_URL': 'http://localhost:8000',
        'LLM_USERNAME': 'testuser',
        'LLM_PASSWORD': 'testpass'
    })
    @patch('llm_arch_sdk.auth.token_manager.HttpClientFactory')
    def test_login_no_token_in_response(self, mock_factory):
        mock_client = Mock()
        mock_factory.create.return_value = mock_client
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_client.post.return_value = mock_response

        manager = TokenManager()
        with pytest.raises(AuthError, match="Error inesperado durante login"):
            manager._login()

    @patch.dict(os.environ, {
        'LLM_BASE_URL': 'http://localhost:8000',
        'LLM_USERNAME': 'testuser',
        'LLM_PASSWORD': 'testpass'
    })
    @patch('llm_arch_sdk.auth.token_manager.HttpClientFactory')
    def test_login_timeout(self, mock_factory):
        mock_client = Mock()
        mock_factory.create.return_value = mock_client
        mock_client.post.side_effect = httpx.TimeoutException("Timeout")

        manager = TokenManager()
        with pytest.raises(AuthError, match="Timeout durante login"):
            manager._login()

    @patch.dict(os.environ, {
        'LLM_BASE_URL': 'http://localhost:8000',
        'LLM_USERNAME': 'testuser',
        'LLM_PASSWORD': 'testpass'
    })
    @patch('llm_arch_sdk.auth.token_manager.HttpClientFactory')
    def test_login_http_error(self, mock_factory):
        mock_client = Mock()
        mock_factory.create.return_value = mock_client
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server Error", request=Mock(), response=mock_response
        )
        mock_client.post.return_value = mock_response

        manager = TokenManager()
        with pytest.raises(AuthError, match="Error HTTP durante login: 500"):
            manager._login()

    @patch.dict(os.environ, {
        'LLM_BASE_URL': 'http://localhost:8000',
        'LLM_USERNAME': 'testuser',
        'LLM_PASSWORD': 'testpass'
    })
    @patch('llm_arch_sdk.auth.token_manager.HttpClientFactory')
    def test_login_circuit_breaker_open(self, mock_factory):
        mock_client = Mock()
        mock_factory.create.return_value = mock_client

        manager = TokenManager()
        # Simulate circuit breaker open
        manager._circuit.allow_request = Mock(return_value=False)

        with pytest.raises(AuthError, match="Circuit breaker abierto: login bloqueado"):
            manager._login()

    @patch.dict(os.environ, {
        'LLM_BASE_URL': 'http://localhost:8000',
        'LLM_USERNAME': 'testuser',
        'LLM_PASSWORD': 'testpass'
    })
    @patch('llm_arch_sdk.auth.token_manager.HttpClientFactory')
    def test_auth_flow_first_request(self, mock_factory):
        mock_client = Mock()
        mock_factory.create.return_value = mock_client
        mock_response = Mock()
        mock_response.json.return_value = {'token': 'test_token'}
        mock_client.post.return_value = mock_response

        manager = TokenManager()
        request = httpx.Request("GET", "http://api.example.com/test")

        # Simulate auth_flow
        flow = manager.auth_flow(request)
        next(flow)  # Send request

        # Check token was attached
        assert request.headers["Authorization"] == "Bearer test_token"

        # Simulate response
        response = Mock()
        response.status_code = 200
        try:
            flow.send(response)
        except StopIteration:
            pass

    @patch.dict(os.environ, {
        'LLM_BASE_URL': 'http://localhost:8000',
        'LLM_USERNAME': 'testuser',
        'LLM_PASSWORD': 'testpass'
    })
    @patch('llm_arch_sdk.auth.token_manager.HttpClientFactory')
    def test_auth_flow_401_retry(self, mock_factory):
        mock_client = Mock()
        mock_factory.create.return_value = mock_client

        # First login response
        mock_response1 = Mock()
        mock_response1.json.return_value = {'token': 'token1'}
        # Second login response for retry
        mock_response2 = Mock()
        mock_response2.json.return_value = {'token': 'token2'}

        mock_client.post.side_effect = [mock_response1, mock_response2]

        manager = TokenManager()
        request = httpx.Request("GET", "http://api.example.com/test")

        flow = manager.auth_flow(request)
        next(flow)  # Send request

        # Simulate 401 response
        response_401 = Mock()
        response_401.status_code = 401
        try:
            flow.send(response_401)
        except StopIteration:
            pass

        # Should have retried and attached new token
        assert request.headers["Authorization"] == "Bearer token2"
        assert request.headers["X-Retry"] == "1"