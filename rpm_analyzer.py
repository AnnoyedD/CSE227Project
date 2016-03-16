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

logFile = sys.argv[1]

log = open(logFile, 'w')

totalNum = 0
totalElf = 0
canaryNum = 0

curDir = os.getcwd()
commands.getstatusoutput('mkdir temp')
for rpmroot, rpmdirs, rpmfiles in os.walk(curDir + '/' + sys.argv[2]):
    if rpmfiles != []:
        for rpmName in rpmfiles:
            if not '.rpm' in rpmName:
                continue
            os.chdir('temp')
            commands.getstatusoutput('rpm2cpio ' + rpmroot + '/' + rpmName + ' | cpio -idm')
            os.chdir('..')

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
            log.write(rpmName + '\n')
            log.write('totalNum: %d, totalElf: %d, canaryNum: %d\n' % (totalNum, totalElf, canaryNum))
            status, output = commands.getstatusoutput('rm -rf temp/*')
#            commands.getstatusoutput('rm -rf ' + rpmroot + '/' + rpmName)

log.close()
commands.getstatusoutput('rm -rf temp')
print '\nFinished!'
