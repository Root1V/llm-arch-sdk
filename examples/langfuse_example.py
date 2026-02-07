import os
from langfuse import Langfuse, observe, propagate_attributes, get_client
from dotenv import load_dotenv
from llm_arch_sdk.observability.context import new_session_id, new_user_id
from llm_arch_sdk.observability.masking import masking_email_and_phone

load_dotenv()

public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
host = os.getenv("LANGFUSE_BASE_URL")
    
langfuse = Langfuse(
    public_key=public_key,
    secret_key=secret_key,
    host=host,
    mask=masking_email_and_phone
)

@observe()
def process_request(request):
    langfuse_client = get_client()
    with propagate_attributes(session_id=new_session_id(), user_id=new_user_id(), tags=["flow:login", "flow:request"]):
        # Simulate processing the request
        print(f"Processing request: {request}")
        
        langfuse_client.update_current_span(level="WARNING", status_message="Es es el mensaje de Warning" )
        
        return invoke_llm(request["payload"], langfuse_client)
        # You can add more attributes or events here as needed

@observe()
def invoke_llm(data, langfuse_client):
    print(f"Invoking LLM with data: {data}")
    
    langfuse_client.update_current_span(level="ERROR", status_message="Es es el mensaje de Error" ) 
    return "Please contact John at john.doe@example.com or call 555123457."

        

if __name__ == "__main__":
    # Simulate receiving a request
    request = {"endpoint": "/api/data", "method": "GET", "payload": {"key": "value"} }
    process_request(request)