from sqlite3 import Timestamp
import requests
import sys
import re
import argparse

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

FIRST_RESPONSE = None
FIRST_TITLE = None
WILD_RESPONSE = None
WILD_TITLE = None

def get_domain(url):
	r = '(?<=\\.)[\\w+(\\-|).]+'
	d = re.findall(r, url)
	
	return d[0]

def req(url, host):
	header = {}
	
	if host != None:
		host = host.replace("\n","")
		header["Host"] = host+DOMAIN
	
	header["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
	header["Forwarded"] = "127.0.0.1"
	header["X-Client-IP"] = "127.0.0.1"
	header["X-Forwarded-By"] = "127.0.0.1"
	header["X-Forwarded-For"] = "127.0.0.1"
	header["X-Forwarded-For-IP"] = "127.0.0.1"
	header["X-Forwarded-Host"] = "127.0.0.1"
	header["X-Host"] = "127.0.0.1"
	header["X-Originating-IP"] = "127.0.0.1"
	header["X-Remote-Addr"] = "127.0.0.1"
	header["X-Remote-IP"] = "127.0.0.1"
	header["X-True-IP"] = "127.0.0.1"
	try:
		resp = requests.get(url, headers=header, proxies=PROXY, verify=False, allow_redirects=False, timeout=5)
	except:
		resp = None
	return resp

def default_of_url(url):
	global FIRST_RESPONSE
	global FIRST_TITLE

	resp = req(url, None)
	infos = get_content_infos(resp)
	FIRST_RESPONSE = infos["content-length"]
	FIRST_TITLE = infos["title"]

def check_error_response(url):
	global WILD_RESPONSE
	global WILD_TITLE

	host = "b25SsZgfsW"
	infos = get_content_infos(req(url,host))
	WILD_RESPONSE = infos["content-length"]
	WILD_TITLE = infos["title"]

def get_content_infos(resp):
	infos = {}
	infos["title"] = None
	if resp != None:
		soup = BeautifulSoup(resp.text, 'html.parser')
		infos["content-length"] = str(len(resp.content))
		infos["status"] = str(resp.status_code)
		for htmltitle in soup.find_all('title'):
				infos["title"] = htmltitle.get_text().replace("\n","")
		if infos["status"] == 301:
			infos["title"] = "Redirect"
	else:
		infos["content-length"] = None
		infos["status"] = None

	
	return infos

def check_response(infos, host):
	host = host.replace("\n","")
	if infos["status"] == 409:
		if infos["content-length"] != FIRST_RESPONSE and infos["content-length"] != WILD_RESPONSE:
			if infos["title"] != FIRST_TITLE and infos["title"] != WILD_TITLE:
				print(f'\u001b[33;1m[vhospping] [host:{host}] [info] {URL} {infos["status"]}\u001b[0m')
				save(host)

def save(host):
	if host not in HOSTS_FOUND:
		HOSTS_FOUND.append(host)

def outpout_save(url, output):
	arq = open(output, "w+")
	for x in HOSTS_FOUND:
		x = x.replace("\n","")
		arq.write(f"[vhospping] [host:{x}] [low] {url}\n")
	arq.close()

def run(host):
	check_response(get_content_infos(req(URL,host)), host)

def executor():
	try:
		with ThreadPoolExecutor() as t:
			t.map(run, HOSTS, timeout=3)
	except KeyboardInterrupt:
		outpout_save(OUTPUT)
		sys.exit()

def url_list_mode():
	global URL
	global DOMAIN

	for x in URLLIST:
		URL = x.replace("\n","")
		DOMAIN = "."+get_domain(URL)
		default_of_url(URL)
		check_error_response(URL)

		print(f"""
[!] Running on {URL}
[i] Normal content-length: {FIRST_RESPONSE}
[i] Normal Title: {FIRST_TITLE}
[i] Wild content-length: {WILD_RESPONSE}
[i] Wild Title: {WILD_TITLE}

""")
		executor()
	
	print(f"\n[!] Finish, total found {str(len(HOSTS_FOUND))}")
	
	if len(HOSTS_FOUND) > 0:
		print(f"[+] Se you results in {OUTPUT}")
		outpout_save(URL, OUTPUT)


def normal_mode():

	default_of_url(URL)
	check_error_response(URL)

	print(f"""
[!] Running on {URL}
[i] Normal content-length: {FIRST_RESPONSE}
[i] Normal Title: {FIRST_TITLE}
[i] Wild content-length: {WILD_RESPONSE}
[i] Wild Title: {WILD_TITLE}

""")
	
	executor()
	print(f"\n[!] Finish, total found {str(len(HOSTS_FOUND))}")
	
	if len(HOSTS_FOUND) > 0:
		print(f"[+] Se you results in {OUTPUT}")
		outpout_save(URL, OUTPUT)

if __name__ == '__main__':
	
	banner = """\u001b[33;1m
                   
   /    _     '  _ 
\//)()_) /)/)//)(/ 
        / /    _/  

	\u001b[0m"""
	print(banner)
	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument("-u", "--url", help="Url")
	parser.add_argument("-uL", "--urlList", help="Url list mode")
	parser.add_argument("-d", "--domain", help="Force domain for header")
	parser.add_argument("-w", "--wordlist", help="Wordlist for hosts")
	parser.add_argument("-s","--subdomainsList", help="Use subdomains for brute force")
	parser.add_argument("-p","--proxy", help="Proxy url for debug Ex: http://127.0.0.1:8080")
	parser.add_argument("-o", "--output", help="Output for save",required=True)
	args = parser.parse_args()

	OUTPUT = args.output
	FIRST_RESPONSE = {}
	HOSTS_FOUND = []
	PROXY = None
	URL = args.url

	if args.proxy:
		PROXY = {"http":args.proxy,"https":args.proxy}

	if args.subdomainsList != None and args.domain == None:
		DOMAIN = ""
		HOSTS = open(args.subdomainsList).readlines()

	if args.subdomainsList == None:
		HOSTS = open(args.wordlist).readlines()

	if args.urlList != None:
		URLLIST = open(args.urlList).readlines()
		url_list_mode()

	if args.domain == None and args.subdomainsList == None:
		DOMAIN = "."+get_domain(URL)

	if args.domain != None and args.subdomainsList == None:
		DOMAIN = "."+args.domain

	if args.url != None:
		URL = args.url
		normal_mode()

