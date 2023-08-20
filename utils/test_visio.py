from vsdx import VisioFile

# Load the Visio file
with VisioFile('Tesseract OCR Design.vsdx') as vis:
    # Initialize an empty string to hold all the text
    all_text = ''

    # Iterate over all the pages in the Visio file
    for page in vis.pages:
        # Iterate over all the shapes in the page
        for shape in page.child_shapes:
            # Append the shape's text to the all_text string
            all_text += shape.text + ' '

# Now all_text contains all the text from the Visio file
print(all_text)
