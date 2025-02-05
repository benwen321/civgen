import PyPDF2
import re
import json
import os

# Define regex pattern
# This pattern requires that the header part consists of "§", a space,
# then a number (with optional decimal), a hyphen, and one or more occurrences of digits followed by a period.
pattern = r'(§\s\d+(?:\.\d+)?-(?:\d+\.)+)([\s\S]*?)(?=§\s\d+(?:\.\d+)?-(?:\d+\.)+|Chapter\s+\S+\.|$)'

# Function to extract text from a PDF using PyPDF2
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"  # Extract text and preserve newlines
    return text

# Function to process one PDF and return extracted sections
def process_pdf(pdf_path):
    pdf_text = extract_text_from_pdf(pdf_path)
    matches = re.findall(pattern, pdf_text, re.DOTALL)
    # Create a list of dictionaries for each matched section,
    # and include the source filename (without path) in the output.
    sections = [
        {
            "pdf": os.path.basename(pdf_path),
            "section": header.replace("§", "").strip(),
            "content": content.strip()
        }
        for header, content in matches
    ]
    return sections

# List of PDF files to process
pdf_files = [ "46.2.1.pdf", "46.2.2.pdf", "46.2.3.pdf", "46.2.6.pdf", "46.2.7.pdf"]

all_sections = []
for pdf_file in pdf_files:
    sections = process_pdf(pdf_file)
    all_sections.extend(sections)

# Save combined sections to a single JSON file
with open("sections.json", "w") as file:
    json.dump(all_sections, file, indent=2)

# Print the JSON output
print(json.dumps(all_sections, indent=2))
