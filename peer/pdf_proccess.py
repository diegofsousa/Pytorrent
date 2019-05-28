import os
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
import textract
import glob

import os
from stat import *
import re

import hashlib

def pdf_splitter(path):
	fname = os.path.splitext(os.path.basename(path))[0]
 
	pdf = PdfFileReader(path)
	for page in range(pdf.getNumPages()):
		pdf_writer = PdfFileWriter()

		#print(extract_text(pdf.getPage(page)))

		pdf_writer.addPage(pdf.getPage(page))
 
		output_filename = '{}_page_{}.pdf'.format(
			fname, page+1)
 
		with open(output_filename, 'wb') as out:
			pdf_writer.write(out)
 
		print('Created: {}'.format(output_filename))


def merger(output_path, input_paths):
	pdf_merger = PdfFileMerger()
	file_handles = []
 
	for path in input_paths:
		pdf_merger.append(path)
 
	with open(output_path, 'wb') as fileobj:
		pdf_merger.write(fileobj)


def info_run_pages(path):
	all_text = ''
	pdf = PdfFileReader(path)
	pages = []
	for page in range(pdf.getNumPages()):
		pdf_writer = PdfFileWriter()

		text = extract_text(pdf.getPage(page))

		num_words = len(re.split('; |, |\*|\n',text))
		all_text += text

		pages.append(num_words)

	return len(pages), pages, hashlib.md5(all_text.encode()) 


def extract_text(page):
	text = page.extractText()

	if text == '' or text.strip() == '':
		temp_file = '.temp.pdf'

		pdf_writer = PdfFileWriter()
		pdf_writer.addPage(page)
 
		with open(temp_file, 'wb') as out:
			pdf_writer.write(out)
		text = textract.process(temp_file, method='tesseract', encoding='utf-8')

	return text


def get_info(path):
	st = os.stat(path)
	name = path.split('/')[-1]
	url = path
	size = st[ST_SIZE]
	num_pages, count_words_by_pages, md5 = info_run_pages(path)

	return {'name':name, 'url':url, 'size':size, 'num_pages':num_pages, 'count_words_by_pages':count_words_by_pages, 'md5': md5.hexdigest()}

# if __name__ == '__main__':
# 	path = '/home/diego/hd/Documentos/Sistemas de Informação/7º Período/TCC I/Proposta III/O bendito/PropostaIII.pdf'
# 	pdf = PdfFileReader(path)
# 	#print(pdf.getPage(1).extractText())
# 	print(get_info(path))

# 	#paths = glob.glob('Plano de Ensino Sistemas de Informação II_*.pdf')
# 	#paths.sort()
# 	#merger('pdf_merger2.pdf', paths)

