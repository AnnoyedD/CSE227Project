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

for l in avail:
    if len(l.split()) != 3:
        continue
    totalNum += 1
    pkgName = l.split()[0]
    version = l.split()[1]
    pkgName, arch = pkgName.split('.')
    log.write.('Package: ' + str(pkgName))
    status, output = commands.getstatusoutput('dnf download ' + pkgName)
    log.write('Download Package: ' + str(status) + '\n')
    fullName = pkgName + '-' + version + '.' + arch + '.rpm'
    curDir = os.getcwd()
    fileList = os.listdir(curDir)

    status, output = commands.getstatusoutput('rpm2cpio ' + fullName + ' | cpio -idm')
