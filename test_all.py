from canary_analysis import *

#read number of samples
sample=int(raw_input('Enter sample number: '))
os_and_version=raw_input('Enter OS and Version(eg. Ubuntu-15.04): ')

#use different repositories
analysis('all',sample, os_and_version)
