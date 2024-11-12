#imported all required libraries
import re
import json
import pdfplumber
import logging
from transformers import AutoModelForTokenClassification, AutoTokenizer

# Suppress warnings from the transformers library for clean output
logging.getLogger("transformers").setLevel(logging.ERROR)

# Load the model and tokenizer
def load_model(model_name="dbmdz/bert-large-cased-finetuned-conll03-english"):
    """
    Loads the pre-trained BERT model and tokenizer for token classification.
    Args:
        model_name (str): The name of the pre-trained model.
    Returns:
        model: The pre-trained BERT model for token classification.
        tokenizer: The tokenizer for the BERT model.
    """
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        return model, tokenizer
    except Exception as e:
        logging.error(f"Error loading model {model_name}: {e}")
        raise RuntimeError("Model loading failed")

# Load the document from PDF
def load_document(file_path):
    """
    Extracts text from the given PDF document.
    Args:
        file_path (str): The path to the PDF file.
    Returns:
        document_text (str): The extracted text from the PDF.
    """
    document_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                document_text += page.extract_text() + "\n"
    except Exception as e:
        logging.error(f"Error loading document {file_path}: {e}")
        raise FileNotFoundError(f"Could not open the file: {file_path}")
    return document_text

# Extract tables for structured data handling
def extract_table_data(file_path):
    """
    Extracts structured table data from the PDF.
    Args:
        file_path (str): The path to the PDF file.
    Returns:
        table_data (list): List of tables extracted from the document.
    """
    table_data = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    table_data.append(table)
    except Exception as e:
        logging.error(f"Error extracting table data from {file_path}: {e}")
        raise RuntimeError("Table extraction failed")
    return table_data

# Clean up extracted text to standard format
def clean_text(text):
    """
    Cleans up text by removing excess whitespace and newlines.
    Args:
        text (str): The raw extracted text.
    Returns:
        cleaned_text (str): The cleaned text.
    """
    return re.sub(r'\s+', ' ', text).strip()  # Remove newlines and extra spaces

# Function to extract tender information from the text
def extract_tender_info(text):
    """
    Extracts the tender reference number and title from the document text.
    Args:
        text (str): The raw document text.
    Returns:
        tender_info (dict): Dictionary containing the reference number and title.
    """
    tender_info = {}
    try:
        ref_number = re.search(r"Ref\.?\s?[eE]-?Tender Notice\s?-?\s?([A-Z0-9/]+)", text)
        if ref_number:
            tender_info['reference_number'] = ref_number.group(1)

        title = re.search(r"(?:invites e-tender for|e-tender for|purpose of)\s+(Fabrication of Machine[^.]*?Materials)", text, re.IGNORECASE)
        tender_info['title'] = title.group(1).strip() if title else "Title not found"
    except Exception as e:
        logging.error(f"Error extracting tender info: {e}")
        tender_info = {"reference_number": "Not found", "title": "Not found"}

    return tender_info

# Extracts timeline details (start date, end date, etc.) from the document
def extract_timeline_info(text, table_data):
    """
    Extracts important timeline information such as start date, end date, and technical bid opening.
    Args:
        text (str): The raw document text.
        table_data (list): The table data extracted from the document.
    Returns:
        timeline_info (dict): Dictionary containing the timeline details.
    """
    timeline_info = {}

    try:
        start_date = re.search(r"(?:Start|Commencement)\s?Date[:\-]?\s*(\d{1,2}[\./-]?\d{1,2}[\./-]?\d{4})", text)
        timeline_info['start_date'] = start_date.group(1) if start_date else "Not found"
        
        end_date = re.search(r"(?:End|Completion)\s?Date[:\-]?\s*(\d{1,2}[\./-]?\d{1,2}[\./-]?\d{4})", text)
        timeline_info['end_date'] = end_date.group(1) if end_date else "Not found"
        
        physical_submission_end_date = re.search(r"(?:Physical\s?submission\s?of\s?Tender|Submission)\s?[Ee]nd\s?[Dd]ate[:\-]?\s*(\d{1,2}[\./-]?\d{1,2}[\./-]?\d{4})", text)
        timeline_info['physical_submission_end_date'] = physical_submission_end_date.group(1) if physical_submission_end_date else "Not found"
        
        # Extracting the technical bid opening date from the table data
        for table in table_data:
            for row in table:
                if "Opening of Technical e-Bid" in str(row):
                    for cell in row:
                        if re.match(r"\d{2}.\d{2}.\d{4}", str(cell)):
                            timeline_info['technical_bid_opening'] = cell.strip()
                            break
    except Exception as e:
        logging.error(f"Error extracting timeline info: {e}")
        timeline_info = {
            "start_date": "Not found",
            "end_date": "Not found",
            "physical_submission_end_date": "Not found",
            "technical_bid_opening": "Not found"
        }

    return timeline_info

