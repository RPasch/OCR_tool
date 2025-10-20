import os
import json
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from config import (
    AGENT_VERBOSE,
    AGENT_ALLOW_DELEGATION,
    MAX_CONTENT_LENGTH
)

def create_document_processing_crew(ocr_result):
    """
    Create a CrewAI crew for SME customer onboarding at a digital bank in UAE
    Context: Maker/Checker step of onboarding process
    """
    
    # Initialize LLM with OpenAI API key from environment
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Agent 1: Document Classifier
    document_classifier = Agent(
        role='JSON Builder',
        goal='Transform arbitrary OCR output into a single JSON object whose key_values map contains normalized keys and their best corresponding values.',
        backstory="""Organizations upload many kinds of documents (licenses, permits, IDs, certificates, invoices, forms, letters, etc.). 
        These vary in layout, language, and structure. OCR provides raw text plus (sometimes) hints like detected barcodes/QR codes. 
        We need a robust, schema-agnostic way to turn any OCR output into a clean JSON of key–value pairs that "makes sense" to downstream systems, without requiring a bespoke schema per document type.
                    """,
        verbose=AGENT_VERBOSE,
        allow_delegation=AGENT_ALLOW_DELEGATION,
        llm=llm
    )
    
    
    # Prepare the document content
    document_text = ocr_result.get('text', '')
    full_content = ocr_result.get('full_content', document_text)
    pages_count = len(ocr_result.get('pages', []))
    document_type = ocr_result.get('document_type', 'Unknown')
    # Define tasks for UAE SME onboarding
    
    # Task 1: Document Classification
    classification_task = Task(
        description=f"""
        You are a data extraction and normalization agent. Given OCR output for ANY document (licenses, permits, IDs, invoices, certificates, letters, forms, etc., in any language), return ONE JSON object that flexibly reflects the document's content.

        ### OUTPUT CONTRACT
        - Return EXACTLY ONE JSON object (no markdown, no prose).
        - The JSON must be valid and parseable.
        - The schema is FLEXIBLE and CONTENT-DRIVEN. Include only sections that make sense for the given document.

        ### REQUIRED MINIMUM
        {{
        "data": {{ ... }},          key–value pairs extracted from the document (flat and/or nested)
        }}

        ### EXTRACTION RULES
        - Ignore and remove all arabic text
        - Build `data` first: a clean set of key–value pairs that capture the most important information. 
        - Keys in snake_case, concise, English where inferable (e.g., license_number, company_name, formation_number, address, issue_date, expiry_date, directors, activities, code, authority_name).
        - Use arrays for real multiples (e.g., directors, activities, addresses).
        - Nest only when a clear grouping exists (e.g., address objects with {{line_1, city, country}}; party objects with {{role, name}}).
        - Do NOT invent values. If uncertain, omit the key.
        - If no value under a certain header/key, input NULL but return the key/header.
        - Preserve identifiers exactly (e.g., punctuation in "2202163.01").
        - If both flat and grouped representations are useful, prefer grouped (in `sections` or `entities`) but keep the key facts also summarized in `data` for easy access.
        - Include all detected barcodes/QRs in "barcodes".
    

        ### DISAMBIGUATION HEURISTICS
        1) Proximity to strong label cues > visual prominence > frequency.
        2) If multiple candidates for the same field: choose the clearest, most consistently labeled value.
        3) Resolve duplicates by preferring values repeated across sections or corroborated by multiple cues.

        ### QUALITY GATES (before returning)
        - Output is ONE valid JSON object.
        - No arabic
        - `data` contains the key facts available in the document.
        - No commentary outside JSON.
        
        Document Content:
        {full_content[:MAX_CONTENT_LENGTH]}
        """,
        agent=document_classifier,
        expected_output="A well formatted valid JSON object with the precise key-value pairs extracted from the document"
    )
    
    
    # Create the crew with single agent
    crew = Crew(
        agents=[document_classifier],
        tasks=[classification_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew

def process_with_crewai(ocr_result):
    """
    Process the OCR result with CrewAI
    """
    try:
        print("Creating CrewAI crew...")
        crew = create_document_processing_crew(ocr_result)
        print("Crew created successfully. Starting kickoff...")
        
        result = crew.kickoff()
        
        print("Crew kickoff completed successfully")
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        print(f"Error in process_with_crewai: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "message": str(e)
        }
