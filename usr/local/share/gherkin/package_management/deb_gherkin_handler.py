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
                package = apt.debfile.DebPackage( folder + debfile )
                package.install()

def remove_packages( packages ):
    cache = apt.Cache()
    for package in packages:
        pkg = cache[ package ]
        pkg.mark_delete( auto_fix = True, purge = True )
    cache.commit()
