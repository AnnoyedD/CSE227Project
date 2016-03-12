dir = '/etc/apt/'
original_file_name = 'source.list'

main_file_name = 'sources_main.list'
restricted_file_name = 'sources_restricted.list'
universe_file_name = 'sources_universe.list'
multiverse_file_name = 'sources_multiverse.list'

main_file = open(dir+main_file_name, 'w+')
restricted_file = open(dir+restricted_file_name, 'w+')
universe_file = open(dir+universe_file_name, 'w+')
multiverse_file = open(dir+multiverse_file_name, 'w+')

with original_file as open(dir+original_file_name):
    for line in original_file:
        if 'main' in line:
            main_file.write(line)
        if 'restricted' in line:
            restricted_file.write(line)        
        if 'universe' in line:
            universe_file.write(line)
        if 'multiverse' in line:
            multiverse_file.write(line)
