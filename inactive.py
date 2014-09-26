#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script relevant les sysops absents depuis un temps donné

# (C) Linedwell, 2011-2014
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html


import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot
import time

# Déclarations
site = pywikibot.getSite('fr','vikidia')
nbrModif = 0
nbrTotal = 0


def getInactiveSysops(duration):
    
    inactiveSysops = []
    
    sysopList = site.allusers(group="sysop")

    for sysop in sysopList:
        uc = site.usercontribs(user=sysop[u'name'])

    for c in uc:
        print c[u'timestamp']
        break


#Exécution
def main():
    timeStart = time.time()
    getInactiveSysops(0)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
