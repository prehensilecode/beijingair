# Python 2.5.5 Setup #

After all required Ubuntu devel packages are installed (UbuntuSetup), we should be ready to compile and install Python 2.5.5. We will install in `/opt` to avoid clashing with the default Python installation.

## Compiling ##
  * First, create the appropriate directories:
```
       $ sudo mkdir /opt
       $ sudo chown $USER /opt
       $ mkdir /opt/src
```
  * Get the source tarball from [the download page](http://www.python.org/download/releases/2.5.5/). Then, move it to `/opt/src`
  * Expand the archive:
```
       $ cd /opt/src
       $ tar zxf Python-2.5.5.tgz
```
  * configure, compile, test (and check for errors/warnings), install:
```
       $ cd Python-2.5.5
       $ ./configure --prefix=/opt
       $ make >& Make.out &            # you can see the output from make in Make.out
       $ make test >& Make.test.out &
```
  * Have a look at `Make.test.out`. You should see complaints about two modules which it it expected to find, but were not there: `dbm`, and `bsddb`. It's safe to ignore those. If there are any others, it may be a bit of a chore to track down.
  * If `Make.test.out` looks OK, install Python 2.5.5:
```
       $ make install >& Make.install.out &
```
  * That should install the `python` interpreter as `/opt/bin/python2.5` and `/opt/bin/python`. The libraries, etc. will be in `/opt/lib/python2.5/`. You can check `Make.install.out` for the gory details of where every single file was installed.
  * Now, you have to modify your `PATH` so that it picks up the python that was just installed. This depends on your shell. Default Ubuntu shell is `bash` unless you changed it. Edit `~/.bashrc` and add the following somewhere near the top of the file:
```
       export PATH=/opt/bin:/opt/sbin:${PATH}
```
  * To test it:
```
       $ . ~/.bashrc
       $ which python2.5
       /opt/bin/python2.5       # expected answer
```

## Other Libraries ##

### Little CMS (lcms) ###
  * Prerequisites - Ubuntu dev packags
    * libtiff4-dev
  * [Little CMS site](http://www.littlecms.com/)
  * Color management for images; prerequisite for PIL (below)
  * Download from Sourceforge:  http://sourceforge.net/projects/lcms/files/
    * get lcms2-2.0a.tar.gz
    * put in `/opt/src`
  * Expand, configure, compile:
```
       $ cd /opt/src
       $ tar zxf lcms2-2.0a.tar.gz
       $ cd lcms2-2.0a
       $ ./configure --prefix=/opt
       $ make >& Make.out &
       $ tail -f Make.out         # use Ctrl-C to stop following the file
       $ make check >& Make.check.out &
       $ make install >& Make.install.out &
```

### SSL ###
  * This is required for connecting to Google's hosting server
  * The easy\_install method doesn't work, so you'll have to do the download and install as with lcms
  * Download from: http://pypi.python.org/pypi/ssl/1.15#downloads
    * get ssl-1.15.tar.gz
    * put in `/opt/src`
  * Expand, install:
```
        $ cd /opt/src
        $ tar zxf ssl-1.15.tar.gz
        $ cd ssl-1.15
        $ python2.5 setup.py install
```

### Python Imaging Library (PIL) ###
  * Download here: http://effbot.org/downloads/Imaging-1.1.7.tar.gz