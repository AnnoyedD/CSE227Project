import os
import struct
import os.path
import commands
import sys


def isElf(filename):
    try:
        f = open(filename, 'r')
        f.seek(0)
        hbytes = struct.unpack_from('BBB', f.read(3))
        if hbytes[0]==127 and hbytes[1]==69 and hbytes[2]==76:
            return True
        else:
            return False
    except:
        return False

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
    arch = pkgName.split('.')[-1]
    pkgName = '.'.join(pkgName.split('.')[:-1])
    log.write('Package: ' + str(pkgName) + '\n')
    status, output = commands.getstatusoutput('dnf download ' + pkgName)
    log.write('Download Package: ' + str(status) + '\n')
    fullName = pkgName + '-' + version + '.' + arch + '.rpm'
    curDir = os.getcwd()
    fileList = os.listdir(curDir)

    os.chdir('temp')
    status, output = commands.getstatusoutput('rpm2cpio ../' + fullName + ' | cpio -idm')
    os.chdir('..')
    log.write('Decompress package: '+ str(status) + '\n')

    for root, dirs, files in os.walk(curDir + '/temp'):
        for name in files:
            fileName = root + '/' + name
            if isElf(fileName):
                totalElf += 1
                status,output = commands.getstatusoutput('readelf -s '+fileName+' | grep \'__stack_chk_fail\'')
                if status==0 and output:
                    canaryNum += 1

        sys.stdout.write("\r%d out of %d" % (canaryNum, totalElf))
        sys.stdout.flush()
    status, output = commands.getstatusoutput('rm -rf temp/*')
    log.write('Remove temporary directory: ' + str(status) + '\n')
    log.write('Current Result (totalNum, totalElf, canaryNum)' + str(totalNum) + str(totalElf) + str(canaryNum) + '\n')
    #status, output = commands.getstatusoutput('rm -rf ' + fullName)
    status, output = commands.getstatusoutput('rm *.rpm')
