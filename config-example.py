from collections import defaultdict
#   UISP Information

host = 'UISP IP or URL'
uispusername = 'UISP suername'
uipspassword = 'UISP password'

#   SSH Credentials
sshusername = 'device ssh username'
sshpassword = 'device ssh password'

#   Sites
Sites = defaultdict(lambda: "Not Present")
Sites['UISP sitename 1'] = ['UISP sitename 1.ovpn', 'UISP sitename 1.txt']
Sites['UISP sitename 2'] = ['UISP sitename 2.ovpn', 'UISP sitename 2.txt']
Sites['UISP sitename 3'] = ['UISP sitename 3.ovpn', 'UISP sitename 3.txt']

Allsites = Sites