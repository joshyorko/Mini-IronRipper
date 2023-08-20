import os
import subprocess

def convert_doc_to_pdf(doc_file):
    pdf_file = f"{os.path.splitext(doc_file)[0]}.pdf"
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", doc_file, "--outdir", os.path.dirname(doc_file)])

