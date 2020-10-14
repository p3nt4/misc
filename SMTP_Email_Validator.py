import telnetlib
import argparse


def verifyEmail(tn, email, debug=False):
    buffer = 'RCPT TO: ' + email
    if debug: print("[*] " + buffer)
    tn.write(buffer.encode('ascii') + b"\n")
    read = tn.read_until(b"\n")
    if debug: print("[*] " + read.decode('ascii').strip())
    if "ok" in read.decode('ascii'):
        print("[+] VALID EMAIL: " + email)
    else:
        print("[-] INVALID EMAIL: " + email)



def main(args):
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

    if args.address:
        verifyEmail(tn, args.address, debug=args.debug)

    elif args.file:
        with open(args.file, 'r') as file1:
            for line in file1.readlines():
                verifyEmail(tn, line.strip(), debug=args.debug)
    tn.close()


if __name__== "__main__":
    parser = argparse.ArgumentParser(description='Check if email addres is valid over SMTP')
    parser.add_argument("-s", "--server", required=True,  help="SMTP server to connect to")
    parser.add_argument("-p", "--port", default=25, type=int, help="Port to connect to")
    parser.add_argument("-f", "--file", help="File containing email addresses to test")
    parser.add_argument("-a", "--address", help="Test a single address")
    parser.add_argument("-m", "--mailfrom", help="Source email")
    parser.add_argument("-d", "--debug", action='store_const', default=False, const=True, help="Enable debugging")
    args = parser.parse_args() 
    main(args) 