# Extract financial information (e.g., tender fee and EMD)
def extract_financial_info_from_table(table_data):
    """
    Extracts financial information from the tables, such as tender fee and EMD.
    Args:
        table_data (list): The extracted table data.
    Returns:
        financial_info (dict): Dictionary containing financial details.
    """
    financial_info = {}

    try:
        tender_fee_pattern = r"([0-9,]+(?:\.\d{2})?)\s*(?:INR|₹|Rs|Rupees)?\s*(?:Tender\s*Fee|Fee)?"
        emd_pattern = r"([0-9,]+(?:\.\d{2})?)\s*(?:EMD|Earnest\s*Money\s*Deposit)?"

        for table in table_data:
            for row in table:
                if len(row) >= 5:
                    tender_fee = row[3]
                    emd = row[4]
                    if tender_fee and emd:
                        if "Tender Fee" in tender_fee and "EMD" in emd:
                            continue
                        tender_fee_match = re.search(tender_fee_pattern, tender_fee)
                        if tender_fee_match:
                            financial_info['tender_fee'] = clean_text(tender_fee_match.group(1))
                        emd_match = re.search(emd_pattern, emd)
                        if emd_match:
                            financial_info['emd'] = clean_text(emd_match.group(1))
    except Exception as e:
        logging.error(f"Error extracting financial info: {e}")
        financial_info = {"tender_fee": "Not found", "emd": "Not found"}

    return financial_info

# Extract eligibility criteria
def extract_eligibility_info(text):
    """
    Extracts eligibility criteria from the document.
    Args:
        text (str): The raw document text.
    Returns:
        eligibility_info (dict): Dictionary containing eligibility details.
    """
    eligibility_pattern = (
        r"(This is a domestic Tender.*?Only class ?–? I.*?eligible to participate in tender.*?)"
        r"(?:\n{2,}|Annexure|Read and Accepted|Technical bid)"
    )
    eligibility_info = {}
    try:
        match = re.search(eligibility_pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            eligibility_text = clean_text(match.group(1))
            eligibility_text = re.sub(r"\d+[\.\-]?\s+", "", eligibility_text)
            eligibility_info = {"eligibility": eligibility_text}
        else:
            eligibility_info = {"eligibility": "Eligibility criteria not found"}
    except Exception as e:
        logging.error(f"Error extracting eligibility info: {e}")
        eligibility_info = {"eligibility": "Error extracting eligibility info"}

    return eligibility_info

# Extract technical specifications
def extract_technical_info(text):
    """
    Extracts technical specifications or scope of work from the document.
    Args:
        text (str): The raw document text.
    Returns:
        technical_info (dict): Dictionary containing technical specifications.
    """
    technical_info = {}
    try:
        technical_specifications = re.search(r"(Technical\s?Specifications|Scope\s?of\s?Work|Work\s?Specifications)\s*[:\-]?\s*(.*?)(?:\n|$)", text, re.IGNORECASE)
        technical_info['technical_specifications'] = technical_specifications.group(2).strip() if technical_specifications else "Not found"
    except Exception as e:
        logging.error(f"Error extracting technical info: {e}")
        technical_info = {'technical_specifications': 'Not found'}

    return technical_info

# Extract contact information (emails, phone numbers)
def extract_contact_info(text):
    """
    Extracts contact information such as emails and phone numbers.
    Args:
        text (str): The raw document text.
    Returns:
        contact_info (dict): Dictionary containing emails and phone numbers.
    """
    contact_info = {}
    try:
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        contact_info['emails'] = list(set(re.findall(email_pattern, text)))
        
        phone_pattern = r"\d{3}[-]?\d{3}[-]?\d{4}"
        contact_info['phone_numbers'] = list(set(re.findall(phone_pattern, text)))
    except Exception as e:
        logging.error(f"Error extracting contact info: {e}")
        contact_info = {'emails': [], 'phone_numbers': []}

    return contact_info

# Main function to drive the entire extraction process
def main():
    """
    Main function to extract and save information from a PDF document, printing it in the console and saving it to a file.
    """
    model, tokenizer = load_model("dbmdz/bert-large-cased-finetuned-conll03-english")
    document_text = load_document("document.pdf")
    table_data = extract_table_data("document.pdf")
    
    # Extraction of information from document
    tender_info = extract_tender_info(document_text)
    timeline_info = extract_timeline_info(document_text, table_data)
    financial_info = extract_financial_info_from_table(table_data)
    eligibility_info = extract_eligibility_info(document_text)
    technical_info = extract_technical_info(document_text)
    contact_info = extract_contact_info(document_text)

    # Compiling all extracted information into a dictionary
    extracted_data = {
        "tender_info": tender_info,
        "timeline_info": timeline_info,
        "financial_info": financial_info,
        "eligibility_info": eligibility_info,
        "technical_info": technical_info,
        "contact_info": contact_info
    }
    
    # Save extracted data to JSON file
    try:
        with open("extracted_data.json", "w") as outfile:
            json.dump(extracted_data, outfile, indent=4)
        logging.info("Extracted data saved to extracted_data.json")
    except Exception as e:
        logging.error(f"Error saving extracted data to file: {e}")

    # Print extracted data to console
    print("Extracted Data:")
    print(json.dumps(extracted_data, indent=4))

# Execute main function when the script is run
if __name__ == "__main__":
    main()