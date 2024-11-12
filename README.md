# Document Extraction from PDF using BERT

This project involves extracting key information from PDF documents related to tenders using a combination of text extraction, regex, and pre-trained BERT models. The extracted data includes tender details, timeline information, financial details, eligibility criteria, technical specifications, and contact information.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Setup Instructions](#setup-instructions)
3. [Running Instructions](#running-instructions)
4. [Model Selection Justification](#model-selection-justification)
5. [Architecture Overview](#architecture-overview)
6. [Sample Outputs](#sample-outputs)

## Project Overview

This project extracts structured and unstructured information from PDF tender documents. The extraction is done through:

- **Text Extraction**: Using `pdfplumber` to extract raw text from the PDF.
- **Regex Matching**: For identifying and capturing specific information such as tender reference numbers, dates, and financial data.
- **Pre-trained Model**: Utilizing a pre-trained BERT model for token classification to process specific language tasks.
- **Structured Data Extraction**: Tables are extracted for structured data handling, like financial information and submission dates.

The data is saved as a JSON file and printed to the console for easy use.

## Setup Instructions

Before running the project, ensure you have the following dependencies installed.

### Dependencies

You need to install the required libraries. Use the following command to install the necessary Python packages.

```bash
pip install -r requirements.txt
```

## requirements.txt

```bash
pdfplumber==0.8.0
transformers==4.11.3
torch==1.10.0
regex==2021.10.23
```
You can also set up your environment using a virtualenv if you prefer.
```bash
# Install virtualenv if not already installed
pip install virtualenv

# Create a virtual environment
virtualenv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
## Running Instructions

1. Prepare the PDF file: Ensure that the PDF file is named document.pdf and is placed in the same directory as the script.
2. Run the script: Execute the script using the following command:

```bash
python main.py
```

This will:
    - Load the pre-trained BERT model for token classification.
    - Extract data from the document.pdf.
    - Save the extracted data into a extracted_data.json file.
    - Print the extracted data to the console.


## Model Selection Justification
For this project, we used the pre-trained BERT model dbmdz/bert-large-cased-finetuned-conll03-english from Hugging Face. This model has been fine-tuned on the CoNLL-03 dataset for Named Entity Recognition (NER), which is effective in identifying entities like organizations, locations, dates, and more, all of which are crucial to extracting information from tenders.

I choose this model because:
    - BERT's Performance: BERT has shown state-of-the-art performance in NLP tasks, including token classification and named entity recognition.
    - Pre-trained and Fine-tuned: The model has been fine-tuned on a specific dataset that helps in recognizing entities in tender documents such as dates, financial terms, etc.
    - Flexibility: It can be easily adapted for further fine-tuning if needed for specialized terms or datasets.


## Architecture Overview
The architecture of this project follows a modular approach for extracting and processing the document:

1. Document Loading: We use pdfplumber to read the PDF file and extract the raw text.
2. Text Cleaning: The extracted text is cleaned using regex to remove excess whitespace and newlines, ensuring a standard format.
3. Model Loading: A pre-trained BERT model is loaded for entity recognition tasks, which will help in extracting specific details like reference numbers, tender titles, dates, and more.
4. Extraction Logic:
    - Text Extraction: Regular expressions are used to match and extract relevant information such as tender number, start date, etc.
    - Table Extraction: PDF tables are parsed and processed to extract structured data like financial information (EMD, tender fee).
    - Contact Information: Email addresses and phone numbers are extracted using regex.
5. Data Compilation: All extracted data is compiled into a dictionary and saved as a JSON file for further use.
6. Output: The extracted data is saved as extracted_data.json and printed on the console for immediate review.

## Flowchart:
1. Load PDF document using pdfplumber.
2. Extract text and tables.
3. Process text with regular expressions for key details (dates, tender numbers, etc.).
4. Use the pre-trained BERT model for recognizing entities in the text.
5. Compile extracted data into a structured format (JSON).
6. Save and print the data.

## Sample Outputs
Below is a sample of the extracted data:

```bash
{
    "tender_info": {
        "reference_number": "EE-Tender-12345",
        "title": "Fabrication of Machine Components"
    },
    "timeline_info": {
        "start_date": "01-01-2024",
        "end_date": "31-12-2024",
        "physical_submission_end_date": "15-11-2024",
        "technical_bid_opening": "01-12-2024"
    },
    "financial_info": {
        "tender_fee": "1000 INR",
        "emd": "50000 INR"
    },
    "eligibility_info": {
        "eligibility": "This is a domestic tender. Only class I contractors are eligible to participate."
    },
    "technical_info": {
        "technical_specifications": "The scope includes the fabrication of steel components for machine assemblies."
    },
    "contact_info": {
        "emails": ["contact@company.com"],
        "phone_numbers": ["123-456-7890"]
    }
}
```

## Conclusion
This project demonstrates an efficient way to extract structured and unstructured data from PDF tender documents using a combination of pre-trained machine learning models and text extraction techniques. The approach is modular, and you can easily adapt it to process other types of documents with similar structures.
