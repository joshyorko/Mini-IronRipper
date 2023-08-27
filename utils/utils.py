# Import necessary libraries for pdf processing, image processing, text extraction, threading, type checking and cli-making
import logging

from io import StringIO
from typing import Dict, List, Tuple

import pandas as pd
import pytesseract
from extract_msg import Message  # Library to handle .msg files
from openpyxl import load_workbook
from pdf2image import convert_from_path
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pypdf import PdfReader

import subprocess
from PIL import Image

import os
from concurrent.futures import ThreadPoolExecutor


import os
from PIL import Image


def convert_image_to_pdf(image_file):
    """
    Converts an image file to a PDF file.

    Args:
        image_file (str): The path to the image file.

    Returns:
        None
    """
    if (
        image_file.endswith(".png")
        or image_file.endswith(".jpg")
        or image_file.endswith(".jpeg")
    ):
        pdf_file = f"{os.path.splitext(image_file)[0]}.pdf"

        if not os.path.exists(pdf_file):  # Skip conversion if the pdf already exists
            image = Image.open(image_file)
            rgb_image = image.convert("RGB")
            rgb_image.save(pdf_file)
            print(f"Converted {image_file} to {pdf_file}")
        else:
            print(f"{pdf_file} already exists")


import os
import subprocess


def convert_doc_to_pdf(doc_file):
    """
    Converts a given document file to PDF format using LibreOffice.

    Args:
        doc_file (str): The path to the document file to be converted.

    Returns:
        None
    """
    pdf_file = f"{os.path.splitext(doc_file)[0]}.pdf"
    subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            doc_file,
            "--outdir",
            os.path.dirname(doc_file),
        ]
    )
    return


from openpyxl import load_workbook


def get_excel_metadata(filepath):
    """
    Extracts metadata from an Excel file.

    Args:
        filepath (str): The path to the Excel file.

    Returns:
        dict: A dictionary containing the metadata extracted from the Excel file.
    """
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
        "keywords": props.keywords,
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
    """
    Extracts metadata from a PDF file using PyPDF2.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        dict: A dictionary containing the metadata extracted from the PDF file.
    """
    try:
        # Use PyPDF2 to extract metadata
        with open(pdf_path, "rb") as f:
            pdf = PdfReader(f)
            info = pdf.metadata
            pdf = PdfReader(pdf_path)
            logging.info(f"Extracted Metadata from PDF: {pdf_path}")
    except Exception as e:
        logging.error(f"Failed to extract metadata from {pdf_path}: {e}")
        info = {}
    return info


# Function to preprocess images by converting to grayscale


def preprocess_image(image):
    """
    Converts the input image to grayscale.

    Args:
        image (PIL.Image): The input image.

    Returns:
        PIL.Image: The grayscale image.
    """
    return image.convert("L")


def pdfminer_to_text(pdf_path):
    """
    Extracts text from a PDF file using the pdfminer library.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF file.
    """
    output_string = StringIO()
    with open(pdf_path, "rb") as f:
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


def ocr_to_text(pdf_path, inner_thread_count=2):
    """
    Extracts text from a PDF file using OCR (Optical Character Recognition).

    Args:
        pdf_path (str): The path to the PDF file.
        inner_thread_count (int, optional): The number of threads to use for processing each image. Defaults to 2.

    Returns:
        str: The extracted text from the PDF file.
    """
    text = ""
    try:
        # Convert each page in the PDF to an image
        images = convert_from_path(pdf_path, dpi=300)

        # Function to process a single image
        def process_image(image):
            image = preprocess_image(image)
            return pytesseract.image_to_string(image, lang="eng")

        # Use a ThreadPoolExecutor for inner parallelism
        with ThreadPoolExecutor(max_workers=inner_thread_count) as executor:
            text_parts = list(executor.map(process_image, images))
            text = "".join(text_parts)

    except Exception as e:
        logging.error(f"Failed to extract text from images in {pdf_path}: {e}")
    return text


def ocr_from_image(image):
    """
    Performs OCR (Optical Character Recognition) on the given image and returns the recognized text.

    Args:
        image: The image to perform OCR on.

    Returns:
        The recognized text from the image.
    """
    processed_image = preprocess_image(image)
    return pytesseract.image_to_string(processed_image, lang="eng")


# Function to combine pdfminer and OCR to extract text from a PDF


def pdf_to_text(pdf_path):
    """
    Extracts text from a PDF file using pdfminer and OCR.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF file.
    """
    # Extract text using pdfminer
    text = pdfminer_to_text(pdf_path)
    # Extract text from images using OCR
    text += ocr_to_text(pdf_path)
    logging.info(f"Extracted Text from PDF: {pdf_path}")
    return text


# Function to extract metadata and text from an```python
# email MSG file


def process_msg(msg_path):
    """
    Extracts metadata and text from a MSG file.

    Args:
        msg_path (str): The path to the MSG file.

    Returns:
        tuple: A tuple containing the extracted metadata and text.
    """
    # Create a Message object
    msg = Message(msg_path)
    # Extract metadata from the MSG file
    info = msg.header
    # Extract text from the MSG file
    text = msg.body
    return info, text


