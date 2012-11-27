# go over all pdfs in NIPS, get all the words from each, discard stop
# words, count frequencies of all words, retain top 100 for each PDF
# and dump a pickle of results into topwords.p

import os
import re
import cPickle as pickle
from string import punctuation
from operator import itemgetter
from pyPdf import PdfFileReader

class PDFextractor:
    def __init__(self):
	self.N= 100 # how many top words to retain
		
	# load in stopwords (i.e. boring words, these we will ignore)
	stopwords = open("stopwords.txt", "r").read().split()
	self.stopwords = [x.strip(punctuation) for x in stopwords if len(x)>2]
        
    def get_files_local(self):
	# get list of all PDFs supplied by NIPS
	self.relpath = "pdfs/"
	allFiles = os.listdir(self.relpath)
	self.pdfs = [x for x in allFiles if x.endswith(".pdf")]

    def get_files_network(self):
        pass

    def get_words(self):
	# go over every PDF, use pdftotext to get all words, discard
	# boring ones, and count frequencies
	topdict = {} # dict of paperid -> [(word, frequency),...]
	with open("allpapers.txt", "w") as outf:
            for i,f in enumerate(self.pdfs):
		paperid = f[:-4]
		fullpath = self.relpath + f

		print "processing %s, %d/%d" % (paperid, i, len(self.pdfs))

		# create text file
		cmd = "pdftotext %s %s" % (fullpath, "out.txt")
		print "EXEC: " + cmd
		os.system(cmd)
	    
		# get all words in a giant list
		txtlst = open("out.txt").read().split() 
		# take only alphanumerics
		words = [x.lower() for x in txtlst
			 if re.match('^[\w-]+$', x) is not None] 
		# remove stop words
		words = [x for x in words
			 if len(x)>2 and (not x in self.stopwords)]
	    

		# count up frequencies of all words
		wcount = {} 
		for w in words: wcount[w] = wcount.get(w, 0) + 1
		top = sorted(wcount.iteritems(), key=itemgetter(1),
			     reverse=True)[:self.N] # sort and take top N

		topdict[paperid] = top # save to our dict

		# For LDA: only take words that occurr at least a bit (for
		# efficiency)
		words = [x for x in words if wcount[x] >= 3]

		outf.write(" ".join(words))
		outf.write("\n")

	# dump to pickle
	pickle.dump(topdict, open("topwords.p", "wb"))

    def get_thumbs(self):
        for i,f in enumerate(self.pdfs):
            paperid = f[:-4]
            fullpath = self.relpath + f

            inputpdf = PdfFileReader(file(fullpath, "rb"))
            numpages = inputpdf.getNumPages()
            if numpages > 8:
		l1 = numpages-6
		l2 = numpages-2
            else:
		l1 = 2
		l2 = 6
            print "processing %s, %d/%d" % (paperid, i, len(self.pdfs))

            # this is a mouthful...  take first 8 pages of the pdf
            # ([0-7]), since 9th page are references tile them
            # horizontally, use JPEG compression 80, trim the borders for
            # each image
	
            cmd = "montage %s[0-1] %s[%d-%d] -mode Concatenate -tile x1 -quality 80 -resize x230 -trim %s" % (fullpath, fullpath, l1,l2, "thumbs/" + f + ".jpg")
            print "EXEC: " + cmd
            os.system(cmd)


if __name__ == "__main__":
    converter = PDFextractor()
    converter.get_files_local()
    converter.get_words()
    converter.get_thumbs()
