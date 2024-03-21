#!/bin/bash

# Create a new directory to save compressed PDFs
mkdir compressed_pdfs

# Loop through all PDF files in the current directory
for file in *.pdf; do
    # Check if the file is a regular file
    if [ -f "$file" ]; then
        # Compress the PDF file and save it to the new directory
        gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook -dNOPAUSE -dBATCH -dQUIET -sOutputFile="compressed_pdfs/$file" "$file"
    fi
done

