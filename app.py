import os
import json
import tempfile
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature

from PIL import Image
import numpy as np
import io
from crewai_processor import process_with_crewai
from config import PAGE_TITLE, PAGE_ICON, SHOW_SAMPLE_WORDS

# Load environment variables
load_dotenv()

# Initialize Azure Document Intelligence client
endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")

# Ensure endpoint doesn't have trailing slash
if endpoint and endpoint.endswith("/"):
    endpoint = endpoint.rstrip("/")

def format_bounding_box(bounding_box):
    """Format bounding box coordinates"""
    if not bounding_box:
        return "N/A"
    reshaped_bounding_box = np.array(bounding_box).reshape(-1, 2)
    return ", ".join(["[{}, {}]".format(x, y) for x, y in reshaped_bounding_box])

def process_document(file_content, file_extension):
    """Process the uploaded document using Azure Document Intelligence"""
    try:
        # Initialize client
        document_analysis_client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
            api_version="2024-11-30"
        )
        
        # Debug: Log the request
        print(f"Endpoint: {endpoint}")
        print(f"File size: {len(file_content)} bytes")
        
        # Start analysis with file stream
        poller = document_analysis_client.begin_analyze_document(
            model_id="prebuilt-read",
            body=file_content,
            features=[DocumentAnalysisFeature.BARCODES]  # Enable QR/barcode extraction
        )
        result = poller.result()
        
        # Extract full document content
        full_content = result.content if hasattr(result, 'content') else ""
        
        # Extract detailed text content with page information
        extracted_text = ""
        pages_data = []
        
        for page in result.pages:
            page_info = {
                "page_number": page.page_number,
                "width": page.width,
                "height": page.height,
                "unit": page.unit,
                "lines": [],
                "words": []
            }
            
            extracted_text += f"\n--- Page {page.page_number} ---\n"
            
            # Extract lines
            for line in page.lines:
                extracted_text += f"{line.content}\n"
                page_info["lines"].append({
                    "content": line.content,
                    "bounding_box": format_bounding_box(line.polygon)
                })
            
            # Extract words with confidence
            for word in page.words:
                page_info["words"].append({
                    "content": word.content,
                    "confidence": word.confidence
                })
            
            pages_data.append(page_info)
        
        # Extract styles (handwritten detection)
        styles_info = []
        if hasattr(result, 'styles') and result.styles:
            for style in result.styles:
                styles_info.append({
                    "is_handwritten": style.is_handwritten if hasattr(style, 'is_handwritten') else False
                })
        
        # Extract barcodes and QR codes from Azure
        barcodes_info = []
        if hasattr(result, 'barcodes') and result.barcodes:
            for barcode in result.barcodes:
                barcodes_info.append({
                    "type": barcode.kind if hasattr(barcode, 'kind') else "Unknown",
                    "value": barcode.value if hasattr(barcode, 'value') else None,
                    "confidence": barcode.confidence if hasattr(barcode, 'confidence') else None,
                    "bounding_box": format_bounding_box(barcode.polygon) if hasattr(barcode, 'polygon') else None,
                    "source": "azure"
                })
        
        # Extract key-value pairs
        key_value_pairs = []
        if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
            for kv_pair in result.key_value_pairs:
                key_content = kv_pair.key.content if kv_pair.key else None
                value_content = kv_pair.value.content if kv_pair.value else None
                key_value_pairs.append({
                    "key": key_content,
                    "value": value_content,
                    "confidence": kv_pair.confidence if hasattr(kv_pair, 'confidence') else None
                })
        
        return {
            "status": "success",
            "full_content": full_content,
            "text": extracted_text,
            "pages": pages_data,
            "styles": styles_info,
            "barcodes": barcodes_info,
            "key_value_pairs": key_value_pairs,
            "document_type": file_extension.upper(),
            "raw_result": result
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

def save_uploaded_file(uploaded_file):
    """Save uploaded file to a temporary location"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

def main():
    st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout="wide")
    st.title(f"{PAGE_ICON} {PAGE_TITLE}")
    
    # Initialize session state
    if 'ocr_result' not in st.session_state:
        st.session_state.ocr_result = None
    if 'crew_result' not in st.session_state:
        st.session_state.crew_result = None
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = os.getenv('OPENAI_API_KEY', '')
    
    # Sidebar for API configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.subheader("API Keys")
        
        # OpenAI API Key input
        openai_key = st.text_input(
            "OpenAI API Key",
            value="",
            type="password",
            help="Enter your OpenAI API key for CrewAI agents. This is required for AI analysis."
        )
        
        if openai_key:
            st.session_state.openai_api_key = openai_key
            os.environ['OPENAI_API_KEY'] = openai_key
            st.success("✅ OpenAI API Key configured")
        elif st.session_state.openai_api_key:
            os.environ['OPENAI_API_KEY'] = st.session_state.openai_api_key
        
        st.divider()
        st.subheader("Options")
    
    # Top section with toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("### Upload and Process Documents")
    with col2:
        enable_crewai = st.checkbox("🤖 Enable CrewAI Analysis", value=True)
    
    st.divider()
    
    # File upload section
    uploaded_file = st.file_uploader(
        "Upload a document (PDF, PNG, JPG, JPEG)",
        type=["pdf", "png", "jpg", "jpeg"]
    )
    
    if uploaded_file is not None:
        # Display file info
        file_extension = Path(uploaded_file.name).suffix.lower()
        st.write(f"**File uploaded:** {uploaded_file.name}")
        
        # Display the file if it's an image (at half size)
        if file_extension in ['.png', '.jpg', '.jpeg']:
            col1, col2 = st.columns([1, 1])
            with col1:
                # Reset file pointer to beginning to ensure image loads correctly
                uploaded_file.seek(0)
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Process the document when the user clicks the button
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                # Save the uploaded file temporarily
                temp_file_path = save_uploaded_file(uploaded_file)
                
                if temp_file_path:
                    try:
                        # Read the file content
                        with open(temp_file_path, "rb") as f:
                            file_content = f.read()
                        
                        # Process the document
                        result = process_document(file_content, file_extension)
                        
                        # Store in session state
                        st.session_state.ocr_result = result
                        
                        if result["status"] == "success":
                            st.success("✅ OCR Processing Complete!")
                            
                            # If CrewAI is enabled, process automatically
                            if enable_crewai:
                                st.info("🤖 Running CrewAI analysis...")
                                try:
                                    crew_result = process_with_crewai(result)
                                    st.session_state.crew_result = crew_result
                                except Exception as e:
                                    st.error(f"CrewAI processing error: {str(e)}")
                                    st.session_state.crew_result = None
                            
                            # Display document info
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Document Type", result["document_type"])
                            with col2:
                                st.metric("Total Pages", len(result["pages"]))
                            
                            # Display styles/handwriting detection
                            if result["styles"]:
                                has_handwriting = any(s["is_handwritten"] for s in result["styles"])
                                st.info(f"Document contains {'handwritten' if has_handwriting else 'no handwritten'} content")
                            
                            # Display key-value pairs
                            if result.get("key_value_pairs"):
                                st.subheader("🔑 Key-Value Pairs")
                                kv_df_data = []
                                for kv in result["key_value_pairs"]:
                                    kv_df_data.append({
                                        "Key": kv["key"],
                                        "Value": kv["value"],
                                        "Confidence": f"{kv['confidence']:.2%}" if kv['confidence'] else "N/A"
                                    })
                                if kv_df_data:
                                    st.dataframe(kv_df_data, use_container_width=True)
                            
                            # Display barcodes and QR codes
                            if result.get("barcodes"):
                                st.subheader("📊 Barcodes & QR Codes")
                                for barcode in result["barcodes"]:
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.write(f"**Type:** {barcode['type']}")
                                    with col2:
                                        source = barcode.get('source', 'unknown')
                                        st.write(f"**Source:** {source}")
                                    
                                    # Display value or data (depending on source)
                                    if barcode.get('data'):
                                        st.write(f"**Data:** `{barcode['data']}`")
                                    elif barcode.get('value'):
                                        st.write(f"**Value:** `{barcode['value']}`")
                                    
                                    # Display confidence if available
                                    if barcode.get('confidence'):
                                        st.write(f"**Confidence:** {barcode['confidence']:.2%}")
                                    
                                    # Display location if available
                                    if barcode.get('bounding_box'):
                                        st.write(f"**Location:** {barcode['bounding_box']}")
                                    
                                    st.divider()
                            
                            # Display extracted text in dropdown
                            with st.expander("📝 Raw Extracted Text"):
                                st.text_area("", value=result["text"], height=300, key="extracted_text", disabled=True)
                            
                            
                        else:
                            st.error(f"Error processing document: {result.get('message', 'Unknown error')}")
                    
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
                    
                    finally:
                        # Clean up the temporary file
                        try:
                            os.unlink(temp_file_path)
                        except:
                            pass
    
    # Display crew results if they exist in session state
    if st.session_state.crew_result is not None:
        if st.session_state.crew_result.get("status") == "success":
            st.divider()
            st.subheader("🤖 CrewAI Analysis Results")
            
            crew_output = st.session_state.crew_result.get("result", "")
            
            # Try to parse and display as JSON
            try:
                # Extract JSON from the output if it contains markdown code blocks
                if "```json" in str(crew_output):
                    json_str = str(crew_output).split("```json")[1].split("```")[0].strip()
                elif "```" in str(crew_output):
                    json_str = str(crew_output).split("```")[1].split("```")[0].strip()
                else:
                    json_str = str(crew_output)
                
                parsed_json = json.loads(json_str)
                st.json(parsed_json)
            except (json.JSONDecodeError, IndexError):
                # If JSON parsing fails, display as text
                st.code(crew_output, language="json")
        else:
            st.error(f"❌ CrewAI processing failed: {st.session_state.crew_result.get('message', 'Unknown error')}")
            st.info("Make sure you have set the OPENAI_API_KEY in your .env file.")

if __name__ == "__main__":
    if not endpoint or not key:
        st.error("Please set the AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY in the .env file")
    else:
        main()
