

# Mini-IronRipper


![Logo](utils/logo.png)


Mini-IronRipper is a Python application for extracting text and metadata from PDFs, Word docs, Excel files, CSVs, images, and emails. It uses OCR for handling scanned documents and images.

## Features

- Extract text from PDFs using pdfminer and OCR 
- Convert Word and PowerPoint docs to PDF for processing
- Extract text, metadata, and sheet data from Excel files
- Read CSV files into Pandas DataFrames
- Perform OCR on images to extract text
- Extract text and metadata from Outlook MSG files
- Multithreading support for faster processing
- Save extracted info to CSV and text files

## Usage

Mini-IronRipper can be run as a CLI application:

```
python mini-iron-ripper.py <directory> <question> <threads> 
```

- `<directory>` - Path to the folder containing files for processing 
- `<question>` - Question to ask about the documents
- `<threads>` - Number of threads to use for parallel processing

This will extract text and metadata from supported files in the given folder. The results will be saved to CSV and text files.

The text file contains the extracted text formatted for asking a question to an AI assistant.

## Requirements

- Python 3.6+
- Requirements listed in requirements.txt:
  - pdfminer
  - pytesseract
  - pandas 
  - openpyxl
  - extract_msg
  - pdf2image
  - Pillow

## Docker Container

A Dockerfile is provided to build an image with the required dependencies. 

Build:

```
docker build -t mini-iron-ripper .
```

Run:

```
docker run -it --rm -v $(pwd):/app mini-iron-ripper <args>
```

## Credits

Mini-IronRipper was created by [Josh Yorko](https://github.com/joshyorko) It uses the following open source libraries:

- [pdfminer](https://github.com/euske/pdfminer) for PDF parsing
- [pytesseract](https://github.com/madmaze/pytesseract) for OCR
- [Pandas](https://github.com/pandas-dev/pandas) for data processing
- [OpenPyXL](https://openpyxl.readthedocs.io/en/stable/) for Excel files
- [extract_msg](https://github.com/mattgwwalker/msg-extractor) for Outlook MSG files

