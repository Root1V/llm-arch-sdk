import os
from langfuse import Langfuse, observe, propagate_attributes
from dotenv import load_dotenv
from llm_arch_sdk.observability.context import new_session_id, new_user_id

load_dotenv()

public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
secret_key = os.getenv("LANGFUSE_SECRET_KEY")
host = os.getenv("LANGFUSE_BASE_URL")
    
langfuse = Langfuse(
    public_key=public_key,
    secret_key=secret_key,
    host=host
)

@observe()
def process_request(request):
    with propagate_attributes(session_id=new_session_id(), user_id=new_user_id(), tags=["flow:login", "flow:request"]):
        # Simulate processing the request
        print(f"Processing request: {request}")
        return invoke_llm(request["payload"])
        # You can add more attributes or events here as needed

@observe()
def invoke_llm(data):
    print(f"Invoking LLM with data: {data}")
    return {"response": "This is a simulated LLM response."}

        
        
if __name__ == "__main__":
    # Simulate receiving a request
    request = {"endpoint": "/api/data", "method": "GET", "payload": {"key": "value"} }
    process_request(request)