import sys
if (len(sys.argv)<2):
    print ("Usage: " + sys.argv[0] + " <File>")
    exit

x = open(sys.argv[1], "r", encoding="utf-8").read()

chunks, chunk_size = len(x), 100
arr = [ x[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]

for a in arr:
    print('oFile.Write "' +a.replace('"','""').replace("\r\n","\n").replace("\n",'"\r\noFile.WriteLine ""\r\n') + "\"")
