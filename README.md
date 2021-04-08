<h1 align="center">
  <br>
  <a href="#"><img src="img/jump.png" width="100px" alt="Nuclei">Vhospping</a>
</h1>

<h4 align="center">Abuse of vhost hopping or proxy pass</h4>

---

> https://mobile.twitter.com/Bugcrowd/status/1372034980164014082/photo/1

## How it works

<h3 align="center">
  <img src="img/banner.png" alt="nuclei-flow" width="700px"></a>
</h3>

## Install
```sh
▶ git clone https://github.com/phor3nsic/vhospping.git
```
### Running

Scanning with hosts.
```sh
▶ python3 vhospping.py -u https://example.com -w wordlist.txt -o output.txt
``` 

Scanning forcing domain.
```sh
▶ python3 vhospping.py -u https://example.com -d example.com -w wordlist.txt -o output.txt
``` 

Scanning with subdomains.
```sh
▶ python3 vhospping.py -u https://example.com -s subdomains.txt -o output.txt
```

Scanning with proxy.
```sh
▶ python3 vhospping.py -u https://example.com -w wordlist.txt -o output.txt -p http://127.0.0.1:8080
```

## Tags
`fuzz` `proxy_pass` `vhost hopping`