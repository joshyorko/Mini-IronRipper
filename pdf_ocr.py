# Import necessary libraries for pdf processing, image processing, text extraction, threading, type checking and cli-making
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from typing import Dict, List, Tuple

import pandas as pd
import pytesseract
import typer
from extract_msg import Message  # Library to handle .msg files
from openpyxl import load_workbook
from pdf2image import convert_from_path
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from PyPDF2 import PdfReader
from sqlalchemy import create_engine

# Custom module to convert word documents to PDF
from utils.convert_word_docs import convert_doc_to_pdf
# Custom module to create database tables
from utils.create_tables import create_table

# Initialize Typer for CLI making
app = typer.Typer()

# Define global path variables
TESSERACT_PATH = '/usr/bin/tesseract'
RESULTS_FILE_NAME = 'output_indexed.csv'
EXTRACTED_TEXT_FILE_NAME = 'extracted_text.txt'

# Configure logging
logging.basicConfig(filename='pdf_processing.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_excel_metadata(filepath):
    # Load the workbook
    workbook = load_workbook(filepath)

    # Access the properties of the workbook
    props = workbook.properties

    # Extract metadata
    metadata = {
        "author": props.creator,
        "last_modified_by": props.lastModifiedBy,
        "created": props.created,
        "modified": props.modified,
        "title": props.title,
        "description": props.description,
        "subject": props.subject,
        "keywords": props.keywords
    }

    return metadata


def read_excel_sheets(filepath):
    """
    This function reads an Excel file and returns a dictionary. Each key-value pair in the dictionary 
    corresponds to a separate sheet in the Excel file, with the key being the sheet name and the value being 
    a pandas DataFrame representing the data in that sheet.

    :param filepath: The path to the Excel file.
    :return: A dictionary containing pandas DataFrame objects, each representing a different sheet in the Excel file.
    """
    # The None parameter will instruct pandas to read all sheets.
    excel_file = pd.read_excel(filepath, sheet_name=None)

    return excel_file

def get_info(pdf_path):
    try:
        # Use PyPDF2 to extract metadata
        pdf = PdfReader(pdf_path)
        info = pdf.metadata
    except Exception as e:
        logging.error(f"Failed to extract metadata from {pdf_path}: {e}")
        info = {}
    return info

# Function to preprocess images by converting to grayscale


def preprocess_image(image):
    return image.convert('L')

# Function to extract text from a PDF using the pdfminer library


def pdfminer_to_text(pdf_path):
    output_string = StringIO()
    with open(pdf_path, 'rb') as f:
        # Create a PDF parser object
        parser = PDFParser(f)
        # Create a PDF document object that stores the document structure
        doc = PDFDocument(parser)
        # Create a PDF resource manager object that stores shared resources
        rsrcmgr = PDFResourceManager()
        # Create a converter object
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        # Create an interpreter object
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # Process each page contained in the document
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return output_string.getvalue()

# Function to extract text from images in a PDF using OCR


def ocr_to_text(pdf_path):
    text = ""
    try:
        # Convert each page in the PDF to an image
        images = convert_from_path(pdf_path, dpi=400)
        for i in range(len(images)):
            # Preprocess each image
            image = preprocess_image(images[i])
            # Use Tesseract to perform OCR on the image
            text += pytesseract.image_to_string(image, lang='eng')
    except Exception as e:
        logging.error(f"Failed to extract text from images in {pdf_path}: {e}")
    return text

# Function to combine pdfminer and OCR to extract text from a PDF


def pdf_to_text(pdf_path):
    # Extract text using pdfminer
    text = pdfminer_to_text(pdf_path)
    # Extract text from images using OCR
    text += ocr_to_text(pdf_path)
    return text

# Function to extract metadata and text from an```python
# email MSG file


def process_msg(msg_path):
    # Create a Message object
    msg = Message(msg_path)
    # Extract metadata from the MSG file
    info = msg.header
    # Extract text from the MSG file
    text = msg.body
    return info, text

# Function to process a file (PDF, DOCX or MSG) and return metadata, extracted text and file path


def process_file(file_path: str) -> Tuple[Dict, str, str]:
    if file_path.endswith('.pdf'):
        # If the file is a PDF, process it directly
        info, text = process_pdf(file_path)
    elif file_path.endswith('.docx'):
        # If the file is a Word document, convert it to PDF and then process it
        logging.info(f'Word Doc Detected...Converting to PDF.... {file_path}')
        convert_doc_to_pdf(file_path)
        pdf_file_path = file_path.replace('.docx', '.pdf')
        info, text = process_pdf(pdf_file_path)
    elif file_path.endswith('.msg'):
        # If the file is an MSG file, process it directly
        logging.info(f'MSG File Detected...Extracting Text.... {file_path}')
        info, text = process_msg(file_path)
    elif file_path.endswith(('.xlsx', '.csv')):
        # If the file is an Excel or CSV file, read it into a pandas DataFrame and convert it to a string
        logging.info(f'Excel/CSV File Detected...Extracting Data.... {file_path}')
        if file_path.endswith('.xlsx'):
            # If the file is an Excel file, extract its metadata
            info = get_excel_metadata(file_path)
            sheets_data = read_excel_sheets(file_path)
        else:
            # For CSV files, we can directly read the file into a pandas DataFrame
            # and set the metadata to an empty dictionary.
            info = {}  
            sheets_data = {'sheet1': pd.read_csv(file_path)}

        text = ''
        for sheet_name, sheet_df in sheets_data.items():
            text += f'\n----- New Table: {sheet_name} -----\n'
            # Convert the DataFrame to a dictionary and then to a string
            text += str(sheet_df.to_dict()) + '\n'
    else:
        logging.warning(f"Unsupported file type: {file_path}")
        raise Exception(f"Unsupported file type: {file_path}")
    return info, text.strip(), file_path




# Wrapper function to call pdf_to_text() and get_info() for a PDF file


def process_pdf(pdf_path):
    # Extract metadata from the PDF
    info = get_info(pdf_path)
    # Extract text from the PDF
    text = pdf_to_text(pdf_path)
    return info, text

# Function to get all PDF, DOCX, TXT, XLSX, CSV and MSG files in a directory


def get_files(dir_path: str) -> List[str]:
    return [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith((".pdf", ".docx", ".txt", ".xlsx", ".csv", ".msg"))]

# The main function to process files, store results and answer questions


@app.command()
def main(
    dir_path: str = typer.Option(..., prompt="The path to the directory containing the files to be processed."),
    question: str = typer.Option(..., prompt="The question to ask."),
    thread_count: int = typer.Option(5, prompt="The number of threads to use."),
):
    # Create database table
    create_table()
    # Create a database engine
    engine = create_engine('sqlite:///pdf_data.db')
    # Get all file paths
    file_paths = get_files(dir_path)
    # Set the path for Tesseract
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    df_data = []
    # Use multithreading to process files
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(process_file, file_path)
                   for file_path in file_paths]
        for future in futures:
            try:
                result = future.result()
                df_dict = {
                    'file_name': os.path.basename(result[2]),
                    'Metadata': result[0],
                    'extracted_text': result[1]
                }
                df = pd.json_normalize(df_dict)
                df_data.append(df)
            except Exception as e:
                logging.error(f"Error processing file: {e}")
    df = pd.concat(df_data)
    df.columns = df.columns.str.replace('Metadata.', '').str.replace('/', '')
    df['extracted_text'] = df['extracted_text'].str.replace('\n', ' ')
    # Get the directory name and use it as the output CSV file name
    results_file_name = os.path.basename(os.path.normpath(dir_path)) + '.csv'
    # Save results to a CSV file
    df.to_csv(results_file_name, index=False, sep=',', escapechar='\\')
    # Extract all text and prepare the data for further processing
    extracted_text = df['extracted_text'].to_list()
    # Define the introductory text
    intro_text = "Human: I'm going to give you several documents. Then I'm going to ask you a question about it. I'd like you to answer the question using facts from the documents. Here are the documents: \n"
    # Define the text that introduces the question
    outro_text = f"First Question: {question} \nAssistant:"

    # Reset index of the dataframe for easier manipulation
    df = df.reset_index(drop=True)
    with open(EXTRACTED_TEXT_FILE_NAME, 'w') as f:
        # Write the introductory text to the output file
        f.write(intro_text + "\n")
        # Write each document's text to the output file
        for idx, item in enumerate(extracted_text):
            # Write the start tag for a document
            f.write(f"\n<document {df['file_name'][idx]}>\n")
            # Write the text of the document
            f.write("%s\n" % item)
            # Write the end tag for a document
            f.write(f"\n</document {df['file_name'][idx]}>\n")
        # Write the text that introduces the question to the output file
        f.write(outro_text)

# If the script is run directly (not imported), execute the main function
if __name__ == "__main__":
    app()
