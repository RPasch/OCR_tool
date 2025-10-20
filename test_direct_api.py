"""
Test direct API call to Azure Document Intelligence
"""

import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
import base64

load_dotenv()

endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

# Remove trailing slash
if endpoint.endswith("/"):
    endpoint = endpoint.rstrip("/")

print(f"Endpoint: {endpoint}")
print(f"Key: {key[:10]}...{key[-5:]}")

# Create a simple test document (small PDF-like bytes)
test_content = b"%PDF-1.4\n1 0 obj\n<</Type /Catalog>>\nendobj\nxref\n0 1\n0000000000 65535 f\ntrailer\n<</Size 1 /Root 1 0 R>>\nstartxref\n0\n%%EOF"

print(f"\nTest content size: {len(test_content)} bytes")

try:
    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    print("✅ Client created successfully")
    
    base64_source = base64.b64encode(test_content)
    print(f"✅ Base64 encoded: {len(base64_source)} bytes")
    
    print("\nAttempting to analyze document with 'prebuilt-read' model...")
    poller = client.begin_analyze_document(
        "prebuilt-read",
        analyze_request=AnalyzeDocumentRequest(base64_source=base64_source)
    )
    print("✅ Request sent successfully")
    
    result = poller.result()
    print("✅ Analysis completed!")
    print(f"Result: {result}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}")
    print(f"Message: {str(e)}")
    
    # Try to get more details
    if hasattr(e, 'error'):
        print(f"Error details: {e.error}")
