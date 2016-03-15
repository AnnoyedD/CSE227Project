from canary_analysis import *

#read number of samples
sample=int(raw_input('Enter sample number: '))
os_and_version=raw_input('Enter OS and Version(eg. Ubuntu-15.04): ')

#use different repositories
analysis('main',sample, os_and_version)
analysis('restricted',sample, os_and_version)
analysis('universe',sample, os_and_version)
analysis('multiverse',sample, os_and_version)
