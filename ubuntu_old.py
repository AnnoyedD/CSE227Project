from __future__ import division
import os
import os.path
import commands
import struct
import sys
#from random import shuffle
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

def get_pkgURL(release,repo,log):
  rootDir = 'http://old-releases.ubuntu.com/ubuntu/' 
  subDir = [release+'/',
	    release+'-backports/',
	    release+'-proposed/',
	    release+'-security/',
	    release+'-updates/']

  pkgURL=[]
  pkgNum=0
  
  for i in range(5):
    pkgInfoURL=rootDir+'dists/'+subDir[i]+repo+'/binary-amd64/Packages.gz'
    status,output=commands.getstatusoutput('wget '+pkgInfoURL)
    log.write('Download package info of '+subDir[i]+': '+str(status)+'\n')
    print 'Download package info of ',subDir[i],': ',status
 
    status,output=commands.getstatusoutput('gunzip Packages.gz')
    log.write('Decompress package info of '+subDir[i]+': '+str(status)+'\n')
    print 'Decompress package info of ',subDir[i],': ',status

    pkgInfo=open('Packages')
  
    line=pkgInfo.readline()
    while line:
      length=len(line)
      if length>=10 and 'Filename: '==line[:10]:
        pkgNum+=1

        URL=rootDir+line[9:length].strip()
        pkgURL.append(URL)

      line=pkgInfo.readline()

    pkgInfo.close()

    status,output=commands.getstatusoutput('rm -f Packages')
    log.write('Delete package info: '+str(status)+'\n')
    print 'Delete package info: ',status

  return pkgNum,pkgURL

def analysis(release,repo):
  log=open('ubuntu_'+release+'_'+repo+'.log','w')
 
  pkgNum,pkgURL=get_pkgURL(release,repo,log)

  log.write('Total number of packages: '+str(pkgNum)+'\n\n')
  print 'Total number of packages: ',pkgNum
  
  totalElf=0
  canaryNum=0
  failNum=0
  for i in range(1):
      URL=pkgURL[i]
      log.write('Pkg URL: '+str(URL)+'\n')
      print 'Pkg URL: ',URL

      status,output=commands.getstatusoutput('wget '+URL)

      if status!=0:
	failNum+=1
	continue

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
          log.write('Total number of packages: '+str(i+1-failNum)+'\n')
          log.write('Total number of elf: '+str(totalElf)+'\n')
          log.write('Total number of canary: '+str(canaryNum)+'\n\n')
          print 'Total number of packages: ',i+1-failNum
          print 'Total numver of elf: ',totalElf
          print 'Total number of canary: ', canaryNum
          break
      
  log.write('\n==============================================================\n')
  log.write('Total number of packages: '+str(pkgNum-failNum)+'\n')
  log.write('Total number of failed packages: '+str(failNum)+'\n')
  log.write('Total number of elf: '+str(totalElf)+'\n')
  log.write('Total number of canary: '+str(canaryNum)+'\n')
  if totalElf>0:
    log.write('Percentage of canary: '+str(canaryNum/totalElf)+'\n')

  log.close()

#read release name
release=raw_input('Enter release name: ')

analysis(release,'main')
analysis(release,'restricted')
analysis(release,'universe')
analysis(release,'multiverse')
