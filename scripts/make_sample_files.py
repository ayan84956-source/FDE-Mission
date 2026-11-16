import fitz
import docx
from config import settings

source = settings.SAMPLE_DATA / "rahul_mehta.txt"
text = source.read_text(encoding="utf-8")
pdf = fitz.open()
page = pdf.new_page()
page.insert_textbox(fitz.Rect(50, 50, 550, 800), text, fontsize = 10)
pdf.save(settings.SAMPLE_DATA / "rahul_mehta.pdf")
pdf.close()
document = docx.Document()
for line in text.splitlines():
    document.add_paragraph(line)
print("Created rahul_mehta.pdf and rahul_mehta.docx")