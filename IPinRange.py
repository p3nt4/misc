from netaddr import IPNetwork, IPAddress
import sys

def addressInNetwork(ip,net):
    if IPAddress(ip) in IPNetwork(net):
        return True
    return False



def main():
    if len(sys.argv) < 3:
        print("Usage: " + sys.argv[0] + " <IPS> <RANGES>" )
        return 1
    
    ranges = [line.rstrip('\n') for line in open(sys.argv[2])]
    ips = [line.rstrip('\n') for line in open(sys.argv[1])]

    for ip in ips:
        for r in ranges:
            try:
                if addressInNetwork(ip,r):
                    print(ip)
                    break
            except Exception as e:
                print(e)
                pass

if __name__== "__main__":
  main()
