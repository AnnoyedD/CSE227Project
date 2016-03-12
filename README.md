# CSE227Project

### Configure
  * pkgInfo: available packages and details
  * logFile: log

### Repository:
  Package list is defined in /etc/apt/sources.list /etc/apt/sources.list.d. 
  Usually /etc/apt/sources.list defines four repositories main, restricted, unive  rse, multiverse. Each repository is defined as several URLs, for example 
  
  deb http://us.archive.ubuntu.com/ubuntu vivid main 
  
  "vivid" defines the release and "main" defines the repositories.
  We want to distinguish the four repositories so we store the four repositories   into four files and the script will automatically read the different repositori  es.  
  To do (root privilege):
  
  <pre><code>
    cd /etc/apt
    cp sources.list sources.backup //backup
    cp sources.list sources_main.list
    cp sources.list sources_restricted.list
    cp sources.list sources_universe.list
    cp sources.list sources_multiverse.list
    rm sources.list
  </code></pre>  
  For each sources_xxx.list, delete all URLs not relevant to the current file's    repositories. For examle, in sources_universe.list, there are only URLs defin    ing "universe" and all other URLs should be deleted.  

### Run

  <pre><code>
  root privilege 
  python test.py
  </code></pre>  
  
