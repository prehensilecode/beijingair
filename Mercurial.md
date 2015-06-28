# Introduction #
  * See the tutorial at http://hginit.com/
  * For quick reference: http://hgbook.red-bean.com/read/mercurial-in-daily-use.html

# Central Repository #
  * Our central repository will be at Google Code:
> > https://beijingair.googlecode.com/hg/
  * Some explanation about the central repo at http://hginit.com/02.html
  * The username is just your Google name without "@gmail.com"
  * The password is different from your Google password: set it at https://code.google.com/hosting/settings?

# Preparation #
  * There needs to be some Python libraries installed
```
        easy_install-2.5 ssl
```

# Basic Use #
  * First, make a local clone of the repository:
```
       mkdir ~/Projects
       cd ~/Projects
       hg clone https://beijingair.googlecode.com/hg/ beijingair
       cd beijingair
```
  * Get updates from the repository
```
       hg pull
```
  * Make changes
  * Commit changes
```
       hg commit 
```
  * Push changes to the repository
```
       hg push
```

# Default Configuration #
  * Edit `~/.hgrc` and add the following (where "username" is your Google username)
```
       [ui]
       username = First Last <myusername@gmail.com>
       verbose = True

       [auth]
       beijingair.prefix = https://beijingair.googlecode.com/hg
       beijingair.username = username
       beijingair.password = XXXXXX
```
  * The password is different from your Google password: https://code.google.com/hosting/settings?