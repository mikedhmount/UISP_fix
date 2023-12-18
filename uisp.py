import requests
import json
from collections import defaultdict
import subprocess
import time
import psutil
import paramiko
import config

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

for key in Sites:
	if key in result:
		siteVPNFile = Sites[key][0]
		siteVPNcfg = Sites[key][1]
		ipaddresses = result[key]
		print('Config file: ' + siteVPNFile)
		print('Text file: ' + siteVPNcfg)
		print('IP: ' + str(ipaddresses))
		taskResult = subprocess.run(["sudo /usr/sbin/openvpn --config VPN/" + siteVPNFile + " --auth-user-pass key/" + siteVPNcfg ], shell=True, capture_output=True, text=True)
		print(taskResult)
		print(key + " open")
		time.sleep(30)
		for ip in ipaddresses:
			print("IP is: " + ip)
			ssh = paramiko.SSHClient()
			try:
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

				ssh.connect(ip,username=sshusername, password=sshpassword)

				print("Connected to " + ip)
				ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("kill $(ps | grep '[{]exe} /bin/udapi-bridge' | awk '{print$1})")
				print("Kill command sent")
				print(ssh_stdout.read().decode())

				ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('exit')
			except:
				print("Cannot connect to " + ip)

		for proc in psutil.process_iter():
			if any (procstr in proc.name() for procstr in ['openvpn']):
				proc.kill()
			
		print(key + " closed")