# Import necessary libraries for pdf processing, image processing, text extraction, threading, type checking and cli-making
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import pytesseract
import typer
from utils import utils as ut



# Initialize Typer for CLI making
app = typer.Typer()

# Define global path variables
TESSERACT_PATH = '/usr/bin/tesseract'
RESULTS_FILE_NAME = 'output_indexed.csv'
EXTRACTED_TEXT_FILE_NAME = 'extracted_text.txt'

# Configure logging
logging.basicConfig(filename='pdf_processing.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


@app.command()
def main(
    dir_path: str = typer.Option(..., prompt="The path to the directory containing the files to be processed."),
    question: str = typer.Option('test', prompt="The question to ask."),
    thread_count: int = typer.Option(3, prompt="The number of threads to use."),
):

    # Get all file paths
    file_paths = ut.get_files(dir_path)
    # Set the path for Tesseract
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
    df_data = []
    # Use multithreading to process files
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = [executor.submit(ut.process_file, file_path)
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

    return ut.write_extracted_text_to_file(EXTRACTED_TEXT_FILE_NAME, extracted_text)

if __name__ == "__main__":
    app()
