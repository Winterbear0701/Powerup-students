import fitz  # PyMuPDF
import os
import json
import re

def get_chapter_from_filename(filename):
    """Extracts chapter number from filenames like 'eemm101.pdf' -> 'Chapter 1'."""
    match = re.search(r'eemm1(\d{2})\.pdf', filename)
    if match:
        # Converts '01' to 1, '14' to 14, etc.
        return f"Chapter {int(match.group(1))}"
    return "Unknown Chapter"

def process_pdf_to_chunks(pdf_path):
    """
    Processes a single PDF and returns a list of structured chunks.
    """
    doc = fitz.open(pdf_path)
    chunks_with_metadata = []

    filename = os.path.basename(pdf_path)
    chapter = get_chapter_from_filename(filename)

    # Heuristics for textbook style
    HEADING_SIZE_THRESHOLD = 11.5
    SUBHEADING_SIZE_THRESHOLD = 10.5

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)["blocks"]

        for block in blocks:
            if "lines" in block:
                full_block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        full_block_text += span["text"] + " "

                full_block_text = full_block_text.strip()

                if not full_block_text or len(full_block_text) < 20:
                    continue

                first_span = block["lines"][0]["spans"][0]
                font_size = first_span["size"]

                content_type = "paragraph"
                if font_size > HEADING_SIZE_THRESHOLD:
                    content_type = "heading"
                elif font_size > SUBHEADING_SIZE_THRESHOLD:
                    content_type = "subheading"
                elif re.match(r'^\d+\.\s|^\([a-zA-Z]\)\s', full_block_text):
                    content_type = "list_item"

                chunk_data = {
                    "content": full_block_text,
                    "metadata": {
                        "source_file": filename,
                        "page_number": page_num + 1,
                        "subject": "Mathematics",
                        "chapter": chapter,
                        "content_type": content_type
                    }
                }
                chunks_with_metadata.append(chunk_data)

    doc.close()
    return chunks_with_metadata

# --- Main Execution ---
all_math_chunks = []
math_directory = '/content/drive/MyDrive/Fifth_standard_ncert_data/Mathematics/'

print(f"Starting processing for all PDFs in: {math_directory}\n")

# Loop through all files in the directory, sorted to maintain chapter order
for filename in sorted(os.listdir(math_directory)):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(math_directory, filename)
        print(f"Processing {filename}...")
        # Process the PDF and add its chunks to our main list
        chunks = process_pdf_to_chunks(pdf_path)
        all_math_chunks.extend(chunks)
        print(f"  -> Extracted {len(chunks)} chunks.")

print("\n" + "="*50)

# --- OUTPUT REPRESENTATION ---
# Show how the chunks from different chapters are stored
print("\n✅ All PDF processing complete.\n")
print("--- Here is a sample of the extracted chunks, showing correct chapter mapping: ---\n")

# Find a chunk from Chapter 1 and a chunk from a later chapter to demonstrate
sample_output = []
# Try to find a chunk from Chapter 1
for chunk in all_math_chunks:
    if chunk['metadata']['chapter'] == 'Chapter 1':
        sample_output.append(chunk)
        break
# Try to find a chunk that is NOT from Chapter 1
for chunk in all_math_chunks:
    if chunk['metadata']['chapter'] != 'Chapter 1':
        sample_output.append(chunk)
        break

print(json.dumps(sample_output, indent=2))
print(f"\nTotal number of chunks created from all math PDFs: {len(all_math_chunks)}")