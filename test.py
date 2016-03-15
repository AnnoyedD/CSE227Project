from __future__ import division
import os
import os.path
import commands
import struct
import sys
from random import shuffle
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

def get_pkginfo(repo,log): 
  pkgInfo='avail_'+repo+'.txt'

  status,output=commands.getstatusoutput('mv /etc/apt/sources_'+repo+'.list /etc/apt/sources.list')
  log.write('Update repo list: '+str(status)+'\n\n')
  print 'Update repo list: ',status

  status,output=commands.getstatusoutput('apt-get update')
  log.write('Packages update: '+str(status)+'\n\n')
  print 'Packages update: ',status

  status,output=commands.getstatusoutput('apt-cache dumpavail > '+pkgInfo)
  log.write('Dump available packakges: '+str(status)+'\n\n')
  print 'Dump available packages: ',status

def shuffle_pkg(repo,log):
  avail=open('avail_'+repo+'.txt','r')
  package=[]
  pkgNum=0

  line=avail.readline()
  while line:
    length=len(line)
    if length>=9 and 'Package: '==line[:9]:
      pkgNum+=1

      sName=line[9:length].strip()
      package.append(sName)

    line=avail.readline()

  avail.close()

  x=[i for i in range(pkgNum)]
  shuffle(x)
  shuffle(x)
  shuffle(x)
  shf=[package[i] for i in x]

  log.write('Shuffled package: '+str(pkgNum)+'\n\n')
  print 'Shuffled package: ',pkgNum

  return pkgNum,shf

def analysis(repo,sample):
  log=open('ubuntu15_04_'+repo+'.log','w')

  get_pkginfo(repo,log) 
  pkgNum,pkg=shuffle_pkg(repo,log)
  
  if sample>pkgNum:
    sample=pkgNum
  
  totalElf=0
  canaryNum=0
  for i in range(sample):
      pkgName=pkg[i]
      log.write('Package: '+str(pkgName))
      print 'Package: ',pkgName

      status,output=commands.getstatusoutput('apt-get download '+pkgName)
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

          status,output=commands.getstatusoutput('rm -rf temp')
          log.write('Remove temporary directory: '+str(status)+'\n')
          print 'Remove temporary directory: ',status
          status,output=commands.getstatusoutput('rm -f '+f)
          log.write('Remove package: '+str(status)+'\n')
          print 'Remove package: ',status
          #for further analysis
          log.write('Total number of packages: '+str(i+1)+'\n')
          log.write('Total number of elf: '+str(totalElf)+'\n')
          log.write('Total number of canary: '+str(canaryNum)+'\n\n')
          print 'Total number of packages: ',i+1
          print 'Total numver of elf: ',totalElf
          print 'Total number of canary: ', canaryNum
          break
      
  log.write('\n==============================================================\n')
  log.write('Total number of sample: '+str(pkgNum)+'\n')
  log.write('Total number of elf: '+str(totalElf)+'\n')
  log.write('Total number of canary: '+str(canaryNum)+'\n')
  if totalElf>0:
    log.write('Percentage of canary: '+str(canaryNum/totalElf)+'\n\n')

  status,output=commands.getstatusoutput('mv /etc/apt/sources.list /etc/apt/sources_'+repo+'.list')
  log.write('Rename repo list: '+str(status)+'\n')
  print 'Rename repo list: ',status

  log.close()

#read number of samples
sample=int(raw_input('Enter sample number: '))

#use different repositories
analysis('main',sample)
analysis('restricted',sample)
analysis('universe',sample)
analysis('multiverse',sample)