def process_file(file_path: str) -> Tuple[Dict, str, str]:
    """
    This function takes a file path as input and processes the file based on its extension.
    Supported file types are PDF, Word documents, Powerpoint documents, MSG files, images, Excel files and CSV files.
    For PDF, Word documents, Powerpoint documents and MSG files, the function extracts text from the file.
    For images, the function uses OCR to extract text from the image.
    For Excel and CSV files, the function reads the file into a pandas DataFrame and converts it to a string.
    The function returns a tuple containing the metadata of the file, the extracted text and the file path.

    Args:
    - file_path (str): The path of the file to be processed.

    Returns:
    - Tuple[Dict, str, str]: A tuple containing the metadata of the file, the extracted text and the file path.
    """
    if file_path.endswith(".pdf"):
        # If the file is a PDF, process it directly
        info, text = process_pdf(file_path)
    elif file_path.endswith(".docx"):
        # If the file is a Word document, convert it to PDF and then process it
        logging.info(f"Word Doc Detected...Converting to PDF.... {file_path}")
        convert_doc_to_pdf(file_path)
        pdf_file_path = file_path.replace(".docx", ".pdf")
        info, text = process_pdf(pdf_file_path)
    elif file_path.endswith(".pptx"):
        logging.info(f"Powerpoint Doc Detected...Converting to PDF.... {file_path}")
        convert_doc_to_pdf(file_path)
        pdf_file_path = file_path.replace(".pptx", ".pdf")
        info, text = process_pdf(pdf_file_path)
    elif file_path.endswith(".msg"):
        # If the file is an MSG file, process it directly
        logging.info(f"MSG File Detected...Extracting Text.... {file_path}")
        info, text = process_msg(file_path)
    elif file_path.endswith((".png", ".jpeg", ".jpg")):
        logging.info(f"Image File Detected...Extracting Text.... {file_path}")
        image = Image.open(file_path)
        info = {}  # Set the metadata to an empty dictionary for images
        text = ocr_from_image(image)  # Call your OCR function here
    elif file_path.endswith((".xlsx", ".csv")):
        # If the file is an Excel or CSV file, read it into a pandas DataFrame and convert it to a string
        logging.info(f"Excel/CSV File Detected...Extracting Data.... {file_path}")
        if file_path.endswith(".xlsx"):
            # If the file is an Excel file, extract its metadata
            info = get_excel_metadata(file_path)
            sheets_data = read_excel_sheets(file_path)

        else:
            # For CSV files, we can directly read the file into a pandas DataFrame
            # and set the metadata to an empty dictionary.
            info = {}
            sheets_data = {"sheet1": pd.read_csv(file_path)}

        text = ""
        for sheet_name, sheet_df in sheets_data.items():
            text += f"\n----- New Table: {sheet_name} -----\n"
            # Convert the DataFrame to a dictionary and then to a string
            text += str(sheet_df.to_dict()) + "\n"
    else:
        logging.warning(f"Unsupported file type: {file_path}")
        raise Exception(f"Unsupported file type: {file_path}")
    return info, text.strip(), file_path


def process_pdf(pdf_path):
    """
    Extracts metadata and text from a given PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        tuple: A tuple containing the extracted metadata and text.
    """
    # Extract metadata from the PDF
    info = get_info(pdf_path)
    # Extract text from the PDF
    text = pdf_to_text(pdf_path)
    logging.info(f"Extracted Text from PDF: {pdf_path}")
    return info, text

def get_files(path: str) -> List[str]:
    """
    Given a path, returns a list of files that end with the following extensions:
    .pdf, .docx, .txt, .xlsx, .csv, .msg

    Args:
    path (str): The path to search for files.

    Returns:
    List[str]: A list of file paths that end with the specified extensions.

    Raises:
    ValueError: If the input path is not a file or directory.
    """
    if os.path.isfile(path):
        return [path]
    elif os.path.isdir(path):
        return [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.endswith((".pdf", ".docx", ".txt", ".xlsx", ".csv", ".msg"))
        ]
    else:
        raise ValueError("Input path is not a file or directory.")




def write_extracted_text_to_file(EXTRACTED_TEXT_FILE_NAME, extracted_text):
    """
    Write extracted text to a file.

    Args:
    - EXTRACTED_TEXT_FILE_NAME (str): The name of the file to write the extracted text to.
    - extracted_text (list): A list of strings, where each string represents the extracted text of a document.

    Returns:
    - None
    """
    with open(EXTRACTED_TEXT_FILE_NAME, "w") as f:
        # Write each document's text to the output file
        for idx, item in enumerate(extracted_text):
            # Write the text of the document
            f.write("%s\n" % item)


def write_extracted_text_to_file_anthropic(
    EXTRACTED_TEXT_FILE_NAME, df, intro_text, extracted_text, outro_text
):
    """
    Write extracted text to a file in a specific format.

    Args:
    - EXTRACTED_TEXT_FILE_NAME (str): The name of the output file.
    - df (pandas.DataFrame): A DataFrame containing information about the extracted text.
    - intro_text (str): The text to be written at the beginning of the output file.
    - extracted_text (list): A list of strings, where each string is the extracted text from a document.
    - outro_text (str): The text to be written at the end of the output file.
    """
    with open(EXTRACTED_TEXT_FILE_NAME, "w") as f:
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
