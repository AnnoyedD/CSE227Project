directory = '/etc/apt/'
original_file_name = 'source.list'

main_file_name = 'sources_main.list'
restricted_file_name = 'sources_restricted.list'
universe_file_name = 'sources_universe.list'
multiverse_file_name = 'sources_multiverse.list'

main_file = open(directory+main_file_name, 'w')
restricted_file = open(directory+restricted_file_name, 'w')
universe_file = open(directory+universe_file_name, 'w')
multiverse_file = open(directory+multiverse_file_name, 'w')
original_file = open(directory+original_file_name)

for line in original_file:
    if 'main' in line:
        main_file.write(line.replace('restricted','').replace('universe','').replace('multiverse',''))
    if 'restricted' in line:
        restricted_file.write(line.replace('main','').replace('universe','').replace('multiverse',''))        
    if 'universe' in line:
        universe_file.write(line.replace('main','').replace('restricted','').replace('multiverse',''))
    if 'multiverse' in line:
        multiverse_file.write(line.replace('main','').replace('restricted','').replace('universe',''))
