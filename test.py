import os
import os.path
from pwn import pwnlib
import commands

pkgInfo='avail.txt'
logFile='ubuntu15_04.log'

log=open(logFile,'w')

status,output=commands.getstatusoutput('apt-get update')
log.write('Packages update: '+str(status)+'\n\n')

status,output=commands.getstatusoutput('apt-cache dumpavail > '+pkgInfo)
log.write('Dump available packakges: '+str(status)+'\n\n')

avail=open(pkgInfo,'r')

totalNum=0
totalElf=0
canaryNum=0

line=avail.readline()
while line:
  if line.find('Package: ')==0:
    totalNum+=1

    length=len(line)
    sName=line[9:length].strip()
    log.write('Package: '+str(sName))

    status,output=commands.getstatusoutput('apt-get download '+sName)
    log.write('Download package: '+str(status)+'\n')
    
    curDir=os.getcwd()
    fileList=os.listdir(curDir)

    for f in fileList:
      if f.find('.deb')!=-1:
	status,output=commands.getstatusoutput('dpkg-deb -x '+f+' temp')
	log.write('Decompress package: '+str(status)+'\n')	

	for root,dirs,files in os.walk(curDir+'/temp'):
	  for name in files:
	    fileName=root+'/'+name
	    if os.access(fileName,os.X_OK):
	      try:
	        absElf=pwnlib.elf.ELF(fileName)
	      except:
		pass
	      else:
		totalElf+=1
	        if absElf.canary:
		  canaryNum+=1	

        status,output=commands.getstatusoutput('rm -rf temp')
	log.write('Remove temporary directory: '+str(status)+'\n')
        status,output=commands.getstatusoutput('rm -f '+f)
	log.write('Remove package: '+str(status)+'\n\n')
	break
  
  line=avail.readline()
  #if totalNum>10:
  #  break;

avail.close()

log.write('Total number of packages: '+str(totalNum)+'\n')
log.write('Total number of elf: '+str(totalElf)+'\n')
log.write('Total number of canary: '+str(canaryNum)+'\n')
log.write('Percentage of canary: '+str(canaryNum/totalElf)+'\n')

log.close()
