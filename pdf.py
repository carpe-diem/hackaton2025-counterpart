from pypdf import PdfReader

pdf_path = "./data/prd.pdf"

reader = PdfReader(pdf_path)
text = "\n".join([page.extract_text() or "" for page in reader.pages])
