import easyocr
from pdf2image import convert_from_path
from PIL import Image
from fpdf import FPDF
import numpy as np
import re
import os
import glob
from pathlib import Path

def process_pdf_to_searchable(input_pdf_path, output_pdf_path, reader):
    """
    Process a single PDF file to make it searchable using OCR
    """
    try:
        print(f"Processing: {input_pdf_path}")
        
        # Convert PDF to images
        pages = convert_from_path(input_pdf_path, 300)
        
        # Create new PDF
        pdf = FPDF()
        
        for i, page in enumerate(pages):
            print(f"  Processing page {i+1}/{len(pages)}")
            
            # Convert PIL image to numpy array for EasyOCR
            img_array = np.array(page)
            
            # Extract text using EasyOCR
            results = reader.readtext(img_array)
            
            # Combine all detected text and clean up special characters
            text = '\n'.join([result[1] for result in results])
            
            # Clean up text to remove problematic Unicode characters
            # Replace common problematic characters with ASCII equivalents
            text = text.replace('€', 'EUR')
            text = text.replace('£', 'GBP')
            text = text.replace('$', 'USD')
            text = text.replace('°', ' degrees')
            text = text.replace('±', '+/-')
            text = text.replace('×', 'x')
            text = text.replace('÷', '/')
            
            # Remove any remaining non-ASCII characters
            text = re.sub(r'[^\x00-\x7F]+', ' ', text)
            
            # Clean up extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, text)
        
        # Save the searchable PDF
        pdf.output(output_pdf_path)
        print(f"  ✓ Completed: {output_pdf_path}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {input_pdf_path}: {str(e)}")
        return False

def process_all_pdfs_in_folder(source_folder_path):
    """
    Process all PDF files in the source folder and save searchable versions to pwcba_pdf folder
    """
    # Get the absolute path to the source folder
    source_folder_path = Path(source_folder_path).resolve()
    
    if not source_folder_path.exists():
        print(f"Error: Source folder {source_folder_path} does not exist!")
        return
    
    # Create pwcba_pdf folder if it doesn't exist
    pwcba_pdf_folder = Path("pwcba/pwcba_pdf")
    pwcba_pdf_folder.mkdir(exist_ok=True)
    
    # Find all PDF files in the source folder (excluding already searchable ones)
    pdf_files = [f for f in source_folder_path.glob("*.pdf") 
                 if not f.name.endswith("_searchable.pdf")]
    
    if not pdf_files:
        print(f"No original PDF files found in {source_folder_path}")
        return
    
    print(f"Found {len(pdf_files)} original PDF files to process:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name}")
    
    # Initialize EasyOCR reader once
    print("Initializing EasyOCR reader...")
    reader = easyocr.Reader(['en'])
    print("EasyOCR reader initialized.")
    
    print("\nStarting OCR processing...")
    
    # Process each PDF file
    for pdf_file in pdf_files:
        # Create output filename with "_searchable" suffix in pwcba_pdf folder
        output_filename = pdf_file.stem + "_searchable.pdf"
        output_path = pwcba_pdf_folder / output_filename
        
        # Process the PDF
        success = process_pdf_to_searchable(str(pdf_file), str(output_path), reader)
        
        # If searchable PDF was created successfully, delete the original
        if success and output_path.exists():
            try:
                pdf_file.unlink()
                print(f"  ✓ Deleted original: {pdf_file.name}")
            except Exception as e:
                print(f"  ✗ Error deleting original {pdf_file.name}: {str(e)}")
        else:
            print(f"  ⚠ Warning: Searchable PDF not created for {pdf_file.name}, keeping original")
        
        print()  # Add blank line between files
    
    print("All PDF processing completed!")
    print("Original PDF files have been deleted. Searchable PDFs are in the pwcba_pdf folder.")

if __name__ == "__main__":
    # Process all PDFs from the current directory (excluding pwcba_pdf folder)
    # You can change this to any folder path where your original PDFs are located
    source_folder = "pwcba/pwcba_pdf"  # Current directory
    process_all_pdfs_in_folder(source_folder) 