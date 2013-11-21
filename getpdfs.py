from BeautifulSoup import BeautifulSoup
import urllib
import cPickle as pickle

class JournalParser:
    def __init__(self, url):
        self.url = url
        html_page = urllib.urlopen(url+'index.html')
        self.soup = BeautifulSoup(html_page)

    def titles2dict(self,titles,authors):
        papers = zip(titles, authors)
        self.parse_links()
        self.dictpapers = dict(zip(self.idpdfs,papers))
        self.dictlinks  = dict(zip(self.idpdfs,self.linkpdfs))

    def get_pdf_files(self):
        for link,id_paper in zip(self.linkpdfs, self.idpdfs):
            savename = 'pdfs/' + id_paper + '.pdf'
            print "Downloading:", link, "in", savename
            urllib.urlretrieve(self.url+link,savename)

    def dump_author_data(self):
        for key in self.dictpapers:
            print key, "=", self.dictpapers[key]
        
        # dump a dictionary indexed by paper id that points to (title,
        # authors) tuple
        pickle.dump(self.dictpapers, open("papers.p", "wb"))
        pickle.dump(self.dictlinks, open("pdflinks.p", "wb"))

    def parse_links(self):
        self.linkpdfs = [link.get('href') for link in self.soup.findAll('a')
                         if link.get('href').endswith(".pdf")]

        self.idpdfs = [link.split('/')[-1][:-4] for link in self.linkpdfs]
        
class JournalParserJMLR(JournalParser):
    def parse_titles(self):
        titles = [title.find(text=True).strip()
                  for title in self.soup.findAll('dt')]
        authors = [auth.find(text=True).strip()
                   for auth in self.soup.findAll('dd')]
        self.titles2dict(titles,authors)


        
class JournalParserRSS(JournalParser):
    def parse_titles(self):
        titles = [link.find(text=True) for link in self.soup.findAll('a')
                  if link.get('href').strip('phtml.').isdigit()]

        authors = [name.find(text=True) for name in self.soup.findAll('i')]
        self.titles2dict(titles,authors)


    
if __name__ == "__main__":
    parser = JournalParserRSS("http://www.roboticsproceedings.org/rss09/")
    parser.parse_titles()
    parser.dump_author_data()
    parser.get_pdf_files()
    
