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

def pkgURL_shuffle(release,log):
  sList = [['http://ftp.us.debian.org/debian/',''],
	   ['http://security.debian.org/','/updates'],
 	   ['http://ftp.us.debian.org/debian/','-updates']]

  pkgURL=[]
  pkgNum=0
  
  for i in range(3):
    pkgInfoURL=sList[i][0]+'dists/'+release+sList[i][1]+'/main/binary-amd64/Packages.gz'
    status,output=commands.getstatusoutput('wget '+pkgInfoURL)
    log.write('Download package info: '+str(status)+'\n')
    print 'Download package info: ',status
 
    status,output=commands.getstatusoutput('gunzip Packages.gz')
    log.write('Decompress package info: '+str(status)+'\n')
    print 'Decompress package info: ',status

    pkgInfo=open('Packages')
  
    line=pkgInfo.readline()
    while line:
      length=len(line)
      if length>=10 and 'Filename: '==line[:10]:
        pkgNum+=1

        URL=sList[i][0]+line[9:length].strip()
        pkgURL.append(URL)

      line=pkgInfo.readline()

    pkgInfo.close()

    status,output=commands.getstatusoutput('rm -f Packages')
    log.write('Delete package info: '+str(status)+'\n')
    print 'Delete package info: ',status

  x=[i for i in range(pkgNum)]
  shuffle(x)
  shuffle(x)
  shuffle(x)
  shf=[pkgURL[i] for i in x]

  log.write('Shuffled package: '+str(pkgNum)+'\n\n')
  print 'Shuffled package: ',pkgNum

  return pkgNum,shf

def analysis(release,sample):
  log=open('debian.log','w')
 
  pkgNum,pkgURL=pkgURL_shuffle(release,log)
  if sample>pkgNum:
    sample=pkgNum
  
  totalElf=0
  canaryNum=0
  for i in range(sample):
      URL=pkgURL[i]
      log.write('Pkg URL: '+str(URL))
      print 'Pkg URL: ',URL

      status,output=commands.getstatusoutput('wget '+URL)
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
  log.write('Total number of sample: '+str(sample)+'\n')
  log.write('Total number of elf: '+str(totalElf)+'\n')
  log.write('Total number of canary: '+str(canaryNum)+'\n')
  if totalElf>0:
    log.write('Percentage of canary: '+str(canaryNum/totalElf)+'\n\n')

  log.close()

#read number of samples
sample=int(raw_input('Enter sample number: '))

analysis('jessie',sample)
