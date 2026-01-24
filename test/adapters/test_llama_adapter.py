import pytest
import os
from unittest.mock import Mock, patch
from llm_arch_sdk.adapters.llama_adapter import LlamaAdapter
from llm_arch_sdk.client.llm_client import LlmClient


class TestLlamaAdapter:
    @patch.dict(os.environ, {'LLM_BASE_URL': 'http://localhost:8000'}, clear=True)
    @patch('llm_arch_sdk.adapters.llama_adapter.TokenManager')
    @patch('llm_arch_sdk.adapters.llama_adapter.AuthHttpClientFactory')
    def test_init_with_env_var(self, mock_auth_factory, mock_token_manager):
        mock_auth = Mock()
        mock_token_manager.return_value = mock_auth
        mock_http_client = Mock()
        mock_auth_factory.create.return_value = mock_http_client

        adapter = LlamaAdapter()

        assert adapter.base_url == 'http://localhost:8000'
        assert adapter.timeout == 60.0
        mock_token_manager.assert_called_once()
        mock_auth_factory.create.assert_called_once_with(
            auth=mock_auth,
            timeout=60.0
        )

    def test_init_with_custom_base_url(self):
        with patch('llm_arch_sdk.adapters.llama_adapter.TokenManager') as mock_token_manager, \
             patch('llm_arch_sdk.adapters.llama_adapter.AuthHttpClientFactory') as mock_auth_factory:

            mock_auth = Mock()
            mock_token_manager.return_value = mock_auth
            mock_http_client = Mock()
            mock_auth_factory.create.return_value = mock_http_client

            adapter = LlamaAdapter(base_url="http://custom:9000", timeout=30.0)

            assert adapter.base_url == "http://custom:9000"
            assert adapter.timeout == 30.0
            mock_auth_factory.create.assert_called_once_with(
                auth=mock_auth,
                timeout=30.0
            )

    @patch.dict(os.environ, {}, clear=True)
    def test_init_missing_base_url(self):
        with pytest.raises(RuntimeError, match="LLM_BASE_URL no configurada"):
            LlamaAdapter()

    @patch.dict(os.environ, {'LLM_BASE_URL': 'http://localhost:8000'}, clear=True)
    @patch('llm_arch_sdk.adapters.llama_adapter.TokenManager')
    @patch('llm_arch_sdk.adapters.llama_adapter.AuthHttpClientFactory')
    @patch('llm_arch_sdk.adapters.llama_adapter.LlmClient')
    def test_client_lazy_initialization(self, mock_llm_client_class, mock_auth_factory, mock_token_manager):
        mock_auth = Mock()
        mock_token_manager.return_value = mock_auth
        mock_http_client = Mock()
        mock_auth_factory.create.return_value = mock_http_client

        mock_llm_client_instance = Mock(spec=LlmClient)
        mock_llm_client_class.return_value = mock_llm_client_instance

        adapter = LlamaAdapter()
        client1 = adapter.client()
        client2 = adapter.client()

        # Should return the same instance
        assert client1 is mock_llm_client_instance
        assert client2 is mock_llm_client_instance

        # LlmClient should be instantiated only once
        mock_llm_client_class.assert_called_once_with(
            base_url='http://localhost:8000',
            http_client=mock_http_client
        )

    @patch.dict(os.environ, {'LLM_BASE_URL': 'http://localhost:8000'}, clear=True)
    @patch('llm_arch_sdk.adapters.llama_adapter.TokenManager')
    @patch('llm_arch_sdk.adapters.llama_adapter.AuthHttpClientFactory')
    @patch('llm_arch_sdk.adapters.llama_adapter.LlmClient')
    def test_client_initialization_params(self, mock_llm_client_class, mock_auth_factory, mock_token_manager):
        mock_auth = Mock()
        mock_token_manager.return_value = mock_auth
        mock_http_client = Mock()
        mock_auth_factory.create.return_value = mock_http_client

        adapter = LlamaAdapter(base_url="http://test:8080", timeout=45.0)
        adapter.client()

        mock_llm_client_class.assert_called_once_with(
            base_url="http://test:8080",
            http_client=mock_http_client
        )