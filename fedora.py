import os
import os.path
from pwn import pwnlib
import commandss

pkgInfo = 'avail.txt'
logFile = 'fedora23.log'

log = open(logFile, 'w')

status, output = commands.getstatusoutput('dnf updateinfo')
log.write('Packages update: ' + str(status) + '\n\n')

status, output = commands.getstatusoutput('dnf list available > ' + pkgInfo)
log.write('Dump available packages: ' + str(status) + '\n\n')

avail = open(pkgInfo, 'r')

totalNum = 0
totalElf = 0
canaryNum = 0

#for l in avail:
