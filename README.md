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
