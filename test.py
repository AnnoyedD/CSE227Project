from __future__ import division
import os
import os.path
import commands
import struct
import sys
#from pwn import pwnlib

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

def analysis(repo):
  pkgInfo='avail_'+repo+'.txt'
  logFile='ubuntu15_04_'+repo+'.log'

  log=open(logFile,'w')

  status,output=commands.getstatusoutput('mv /etc/apt/sources_'+repo+'.list /etc/apt/sources.list')
  log.write('Update repo list: '+str(status)+'\n\n')
  print 'Update repo list: ',status

  status,output=commands.getstatusoutput('apt-get update')
  log.write('Packages update: '+str(status)+'\n\n')
  print 'Packages updata: ',status

  status,output=commands.getstatusoutput('apt-cache dumpavail > '+pkgInfo)
  log.write('Dump available packakges: '+str(status)+'\n\n')
  print 'Dump available packages: ',status

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
      print 'Package: ',sName

      status,output=commands.getstatusoutput('apt-get download '+sName)
      log.write('Download package: '+str(status)+'\n')
      print 'Download package: ',status
    
      curDir=os.getcwd()
      fileList=os.listdir(curDir)

      for f in fileList:
        if f.find('.deb')!=-1:
          status,output=commands.getstatusoutput('dpkg-deb -x '+f+' temp')
          log.write('Decompress package: '+str(status)+'\n')
          print 'Decompress package: ',status

          for root,dirs,files in os.walk(curDir+'/temp'):
            for name in files:
              fileName=root+'/'+name

              if isElf(fileName):
                totalElf += 1
                status,output = commands.getstatusoutput('readelf -s '+fileName+' | grep \'__stack_chk_fail\'')
                if status==0 and output:
		  canaryNum += 1

             # if os.access(fileName,os.X_OK):
             #   try:
             #     absElf=pwnlib.elf.ELF(fileName)
             #   except:
             #     pass
             #   else:
             #     totalElf+=1
             #     if absElf.canary:
             #       canaryNum+=1  

          status,output=commands.getstatusoutput('rm -rf temp')
          log.write('Remove temporary directory: '+str(status)+'\n')
          print 'Remove temporary directory: ',status
          status,output=commands.getstatusoutput('rm -f '+f)
          log.write('Remove package: '+str(status)+'\n')
          print 'Remove package: ',status
          #for further analysis
          log.write('Total number of packages: '+str(totalNum)+'\n')
          log.write('Total number of elf: '+str(totalElf)+'\n')
          log.write('Total number of canary: '+str(canaryNum)+'\n\n')
          print 'Total number of packages: ',totalNum
          print 'Total numver of elf: ',totalElf
          print 'Total number of canary: ', canaryNum
          break
      
    line=avail.readline()
    #if totalNum>0:
    #  break;

  avail.close()
  
  log.write('==============================================================\n')
  log.write('Total number of packages: '+str(totalNum)+'\n')
  log.write('Total number of elf: '+str(totalElf)+'\n')
  log.write('Total number of canary: '+str(canaryNum)+'\n')
  log.write('Percentage of canary: '+str(canaryNum/totalElf)+'\n\n')

  status,output=commands.getstatusoutput('mv /etc/apt/sources.list /etc/apt/sources_'+repo+'.list')
  log.write('Rename repo list: '+str(status)+'\n')
  print 'Rename repo list: ',status

  log.close()

#use different repositories
analysis('main')
analysis('restricted')
analysis('universe')
analysis('multiverse')
