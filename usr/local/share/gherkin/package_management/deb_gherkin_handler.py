#!/usr/bin/env python

import os
import apt.debfile
import apt
import subprocess

def install_packages( folders ):
    for folder in folders:
        if not folder.endswith( '/' ):
            folder = folder + '/'
        for debfile in os.listdir( folder ):
            if debfile.endswith( ".deb" ):
                subprocess.call(["dpkg","-i",debfile])

def remove_packages( packages ):
    cache = apt.Cache()
    for package in packages:
        subprocess.call(["dpkg","--purge",package])
    cache.commit()
