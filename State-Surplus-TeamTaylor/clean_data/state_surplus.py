import pandas as pd 
import PyPDF2


def read_pdf(filename):
  pdf_file = open(filename,'rb')
  read_pdf = PyPDF2.PdfFileReader(pdf_file)
  number_of_pages = read_pdf.getNumPages()

  state_agencies = []
  for i in range(number_of_pages):
    page = read_pdf.getPage(i)
    page_content = page.extractText()
    page_content = page_content.split('\n')
    state_agencies.append(page_content)

  return state_agencies


print(read_pdf('../../docs/state_agency_names.pdf'))
