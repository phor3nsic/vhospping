import requests
import sys
import re
import argparse

from concurrent.futures import ThreadPoolExecutor
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def getDomain(url):
	r = '(?<=\\.)[\\w+.]+'
	d = re.findall(r, url)
	return d[0]

def req(url, host):
	header = ""
	if host != None:
		host = host.replace("\n","")
		header = {"host":host+DOMAIN}
	resp = requests.get(url, headers=header, proxies=PROXY, verify=False)
	return resp

def getProps(resp):
	sc = resp.status_code
	cl = len(resp.text)
	return {"sc":sc,"cl":cl}

def getFirstReq(url):
	resp = req(url, None)
	props = getProps(resp)
	FIRST_RESPONSE["sc"] = props["sc"]
	FIRST_RESPONSE["cl"] = props["cl"]

def save(host):
	if host not in HOSTS_FOUND:
		HOSTS_FOUND.append(host)

def checkResp(props, host):
	scs = [200,500,503,401,403]
	sc = props["sc"]
	cl = props["cl"]

	fsc = FIRST_RESPONSE["sc"]
	fcl = FIRST_RESPONSE["cl"]

	if sc in scs:
		if cl != fcl:
			save(host)

def outputSave(url, output):
	arq = open(output, "w+")
	for x in HOSTS_FOUND:
		x = x.replace("\n","")
		arq.write(f"[vhospping] [host:{x}] [low] {url}\n")
	arq.close()

def run(host):
	checkResp(getProps(req(URL,host)), host)

def main():
	getFirstReq(URL)
	print(f"[!] Running on {URL}")

	try:
		with ThreadPoolExecutor() as t:
			t.map(run, HOSTS, timeout=3)
	except KeyboardInterrupt:
		outputSave(OUTPUT)
		sys.exit()
	
	print(f"[!] Finish, total found {str(len(HOSTS_FOUND))}")
	if len(HOSTS_FOUND) > 0:
		print(f"[+] Se you results in {OUTPUT}")
		outputSave(URL, OUTPUT)

if __name__ == '__main__':
	
	banner = """\u001b[33;1m
                   
   /    _     '  _ 
\//)()_) /)/)//)(/ 
        / /    _/  

	\u001b[0m"""
	print(banner)
	parser = argparse.ArgumentParser(add_help=True)
	parser.add_argument("-u", "--url", help="Url",required=True)
	parser.add_argument("-d", "--domain", help="Force Domain for header")
	parser.add_argument("-w", "--wordlist", help="Wordlist For hosts")
	parser.add_argument("-s","--subdomainsList", help="Use subdomains for brute force")
	parser.add_argument("-p","--proxy", help="Proxy url for Debug")
	parser.add_argument("-o", "--output", help="Output for save",required=True)
	args = parser.parse_args()

	URL = args.url
	OUTPUT = args.output
	FIRST_RESPONSE = {}
	HOSTS_FOUND = []
	PROXY = None

	if args.proxy:
		PROXY = {"http":args.proxy,"https":args.proxy}

	if args.domain == None and args.subdomainsList == None:
		DOMAIN = "."+getDomain(URL)

	if args.domain != None and args.subdomainsList == None:
		DOMAIN = "."+args.domain

	if args.subdomainsList != None and args.domain == None:
		DOMAIN = ""
		HOSTS = open(args.subdomainsList).readlines()

	if args.subdomainsList == None:
		HOSTS = open(args.wordlist).readlines()

	main()