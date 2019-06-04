import os
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfFileMerger
#import textract
import glob

import os
from stat import *
import re

import hashlib

def pdf_splitter(ip, path, num_pages, md5):
	fname = os.path.splitext(os.path.basename(path))[0]
 
	pdf = PdfFileReader(path)

	paths_str = []

	for page in num_pages:
		pdf_writer = PdfFileWriter()

		#print(extract_text(pdf.getPage(page)))

		pdf_writer.addPage(pdf.getPage(page-1))
 
		output_filename = 'temp/{}_page_{}.pdf'.format(
			md5, page+1)

		paths_str.append(output_filename)
 
		with open(output_filename, 'wb') as out:
			pdf_writer.write(out)

	return merger_split(paths_str, md5, ip)


def merger_split(input_paths, md5, ip):
	pdf_merger = PdfFileMerger()
	file_handles = []

	for path in input_paths:
		pdf_merger.append(path)

	with open('temp/{}_{}.pdf'.format(md5, ip), 'wb') as fileobj:
		pdf_merger.write(fileobj)
	return 'temp/{}_{}.pdf'.format(md5, ip)


def merger(input_paths, name_file):
	pdf_merger = PdfFileMerger()
	file_handles = []
 
	for path in input_paths:
		pdf_merger.append(path)
 
	with open('files/{}'.format(name_file), 'wb') as fileobj:
		pdf_merger.write(fileobj)
	return 'files/{}'.format(name_file)




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
	return page.extractText()


def get_info(path):
	st = os.stat(path)
	name = path.split('/')[-1]
	url = path
	size = st[ST_SIZE]
	num_pages, count_words_by_pages, md5 = info_run_pages(path)

	return {'name':name, 'url':url, 'size':size, 'num_pages':num_pages, 'count_words_by_pages':count_words_by_pages, 'md5': md5.hexdigest()}


def fat_per(x):
	a = 100/x
	l = []
	for i in range(x):
		l.append(a)
	for y in range(len(l)-1):
		l[y] = l[y]/2
		l[y+1] += l[y]
		return l


def pages(num_pages, peers):
	aux_peers = peers
	peers = len(peers)

	if peers == 1:
		return[[aux_peers[0], [i for i in range(1, num_pages+1)]]]

	percents = fat_per(peers)
	percents.sort(reverse=True)

	w_peers = []

	for p in percents:
		a = (p/100) * num_pages
		w_peers.append(round(a))

	if sum(w_peers) > num_pages:
		w_peers[0] = w_peers[0] - (sum(w_peers) - num_pages)
	if sum(w_peers) < num_pages:
		w_peers[0] = w_peers[0] + (num_pages-sum(w_peers))

	pages_by_hosts = []

	for ip in range(peers):
		if ip == 0:
			pages_by_hosts.append([aux_peers[ip], [i for i in range(1, w_peers[ip] + 1)]])
		else:
			pages_by_hosts.append([aux_peers[ip], [i for i in range(pages_by_hosts[-1][1][-1]+1, pages_by_hosts[-1][1][-1] + w_peers[ip] + 1)]])

	return pages_by_hosts