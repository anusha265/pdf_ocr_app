import os
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from pdf2image import convert_from_bytes
import pytesseract
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
def upload_pdf(request):
    if request.method == 'POST' and request.FILES['pdf_file']:
        pdf_file = request.FILES['pdf_file']
        pdf_content = pdf_file.read()
        # Perform OCR on the PDF content
        ocr_text = perform_ocr(pdf_content)
        # Create a new PDF with OCR-ed text
        output_filename = f"converted_{pdf_file.name}"
        output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
        # Save the OCR-ed text as a PDF file
        with open(output_path, 'wb') as output_file:  # Change 'w' to 'wb'
            save_ocr_as_pdf(ocr_text, output_file)
        # Serve the converted PDF directly for download
        with open(output_path, 'rb') as output_file:
            response = HttpResponse(output_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{output_filename}"'
            return response
    elif request.method == 'GET':
        return render(request, 'upload.html')
    return HttpResponse(status=405)  # Method Not Allowed for unsupported methods
def perform_ocr(pdf_content):
    # Function to perform OCR on a given PDF content
    print("Converting PDF to images...")
    images = convert_to_images(pdf_content)
    print(f"Number of images converted: {len(images)}")
    ocr_text = ""
    for idx, image in enumerate(images):
        print(f"Processing image {idx + 1}...")
        img = preprocess_image(image)
        text = pytesseract.image_to_string(img, lang='eng')
        ocr_text += text + "\n\n"
    print("OCR process completed.")
    return ocr_text
def convert_to_images(pdf_content):
    # Function to convert PDF content into images
    images = convert_from_bytes(pdf_content, dpi=300)
    return images
def preprocess_image(image):
    # Function to preprocess the image before OCR
    img = image.convert("L")  # Convert to grayscale
    img = img.point(lambda x: 0 if x < 200 else 255, "1")  # Binarization
    return img
def save_ocr_as_pdf(ocr_text, output_file):
    # Function to save the OCR-ed text as a new PDF file
    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    content = [Paragraph(ocr_text, styles['Normal'])]
    doc.build(content)
 