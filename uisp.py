import requests
import json
from collections import defaultdict
import os
import time
import psutil
from paramiko import client, ssh_exception
import config
import logging
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket

uisphost = config.host
uispusername = config.uispusername
uisppassword = config.uipspassword

sshusername = config.sshusername
sshpassword = config.sshpassword

Sites = config.Allsites

urlbase = uisphost
myobj = {'username': uispusername, 'password': uisppassword}

x = requests.post(urlbase + 'user/login', json = myobj, verify=False)
head = x.headers
headrs = json.dumps(dict(head))
jsonhead = json.loads(headrs)
authtoken = jsonhead["x-auth-token"]

p = requests.get(urlbase + 'devices', json = myobj, headers={'x-auth-token': authtoken}, verify=False)

data = p.json()

sitelist = []


for item in data:
	cpuusage = item["overview"]["cpu"]
	if cpuusage == 100:
		print(item["identification"]["site"]["name"])
		sitename = item["identification"]["site"]["name"]
		print(item["identification"]["hostname"])
		hostname = item["identification"]["hostname"]
		print(item["ipAddressList"][0])
		ipaddress = item["ipAddressList"][0]
		thissite = [sitename, ipaddress]
		sitelist.append(thissite)
result = defaultdict(list)
for i,j in sitelist:
	result[i].append(j)

siteHTML = ""

f = open("log.txt", "a")

for key in Sites:
	if key in result:
		siteVPNFile = Sites[key][0]
		siteVPNcfg = Sites[key][1]
		ipaddresses = result[key]
		print('Config file: ' + siteVPNFile)
		print('Text file: ' + siteVPNcfg)
		print('IP: ' + str(ipaddresses))
		os.system("sudo /usr/sbin/openvpn --config /home/mngsvc/UISP/VPN/" + siteVPNFile + " --auth-user-pass /home/mngsvc/UISP/VPN/key/" + siteVPNcfg + " &")
		print(key + " open")
		f.write(key + " open\n")
		siteHTML += "<b>" + key + "</b><br/>"
		time.sleep(10)
		for ip in ipaddresses:
			f.write("IP is: " + ip + "\n")
			print("IP is: " + ip)
			siteHTML += ip + "<br/>"
			ssh_client = client.SSHClient()
			try:
				ssh_client.set_missing_host_key_policy(client.AutoAddPolicy())

				ssh_client.connect(hostname=ip, username=sshusername, password=sshpassword, look_for_keys=False)
				f.write("Connected to " + ip + "\n")
				print("Connected to " + ip)
				device_access = ssh_client.invoke_shell()
				device_access.send("kill $(ps | grep '[{]exe} /bin/udapi-bridge' | awk '{print$1}')\n")
				time.sleep(2)
				output = device_access.recv(65535)
				f.write(output.decode() + "\n")
				print(output.decode(), end='')
				ssh_client.close()
				f.write("Kill command sent\n")
				print("Kill command sent")
			except ssh_exception.NoValidConnectionsError:
				f.write("Cannot connect to " + ip + "\n")
				print("Cannot connect to " + ip)
			except ssh_exception.AuthenticationException:
				f.write("Authentication error. Check username/password\n")
				print("Authentication error. Check username/password")
			except socket.timeout:
				f.write("Timeout to " + ip + "\n")
				siteHTML += (ip + " - Timeout<br/>")
		for proc in psutil.process_iter():
			if any (procstr in proc.name() for procstr in ['openvpn']):
				proc.kill()
		f.write(key + " closed\n")
		print(key + " closed")
		siteHTML += "<br/>"

f.close()
print(siteHTML)
if siteHTML == "":
	siteHTML = "No P2Ps required reboot"
	
sender_email = config.emailname
receiver_email = config.emailname
email_pass = config.emailpass

message = MIMEMultipart("alternative")
message["Subject"] = "P2P Report"
message["From"] = sender_email
message["To"] = receiver_email

part1 = MIMEText(siteHTML, "html")

message.attach(part1)

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
	server.login(sender_email, email_pass)
	server.sendmail(
		sender_email, receiver_email, message.as_string()
	)

