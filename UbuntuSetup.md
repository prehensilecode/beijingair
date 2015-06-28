# Introduction #

  1. Virtual Box + Ubuntu
  1. Dev packages for Ubuntu
  1. Python 2.7.x
  1. Google App Engine dev kit
  1. (Optional) Eclipse IDE

The most tedious part will be getting Python 2.5 running on Ubuntu. The current Python version is 2.6, and that's what comes with Ubuntu. Google App Engine, however, wants Python 2.5, which means compiling it yourself. That's not terrible except that Ubuntu Desktop really isn't set up to be a development environment: so you have to chase down all the dev packages in order that the Python you compile will be complete.

# Virtual Box + Ubuntu #
  * [Download VirtualBox](http://www.virtualbox.org/)
  * [Download Ubuntu CDROM image](http://www.ubuntulinux.org/) (Desktop version, 64-bit)
  * [Create a virtual machine (VM) for running Ubuntu](http://www.virtualbox.org/manual/ch01.html#gui-createvm)
    * Make it a 32-bit machine, of course
    * 512 MB RAM should be enough
    * 6 GB disk should be enough, though I tend to use between 8 GB and 10 GB
    * Under [System Settings - Motherboard tab](http://www.virtualbox.org/manual/ch03.html#settings-motherboard), set "Hardware clock in UTC time"
    * For networking, use a ["Bridged" network](http://www.virtualbox.org/manual/ch06.html#id2533733) connector; for the [virtual networking hardware](http://www.virtualbox.org/manual/ch06.html#nichardware), pick "virtio"
    * Under Virtual Box's [Virtual Media Manager](http://www.virtualbox.org/manual/ch05.html#vdis), add the Ubuntu ISO that you downloaded under the "CD/DVD Images" tab
    * Then, under [Storage Settings](http://www.virtualbox.org/manual/ch03.html#settings-storage) for the VM you created, add the CD image so that it will boot off it when you start
  * Start up the VM, and it should boot off the CD image; Install Ubuntu following instructions. Use the whole disk.
  * On first login, run the updater: on the main menu bar (it's a "GNOME panel"), go to System -> Administration -> Update Manager. You'll probably have to reboot
  * Then, one final thing to have Virtual Box compatibility (you'll probably have to do this every time the Ubuntu kernel is updated, and/or Virtual Box is updated):
    * In the VM window, Devices -> [Install Guest Additions...](http://www.virtualbox.org/manual/ch04.html)
    * Usually, this will automatically mount the CD image containing the Virtual Box guest additions software in Ubuntu: the image will appear on the desktop
    * However, it hasn't been doing that automatically for me; so, just mount it manually for the moment, using the terminal. And execute the installation script:
```
         $ sudo mkdir /mnt/cdrom
         $ sudo mount -t iso9660 -o ro /dev/cdrom /mnt/cdrom
         $ cd /mnt/cdrom
         $ sudo ./VBoxLinuxAdditions-x86.run
         ...
         $ cd
         $ sudo umount /mnt/cdrom
```
    * You should reboot after that. Once you do so, you will notice that you can resize the VM window, and the display matches the window size. Also, you won't have mouse pointer issues.
    * And a final tweak: You'll notice the desktop is empty, not even a trashcan (it's in the bottom menubar/panel).
      * Open a terminal (Applications -> Accessories -> Terminal), and run gconf-editor.
      * Go to: apps -> nautilus -> desktop and check on "home\_icon\_visible", "trash\_icon\_visible" and whatever else you want to appear on the desktop.
  * And, [some tips](http://www.virtualbox.org/manual/ch01.html#id2511923) on using Virtual Box snapshots to retain the state of the VM when you shut it down. In short, close the VM, and choose "Save the machine state"

# Dev Packages for Ubuntu #
Use the Synaptic Package Manager (under System -> Administration) to install.

The following are for building Python.

  * libreadline-dev
  * tcl-dev
  * libgdbm-dev
  * db4.8-util
  * libdb-dev
  * libssl-dev
  * zlib1g-dev
  * libjpeg62-dev
  * libbz2-dev
  * sqlite3
  * sqlite3-doc
  * libsqlite3-dev

The following are the mercurial packages for working with the Google Code repository.

  * mercurial
  * gquilt
  * hgview
  * tortoisehg-mercurial
  * meld

# Python 2.5.5 #
See PythonSetup

# Google App Engine dev kit #
  * Follow the [sign up link](http://code.google.com/appengine/), and connect your Google account to an App Engine account
  * Download the [Google App Engine SDK (Software Development Kit) for Python](http://code.google.com/appengine/downloads.html) - it's called something like `google_appengine.1.3.4.zip`
  * Put in `/opt`: `mv google_appengine.1.3.4.zip /opt`
  * Expand it:
```
       $ cd /opt
       $ unzip google_appengine.1.3.4.zip
```
  * That should give you a directory called `google_appengine`
  * In your .bashrc or .tcshrc, add the `google_appengine` directory to your path (use the fully-qualified path, i.e. export PATH=/opt/google\_appengine:${PATH}

# Eclipse IDE (optional) #
  * Download from http://www.eclipse.org
  * Install the PyDev module: http://pydev.org/
  * Install the Mercurial module: http://javaforge.com/project/HGE
  * Install the Google App Engine module: http://code.google.com/appengine/downloads.html#Download_the_Google_Plugin_for_Eclipse