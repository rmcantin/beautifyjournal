from BeautifulSoup import BeautifulSoup
import urllib
import cPickle as pickle

class JournalParser:
    def __init__(self, url):
        self.url = url
        html_page = urllib.urlopen(url)
        self.soup = BeautifulSoup(html_page)

    def parse_titles_jmlr(self):
        titles = [title.find(text=True).strip()
                  for title in self.soup.findAll('dt')]
        authors = [auth.find(text=True).strip()
                   for auth in self.soup.findAll('dd')]
        self.titles2dict(titles,authors)
        
    def parse_titles_rss(self):
        titles = [link.find(text=True) for link in soup.findAll('a')
                  if link.get('href').strip('phtml.').isdigit()]

        authors = [name.find(text=True) for name in soup.findAll('i')]
        self.titles2dict(titles,authors)

    def titles2dict(self,titles,authors):
        papers = zip(titles, authors)
        linkpdfs = [link.get('href') for link in self.soup.findAll('a')
                         if link.get('href').endswith(".pdf")]

        idpdfs = [link.split('/')[-1][:-4] for link in linkpdfs]
        self.linkids = zip(linkpdfs, idpdfs)
        self.dictpapers = dict(zip(idpdfs,papers))


    def get_pdf_files(self):
        for link,id_paper in self.linkids:
            savename = 'pdfs/' + id_paper + '.pdf'
            print "Downloading:", link, "in", savename
            urllib.urlretrieve(link,savename)

    def dump_author_data(self):
        for key in self.dictpapers:
            print key, "=", self.dictpapers[key]
        
        # dump a dictionary indexed by paper id that points to (title,
        # authors) tuple
        pickle.dump(self.dictpapers, open("papers.p", "wb"))


if __name__ == "__main__":
    parser = JournalParser("http://jmlr.csail.mit.edu/papers/v13/")
    parser.parse_titles_jmlr()
    parser.dump_author_data()
    
