import os
from bs4 import BeautifulSoup
import requests
import json

from requests.exceptions import Timeout
import html2md
import random
import time

my_headers = [
        {'Connection': 'close','User-Agent':"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"},
        {'Connection': 'close','User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36"},
        {'Connection': 'close','User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0"},
        {'Connection': 'close','User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14"},
        {'Connection': 'close','User-Agent':"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"},
        {'Connection': 'close','User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'},
        {'Connection': 'close','User-Agent':'Opera/9.25 (Windows NT 5.1; U; en)'},
        {'Connection': 'close','User-Agent':'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)'},
        {'Connection': 'close','User-Agent':'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)'},
        {'Connection': 'close','User-Agent':'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12'},
        {'Connection': 'close','User-Agent':'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9'},
        {'Connection': 'close','User-Agent':"Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7"},
        {'Connection': 'close','User-Agent':"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0"}
    ]

refresh = False
start = '15_Advanced'
c = 1
timeo = 31

def url2ipynb(url,outfile):
    data = requests.get(url,headers = random.choice(my_headers),timeout=timeo)
    soup = BeautifulSoup(data.text, 'html.parser')

    ipynb = {'nbformat': 4, 'nbformat_minor': 1, 'cells': [], 'metadata': {}}
    divlist = soup.find_all('div', class_=['text_cell_render' , 'input_area'])
    if divlist:
        for d in divlist:
            if "input_area" in d['class']:
                cell = {}
                cell['metadata'] = {}
                cell['outputs'] = []
                cell['source'] = [d.get_text()]
                cell['execution_count'] = None
                cell['cell_type'] = 'code'
            else:
                cell = {}
                cell['metadata'] = {}

                cell['source'] = [html2md.html2md(str(d))]
                cell['cell_type'] = 'markdown'
            ipynb['cells'].append(cell)
        open(outfile, 'w').write(json.dumps(ipynb))

url = 'https://plotly.com/python/'
os.chdir('plotly')

try:
    with open('main.tmp') as f:
        maintxt = f.read()
except IOError:
    data = requests.get(url,headers = random.choice(my_headers),timeout=timeo)
    maintxt=data.text
    with open('main.tmp','w') as f:
        f.write(maintxt)
    
soup = BeautifulSoup(maintxt, 'html.parser')
tutorial_sec=soup.findAll('section',class_='--tutorial-section')

for sec in tutorial_sec:
    dirname = '%02d_'%c +'_'.join(sec.header.a.get_text().split())
    c += 1
    
    if  start and start != dirname :
        continue
    else:
        start = ''

    print(dirname)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    os.chdir(dirname)
    a=sec.find(lambda x: x.name=='a' and 'More' in x.get_text())
    if a:
        try:
            with open('chapter.tmp') as f:
                maintxt = f.read()
        except IOError:
            data = requests.get('https://plotly.com'+a['href'],headers = random.choice(my_headers),timeout=timeo)
            maintxt=data.text
            with open('chapter.tmp','w') as f:
                f.write(maintxt)
        
        s = BeautifulSoup(maintxt, 'html.parser')

        sub_sec=s.find('section',class_='--tutorial-section')
        linklist = sub_sec.findAll('a')
    else:
        linklist = sec.findAll('a')
        # del linklist[0]
    
    i = 1
    for atag in linklist:
        if atag['href'].startswith('http') or atag['href'].startswith('#') : continue
        outfile = '%02d_'%i + '_'.join(atag.span.get_text().split()) + '.ipynb'
        if not os.path.exists(outfile) or refresh:
            time.sleep(random.randint(1,4))
            url2ipynb('https://plotly.com'+atag['href'] , outfile)
            print(outfile)
        else:
            print('Skip %s'%outfile)
        i += 1

    try:
        os.remove('chapter.tmp')
    except:
        pass
    
    os.chdir('..')

try:
    os.remove('main.tmp')
except:
    pass