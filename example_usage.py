"""
Example usage of the Document OCR functionality
This script demonstrates how to use the OCR and CrewAI processing programmatically
"""

import os
import json
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
import base64
from crewai_processor import process_with_crewai
from config import AZURE_DI_MODEL

# Load environment variables
load_dotenv()

def process_document_file(file_path):
    """
    Process a document file and extract text using Azure Document Intelligence
    
    Args:
        file_path: Path to the document file (PDF, PNG, JPG, JPEG)
    
    Returns:
        dict: Extracted document data
    """
    # Initialize client
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    
    if not endpoint or not key:
        raise ValueError("Azure credentials not found. Please set them in .env file")
    
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )
    
    # Read the file
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    # Convert to base64
    base64_source = base64.b64encode(file_content).decode("utf-8")
    
    # Start analysis
    print(f"Processing document: {file_path}")
    poller = document_intelligence_client.begin_analyze_document(
        AZURE_DI_MODEL,
        analyze_request=AnalyzeDocumentRequest(base64_source=base64_source)
    )
    result = poller.result()
    
    # Extract content
    full_content = result.content if hasattr(result, 'content') else ""
    
    print(f"✓ Document processed successfully")
    print(f"  Pages: {len(result.pages)}")
    print(f"  Characters extracted: {len(full_content)}")
    
    # Prepare result
    ocr_result = {
        "status": "success",
        "full_content": full_content,
        "pages": len(result.pages),
        "document_type": os.path.splitext(file_path)[1].upper()
    }
    
    return ocr_result

def main():
    # Example usage
    print("=== Document OCR Example ===\n")
    
    # Check if example file exists
    example_file = "example_document.pdf"  # Replace with your file
    
    if not os.path.exists(example_file):
        print(f"⚠️  Example file '{example_file}' not found.")
        print("Please provide a path to your document:")
        file_path = input("> ")
        if not os.path.exists(file_path):
            print("❌ File not found!")
            return
    else:
        file_path = example_file
    
    # Process the document with OCR
    ocr_result = process_document_file(file_path)
    
    # Save OCR results
    output_file = f"{os.path.splitext(file_path)[0]}_ocr_results.json"
    with open(output_file, "w") as f:
        json.dump(ocr_result, f, indent=2)
    print(f"\n✓ OCR results saved to: {output_file}")
    
    # Ask if user wants to process with CrewAI
    print("\nWould you like to process this document with CrewAI? (y/n)")
    choice = input("> ").lower()
    
    if choice == 'y':
        print("\n🤖 Processing with CrewAI...")
        crew_result = process_with_crewai(ocr_result)
        
        if crew_result["status"] == "success":
            print("\n✓ CrewAI processing completed!\n")
            print("=== Analysis Results ===")
            print(crew_result["result"])
            
            # Save CrewAI results
            crew_output_file = f"{os.path.splitext(file_path)[0]}_crewai_analysis.txt"
            with open(crew_output_file, "w") as f:
                f.write(str(crew_result["result"]))
            print(f"\n✓ Analysis saved to: {crew_output_file}")
        else:
            print(f"\n❌ CrewAI processing failed: {crew_result.get('message', 'Unknown error')}")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main()
