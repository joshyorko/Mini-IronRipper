from PIL import Image
import os

def convert_image_to_pdf(image_file):
    if image_file.endswith(".png") or image_file.endswith(".jpg") or image_file.endswith(".jpeg"):
        pdf_file = f"{os.path.splitext(image_file)[0]}.pdf"

        if not os.path.exists(pdf_file):  # Skip conversion if the pdf already exists
            image = Image.open(image_file)
            rgb_image = image.convert('RGB')
            rgb_image.save(pdf_file)
            print(f"Converted {image_file} to {pdf_file}")
        else:
            print(f"{pdf_file} already exists")

# Specify the image file you want to convert
image_file = "Picture1.png"

convert_image_to_pdf(image_file)
