import telnetlib
import argparse
from threading import Thread
from queue import Queue
import time

def verifyEmail(tn, email, q2, debug=False):
    buffer = 'RCPT TO: ' + email
    if debug: print("[*] " + buffer)
    tn.write(buffer.encode('ascii') + b"\n")
    read = tn.read_until(b"\n")
    if debug: print("[*] " + read.decode('ascii').strip())
    if "Ok" in read.decode('ascii'):
        q2.put("[+] VALID EMAIL: " + email)
    else:
        q2.put("[-] INVALID EMAIL: " + email)


def connect(args):
    tn = telnetlib.Telnet(args.server,args.port)

    ## HANDSHAKE
    read = tn.read_until(b"\n")
    if args.debug: print("[*] " + read.decode('ascii').strip())
    name = read.decode('ascii').split(' ')[1]
    buffer = 'HELO ' + name
    if args.debug: print("[*] " + buffer)
    tn.write(buffer.encode('ascii') + b"\n")
    read = tn.read_until(b"\n")
    if args.debug: print("[*] " + read.decode('ascii').strip())

    ## MAIL FROM
    buffer = 'MAIL FROM: ' + args.mailfrom
    if args.debug: print("[*] " + buffer)
    tn.write(buffer.encode('ascii') + b"\n")
    read = tn.read_until(b"\n")
    if args.debug: print("[*] " + read.decode('ascii').strip())
    return tn


def verificator(args, q, q2):
    tn = connect(args)
    while not(q.empty()):
        try:
            item = q.get(block=True)
        except:
            pass
        try:
            verifyEmail(tn, item,  q2, debug=args.debug)
        except:
            tn = connect(args)
            try:
                verifyEmail(tn, item,  q2, debug=args.debug)
            except:
                pass
    q2.put("THREAD_CLOSED")
    tn.close()
    
def writer(args, q2):
    closed_count = 0;
    
    if (args.output):
        f = open(args.output, "w")
    
    while (closed_count < args.threads):
        time.sleep(1)
        while not(q2.empty()):
            e = q2.get(block=True)
            if (e == "THREAD_CLOSED"):
                closed_count += 1
            else:
                if(args.output):
                    f.write(e + "\n")
                else:
                    print(e)
    
    if (args.output):
        f.close()
    

def main(args):
    q = Queue()
    q2 = Queue()
    if args.address:
        q.put(args.address)

    elif args.file:
        with open(args.file, 'r') as file1:
            for line in file1.readlines():
                q.put(line.strip())
                
    for x in range(args.threads):
        thread = Thread(target = verificator,args=(args, q, q2,))
        thread.start()
    thread = Thread(target = writer,args=(args, q2,))
    thread.start()

if __name__== "__main__":
    parser = argparse.ArgumentParser(description='Check if email addres is valid over SMTP')
    parser.add_argument("-s", "--server", required=True,  help="SMTP server to connect to")
    parser.add_argument("-o", "--output", help="Write output to a file")
    parser.add_argument("-p", "--port", default=25, type=int, help="Port to connect to")
    parser.add_argument("-f", "--file", help="File containing email addresses to test")
    parser.add_argument("-a", "--address", help="Test a single address")
    parser.add_argument("-m", "--mailfrom", help="Source email")
    parser.add_argument("-t", "--threads", default=1, type=int, help="Number of threads")
    parser.add_argument("-d", "--debug", action='store_const', default=False, const=True, help="Enable debugging")

    args = parser.parse_args() 
    main(args) 
