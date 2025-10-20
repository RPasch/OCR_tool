# Document OCR with Azure AI and CrewAI

This Streamlit application allows users to upload PDF or image files (PNG, JPG) and extract text using Azure Document Intelligence. The extracted information is then processed by CrewAI agents for analysis, data extraction, and summarization.

## Features

- 📤 **Upload documents**: Support for PDF, PNG, JPG, and JPEG files
- 🔍 **OCR Extraction**: Extract text, words, and metadata using Azure Document Intelligence
- 📊 **Detailed Analysis**: View page-by-page breakdown with confidence scores
- 🤖 **AI Processing**: CrewAI agents analyze, extract insights, and summarize content
- 💾 **Export Results**: Download OCR results as JSON and CrewAI analysis as text
- 🎯 **Handwriting Detection**: Identifies handwritten content in documents

## Prerequisites

- Python 3.8+
- Azure Document Intelligence service (Form Recognizer) - [Get started](https://learn.microsoft.com/azure/ai-services/document-intelligence/)
- Azure subscription (for API access)
- OpenAI API key (for CrewAI processing)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Azure Document Intelligence

1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a **Document Intelligence** resource
3. Copy the **Endpoint** and **Key** from the resource

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_azure_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### 1. Start the Application

**Option A: Using the run script (recommended)**
```bash
./run.sh
```

**Option B: Manual start**
```bash
streamlit run app.py
```

**Option C: Programmatic usage**
```bash
python example_usage.py
```

### 2. Process a Document

1. Open your browser and navigate to http://localhost:8501
2. Upload a document (PDF, PNG, JPG, or JPEG)
3. Click **"Process Document"** to extract text using OCR
4. View extracted text, page details, and confidence scores
5. Download results as JSON if needed

### 3. Analyze with CrewAI

1. After OCR processing, scroll to the **"Process with CrewAI"** section
2. Click **"🚀 Process with CrewAI"** button
3. Wait for the AI agents to complete their analysis
4. View the comprehensive analysis, extracted data, and summary
5. Download the analysis as a text file

## CrewAI Agents

The application uses three specialized AI agents:

- **Document Analyzer**: Analyzes document type, structure, and main topics
- **Data Extractor**: Extracts entities, numbers, dates, and actionable items
- **Content Summarizer**: Creates executive summaries and key points

## Project Structure

```
├── app.py                      # Main Streamlit application
├── crewai_processor.py         # CrewAI agents and tasks
├── config.py                   # Configuration settings
├── example_usage.py            # Example programmatic usage
├── run.sh                      # Quick start script
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create from .env.example)
├── .env.example                # Template for environment variables
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Troubleshooting

### Azure Document Intelligence Errors
- Verify your endpoint and key are correct in `.env`
- Ensure your Azure subscription is active
- Check that your resource region matches the endpoint

### CrewAI Processing Errors
- Verify your OpenAI API key is set in `.env`
- Ensure you have sufficient OpenAI API credits
- Check your internet connection

## License

MIT
