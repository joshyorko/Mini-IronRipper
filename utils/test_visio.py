from vsdx import VisioFile
import pandas as pd
# Load the Visio file
import os

def get_filepaths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.vsdx'):
                filepath = os.path.join(root, filename)
                file_paths.append(filepath)
    return file_paths

def extract_text(filename):
    with VisioFile(filename) as vis:
        # Initialize an empty string to hold all the text
        all_text = ''

        # Iterate over all the pages in the Visio file
        
        for page in vis.pages:
            # Iterate over all the shapes in the page
            for shape in page.child_shapes:
                # Append the shape's text to the all_text string
                all_text += shape.text + ' '
    # convert all_text to dataframe to write to csv
    df = pd.Series(all_text).to_frame()
    df.to_csv(f'{filename.replace(".vsdx","_visio.csv")}', index=False, sep=',', escapechar='\\')
                

def main():
    
    file_paths = get_filepaths('/home/jyorko/projects/dw-tesseract-ocr')
    print(f'file_paths: {file_paths}')
    for filename in file_paths:
        extract_text(filename)

if __name__ == '__main__':
    main()

# Now all_text contains all the text from the Visio file

