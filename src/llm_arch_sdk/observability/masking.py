import re 

from llm_guard.input_scanners import Anonymize
from llm_guard.input_scanners.anonymize_helpers import BERT_LARGE_NER_CONF
from llm_guard.vault import Vault

vault = Vault()  

def create_anonymize_scanner():
    scanner = Anonymize(
        vault,
        recognizer_conf=BERT_LARGE_NER_CONF,
        language="en"
    )
    return scanner

def masking_secret(data: any, **kwargs) -> any:
    """Function to mask sensitive data before sending to Langfuse."""
    if isinstance(data, str) and data.startswith("SECRET_"):
        return "[REDACTED]"
 
    # For more complex data structures
    elif isinstance(data, dict):
        return {k: masking_secret(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [masking_secret(item) for item in data]
    
    return data


def masking_credit_card(data, **kwargs) -> any:
    if isinstance(data, str):
        # Regular expression to match credit card numbers (Visa, MasterCard, AmEx, etc.)
        pattern = r'\b(?:\d[ -]*?){13,19}\b'
        data = re.sub(pattern, '[REDACTED CREDIT CARD]', data)
    return data


def masking_PII(data, **kwargs) -> any:
    if isinstance(data, str):
        scanner = create_anonymize_scanner()
        # Scan and redact the data
        sanitized_data, is_valid, risk_score = scanner.scan(data)
        print(f"Original: {data} | Sanitized: {sanitized_data} | Valid: {is_valid} | Risk Score: {risk_score}")
        return sanitized_data
    return data

def masking_email_and_phone(data, **kwargs):
    if isinstance(data, str):
        # Mask email addresses
        data = re.sub(r'\b[\w.-]+?@\w+?\.\w+?\b', '[REDACTED EMAIL]', data)
        # Mask phone numbers
        data = re.sub(r'\b(?:\d{3}[-. ]?\d{3}[-. ]?\d{4}|\d{3}[-. ]?\d{3}[-. ]?\d{3})\b', '[REDACTED CELLPHONE]', data)
    return data