"""
Configuration file for the Document OCR application
Customize these settings to match your needs
"""

# Azure Document Intelligence Settings
# Using azure-ai-formrecognizer SDK (stable version)

# CrewAI Agent Settings
AGENT_VERBOSE = True  # Set to False to reduce console output
AGENT_ALLOW_DELEGATION = False  # Set to True to allow agents to delegate tasks

# Document Processing Settings
MAX_CONTENT_LENGTH = 2000  # Maximum characters to send to CrewAI (to avoid token limits)
SHOW_SAMPLE_WORDS = 5  # Number of sample words to show per page

# UI Settings
PAGE_TITLE = "Document OCR with Azure AI"
PAGE_ICON = "📄"

# Agent Configurations
DOCUMENT_ANALYZER_CONFIG = {
    "role": "Document Analyzer",
    "goal": "Analyze and understand the content of the document",
    "backstory": "You are an expert in document analysis with years of experience in extracting meaningful information from various types of documents."
}

DATA_EXTRACTOR_CONFIG = {
    "role": "Data Extractor",
    "goal": "Extract structured data and key information from the document",
    "backstory": "You specialize in identifying and extracting key data points, entities, and relationships from documents."
}
