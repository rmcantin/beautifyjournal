# creates the nice .html page
# assumes that pdftowordcloud.py, pdftothumbs.py and scrape.py were already run

import cPickle as pickle
from numpy import argmax, zeros, ones
from math import log

def generate_page(pdflinkbase=None, bibtexlinkbase=None,
		  titlepage=None, urlold=None):
    use_images = False

    # load the pickle of papers scraped from the HTML page (result of
    # scrape.py)
    paperdict = pickle.load(open( "papers.p", "rb" ))
    print "Loaded %d papers from papers.p" % (len(paperdict), )

    # load the top word frequencies (result of pdftowordcloud.py)
    topdict = pickle.load(open("topwords.p", "rb"))
    print "Loaded %d entries from topwords.p" % (len(topdict), )

    # load LDA words and invert their dictionary list
    (ldak, phi, voca) = pickle.load(open("ldaphi.p", "rb"))
    wtoid = {}
    for i,w in enumerate(voca):
	wtoid[w] = i

    # compute pairwise distances between papers based on top words
    # using something similar to tfidf, but simpler. No vectors
    # will be normalized or otherwise harmed during this computation.
    # first compute inverse document frequency (idf)
    N = len(paperdict) # number of documents
    idf = {}
    for pid,p in enumerate(paperdict):
	tw = topdict.get(p, []) # top 100 words
	ts = [x[0] for x in tw]
	for t in ts:
	    idf[t] = idf.get(t, 0.0) + 1.0
    for t in idf:
	idf[t] = log(N/idf[t], 2)

    # now compute weighted intersection
    ds = zeros((N, N))
    for pid,p in enumerate(paperdict):
	tw = topdict.get(p, [])
	w = set([x[0] for x in tw]) # just the words
	accum = 0.0

	for pid2, p2 in enumerate(paperdict):
	    if pid2<pid: continue
	    tw2= topdict.get(p2, [])
	    w2 = set([x[0] for x in tw2]) # just the words

	    # tw and tw2 are top 100 words as (word, count) in both
	    # papers. Compute the intersection!
	    winter = w.intersection(w2)
	    score = sum([idf[x] for x in winter])
	    ds[pid, pid2] = score
	    ds[pid2, pid] = score

    # build up the string for html
    html = open("nipsnice_template.html", "r").read()
    s = ""
    js = "ldadist=["
    js2 = "pairdists=["
    for pid, p in enumerate(paperdict):

	# get title, author
	title, author = paperdict[p]

	# create the tags string
	topwords = topdict.get(p, [])
	# some top100 words may not have been computed during LDA so
	# exclude them if they aren't found in wtoid
	t = [x[0] for x in topwords if x[0] in wtoid]
	# assign each word to class
	tid = [int(argmax(phi[:, wtoid[x]])) for x in t] 
	tcat = ""
	for k in range(ldak):
	    ws = [x for i,x in enumerate(t) if tid[i]==k]
	    tcat += '[<span class="t'+ `k` + '">' + ", ".join(ws) + '</span>] '
	
	# count up the complete distribution for the entire document
	# and build up a javascript vector storing all this
	svec = zeros(ldak)
	for w in t: 
	    svec += phi[:, wtoid[w]]
	if svec.sum() == 0: 
	    svec = ones(ldak)/ldak;
	else: 
	    svec = svec / svec.sum() # normalize
	nums = [0 for k in range(ldak)]
	for k in range(ldak): 
	    nums[k] = "%.2f" % (float(svec[k]), )
	
	js += "[" + ",".join(nums) + "]"
	if not pid == len(paperdict)-1: js += ","

	# dump similarities of this document to others
	scores = ["%.2f" % (float(ds[pid, i]),) for i in range(N)]
	js2 += "[" + ",".join(scores) + "]"
	if not pid == len(paperdict)-1: js2 += ","

	# get path to thumbnails for this paper
	thumbpath = "thumbs/%s.pdf.jpg" % (p, )

	# get links to PDF, supplementary and bibtex on NIPS servers
#	if pdflinkbase: pdflink = pdflinkbase+ "%s/%s.pdf" % (p,p)
#	if bibtexlinkbase:bibtexlink = bibtexlinkbase + "%s.html" % (p, )

	bibtexlink = bibtexlinkbase % (p, )
	pdflink = pdflinkbase % (p,p)

	s += """

	<div class="apaper" id="pid%d">
	<div class="paperdesc">
		<span class="ts">%s</span><br />
		<span class="as">%s</span><br /><br />
	</div>
	<div class="dllinks">
		<a href="%s">[pdf] </a>
		<a href="%s">[bibtex] </a>
		<span class="sim" id="sim%d">[rank by tf-idf similarity to this]</span>
	</div>
	<img src = "%s"><br />
	<span class="tt">%s</span>
	</div>

	""" % (pid, title, author, pdflink, bibtexlink, pid, thumbpath, tcat)

    newhtml = html.replace("TITLEPAGE", titlepage)
    newhtml = newhtml.replace("URL_MAIN", urlold)
    newhtml = newhtml.replace("RESULTTABLE", s)

    js += "]"
    newhtml = newhtml.replace("LOADDISTS", js)

    js2 += "]"
    newhtml = newhtml.replace("PAIRDISTS", js2)

    with open("nipsnice.html", "w") as f:
        f.write(newhtml)
	f.close()

if __name__ == "__main__":
    generate_page(bibtexlinkbase="http://www.jmlr.org/papers/v13/%s.html",
		  pdflinkbase="http://www.jmlr.org/papers/volume13/%s/%s.pdf",
		  titlepage="JMLR Vol 13",
		  urlold="http://jmlr.csail.mit.edu/papers/v13/")
