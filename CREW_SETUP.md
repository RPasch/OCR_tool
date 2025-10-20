# CrewAI Setup for UAE Digital Bank SME Onboarding

## Overview
The CrewAI crew is specifically designed for the **Maker/Checker step** of SME customer onboarding at a digital bank in the UAE. Three specialized agents work sequentially to classify, extract, and assess customer documents.

## The Three Agents

### Agent 1: Document Classifier & Validator
**Role**: Document Classifier & Validator  
**Expertise**: SME customer onboarding for digital banking in UAE

**Responsibilities**:
- Identify the document type (Trade License, Passport, Bank Statement, Invoice, Contract, etc.)
- Determine the document's purpose in the onboarding context
- Assess relevance for UAE digital bank SME onboarding
- Identify critical information that must be extracted
- Identify discardable information
- Map document to UAE regulatory requirements
- Assess document quality and completeness

**Output**: Detailed classification report with document type, purpose, relevance assessment, and compliance alignment

---

### Agent 2: Structured Data Extractor
**Role**: Structured Data Extractor  
**Expertise**: Financial and business document parsing

**Responsibilities**:
- Extract all critical information identified by the classifier
- Format data into a structured, machine-readable dictionary
- Organize information into standardized categories:
  - Document Metadata
  - Entity Information
  - Contact Information
  - Financial Information
  - Compliance Information
  - Document Quality Indicators
  - Extracted Data Quality Metrics

**Output**: Valid JSON dictionary with all extracted structured data

**Categories Extracted**:
```json
{
  "document_metadata": {
    "document_type": "string",
    "document_date": "string",
    "document_id": "string",
    "pages_count": "number",
    "extraction_confidence": "number"
  },
  "entity_information": {
    "company_name": "string",
    "registration_number": "string",
    "trade_license_number": "string",
    "tax_id": "string",
    "business_type": "string",
    "industry_sector": "string"
  },
  "contact_information": {
    "primary_contact_name": "string",
    "email": "string",
    "phone": "string",
    "address": "string",
    "country": "string",
    "emirate": "string"
  },
  "financial_information": {
    "annual_revenue": "number",
    "number_of_employees": "number",
    "bank_account_details": "string",
    "financial_year_end": "string"
  },
  "compliance_information": {
    "beneficial_owners": "array",
    "pep_status": "boolean",
    "sanctions_screening_required": "boolean",
    "aml_kyc_status": "string"
  },
  "document_quality": {
    "is_legible": "boolean",
    "is_complete": "boolean",
    "requires_manual_review": "boolean",
    "quality_issues": "array"
  },
  "extraction_quality": {
    "confidence_score": "number",
    "fields_with_low_confidence": "array",
    "missing_critical_fields": "array"
  }
}
```

---

### Agent 3: Senior Compliance Onboarding Officer
**Role**: Senior Compliance Onboarding Officer  
**Expertise**: UAE banking regulations, AML/CFT, KYC requirements

**Responsibilities**:
- Assess document authenticity and identify red flags
- Evaluate regulatory compliance (UAE Central Bank requirements)
- Conduct risk assessment (Low/Medium/High/Critical)
- Verify beneficial ownership clarity
- Assess business legitimacy
- Provide onboarding recommendation
- Identify action items and follow-ups

**Onboarding Recommendations**:
- **APPROVE**: Proceed with onboarding
- **CONDITIONAL**: Approve with specific conditions
- **REJECT**: Do not proceed (with reasons)
- **ESCALATE**: Requires manual review by compliance team

**Output**: Professional compliance assessment report with risk evaluation and clear recommendation

---

## Workflow

```
Document Upload
       ↓
   OCR Processing
       ↓
   ┌─────────────────────────────────────┐
   │  Agent 1: Classification            │
   │  - Identify document type           │
   │  - Determine critical vs. discard   │
   │  - Map to compliance requirements   │
   └─────────────────────────────────────┘
       ↓
   ┌─────────────────────────────────────┐
   │  Agent 2: Data Extraction           │
   │  - Extract structured data          │
   │  - Create JSON dictionary           │
   │  - Assess extraction quality        │
   └─────────────────────────────────────┘
       ↓
   ┌─────────────────────────────────────┐
   │  Agent 3: Compliance Review         │
   │  - Assess authenticity              │
   │  - Evaluate regulatory compliance   │
   │  - Provide recommendation           │
   └─────────────────────────────────────┘
       ↓
   Frontend Display
   - Classification Report
   - Structured Data (JSON)
   - Compliance Assessment
   - Full Report
```

## Frontend Display

The application displays CrewAI results in four tabs:

1. **📋 Classification Tab**
   - Document type and purpose
   - Relevance assessment
   - Critical vs. discardable information
   - Compliance requirements

2. **📊 Structured Data Tab**
   - Extracted JSON dictionary
   - Organized by category
   - Download button for JSON export
   - Ready for database storage

3. **✅ Compliance Review Tab**
   - Document authenticity assessment
   - Regulatory compliance status
   - Risk evaluation
   - Onboarding recommendation
   - Action items

4. **📄 Full Report Tab**
   - Complete CrewAI output
   - Text area for review
   - Download button for full report

## Usage

1. Upload a document (PDF, PNG, JPG, JPEG)
2. Click "Process Document" for OCR extraction
3. Click "🚀 Process with CrewAI" to run the crew
4. Review results in the tabs
5. Download structured data or full report as needed

## Configuration

Edit `config.py` to customize:
- `AGENT_VERBOSE`: Set to `False` to reduce console output
- `AGENT_ALLOW_DELEGATION`: Set to `True` to allow agents to delegate tasks
- `MAX_CONTENT_LENGTH`: Maximum characters sent to CrewAI
- `SHOW_SAMPLE_WORDS`: Number of sample words to display per page

## Requirements

- OpenAI API key (for LLM)
- Azure Document Intelligence credentials (for OCR)
- Python 3.11+
- All dependencies in `requirements.txt`

## Notes

- The crew uses sequential processing: Classifier → Extractor → Compliance Officer
- Each agent's output informs the next agent's task
- The structured data output is specifically designed for database storage and frontend display
- All outputs are formatted for compliance and audit trail purposes
