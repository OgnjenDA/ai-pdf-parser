from pdf2image import convert_from_path
import pytesseract
import os

def pdf_to_images(pdf_path):
    """
    Convert a PDF to a list of images.
    """
    return convert_from_path(pdf_path)

def ocr_image(image):
    """
    Perform OCR on an image and return the extracted text.
    """
    return pytesseract.image_to_string(image)

def main():
    pdf_path = 'test_pdf.pdf'

    # Convert PDF to a list of images
    images = pdf_to_images(pdf_path)

    # Display total number of pages
    print(f"The PDF has {len(images)} pages.")

    # Ask user which page to OCR
    page_num = 4

    # Error handling in case of invalid page number
    if page_num < 1 or page_num > len(images):
        print("Invalid page number.")
        return

    # OCR the selected page
    text = ocr_image(images[page_num - 1])

    # Output the extracted text
    with open(f"page_{page_num}_output.txt", "w") as f:
        f.write(text)

    print(f"Text from page {page_num} has been written to 'page_{page_num}_output.txt'.")

if __name__ == "__main__":
    main()
