# dw-tesseract-ocr

The `dw-tesseract-ocr` project is a Python-based application that uses both the `pdfminer` library and Optical Character Recognition (OCR) to process documents, extract text, and store the results in a SQLite database. It's primarily designed to handle PDF, MSG, Excel, and CSV files. It can also process Word documents by converting them into PDF format first. Additionally, this application supports the conversion of image files into PDF and extraction of text from those files.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Building the Docker Image](#building-the-docker-image)
- [Running the Docker Container](#running-the-docker-container)
- [Application Scripts](#application-scripts)
- [Project Dependencies](#project-dependencies)
- [Output](#output)
- [Usage](#usage)
- [Dockerfile](#dockerfile)

## Prerequisites

Make sure Docker is installed on your system. If you haven't installed Docker yet, please follow the instructions from the official Docker documentation [here](https://docs.docker.com/get-docker/).

## Installation

1. Clone this repository to your local machine using:

```bash
git clone https://github.com/jyorko/dw-tesseract-ocr.git
cd dw-tesseract-ocr
```

## Building the Docker Image

Navigate to the project root directory and run the following command to build the Docker image:

```bash
docker build -t dw-tesseract-ocr:latest .
```

This command will create a Docker image with the name `dw-tesseract-ocr` and tag it as `latest`.

## Running the Docker Container

Once the image is built, you can create and run a Docker container from it using the following command:

```bash
docker run -it --name ocr_container dw-tesseract-ocr:latest
```

You can then interact with the application inside the container's shell. The application will prompt you to input the directory path containing the documents to be processed, the question you'd like to ask, and the number of threads you'd like to use.

## Application Scripts

The application consists of several Python scripts to perform various tasks. It also uses multithreading to process files and is designed to be run as a CLI application:

- `pdf_ocr.py`: The main application script that performs OCR on the documents.
- `utils/convert_word_docs.py`: A utility script to convert Word documents to PDF format.
- `utils/convert_image_pdf.py`: A utility script to convert image files (in png, jpg, or jpeg format) to PDF format.
- `create_tables.py`: A script to create the SQLite database table where the extracted data will be stored.

Please ensure that you have all these scripts in the appropriate directories as mentioned above to make the application work correctly.

## Project Dependencies

The project is dependent on the following Python libraries:

- `os`
- `pandas`
- `pdf2image`
- `PyPDF2`
- `pytesseract`
- `tqdm`
- `sqlalchemy`
- `pdfminer`
- `PIL` from `Pillow`
- `extract-msg`

These dependencies are listed in the `requirements.txt` file and will be installed when building the Docker image.

## Output

The output will be a SQLite database named `pdf_data.db` containing the data extracted from the documents and a CSV file named based on the directory name. The extracted text from the documents is also written to a text file named `extracted_text.txt`. Additionally, the extracted text from the documents is also written to a text file named `extracted_text.txt`.

## Usage

To use this application:

1. Make sure Docker is installed on your system.
2. Clone this repository.
3. Build the Docker image.
4. Run the Docker container.
5. When prompted, input the directory path containing the documents to be processed and the question you'd like to ask.

Supported document types include `.pdf`, `.doc`, `.docx`, `.msg`, `.xlsx`, `.csv`, and image files in `.png`, `.jpg`, and `.jpeg` formats.

## Dockerfile

The Dockerfile in this repository contains the steps to build the Docker image. It's based on a Python 3 image and includes instructions to:

1. Set the working directory in the container.
2. Copy the project files into the container.
3. Install the required Python packages.
4. Run the application script.

The Dockerfile is crucial in ensuring the application runs smoothly in a Docker container, and it should not be modified unless you're certain of the changes you're making.

For any additional instructions or details, you should refer to the `README.md` file within the GitHub repository, or contact the maintainers or contributors of the project directly.