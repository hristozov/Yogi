import telnetlib
import urllib

def getASN(ipaddr):
    """Gets the ASN of an IP address"""
    tn=telnetlib.Telnet('whois.radb.net',43)
    tn.write(ipaddr+" \n")
    d=tn.read_all().split()
    for q in range(len(d)):
        if d[q]=="origin:":
            return d[q+1][2:]
    return 0

def getCountry(ipaddr):
    """Gets the country code of an IP address"""
    d=urllib.urlopen("http://api.hostip.info/get_html.php?ip="+ipaddr).readlines()[0]
    d.replace('\n','')
    return d.split()[-1][1:-1]

if __name__=="__main__":
    pass #testing
