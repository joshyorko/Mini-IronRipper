from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
import os

# Define the directory
dir_path = "sample_pdfs"
os.makedirs(dir_path, exist_ok=True)

# Define the font size and the font
fontsize = 16
font = ImageFont.load_default()

# Create 50 PDFs
for i in range(1, 51):
    img = Image.new('RGB', (400, 400), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    if i <= 45:
        d.text((10,10), f"This is sample text for file number {i}", font=font, fill=(255, 255, 0))
    else:
        d.text((10,10), f"This is sample text for file number {i}, related to Joshua.", font=font, fill=(255, 255, 0))
    img.save(f"{dir_path}/file_{i}.png")

    pdf = FPDF()
    pdf.add_page()
    pdf.image(f"{dir_path}/file_{i}.png", x = 10, y = 10, w = 100)
    pdf.output(f"{dir_path}/file_{i}.pdf", "F")
