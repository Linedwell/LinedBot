#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script XXXX

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
site = pywikibot.Site('fr','wikipedia')
nbrModif = 0
nbrTotal = 0


# Récupère la liste des éditions du compte ciblé au cours du délai donné
def getRecentEdits(userName):
    recentEdits = site.usercontribs(user=userName,top_only=True,end="2014-12-15T00:00:00Z")
    
    for edit in recentEdits:
        print edit

    print len(list(recentEdits))

# Exécution
def main():
    timeStart = time.time()
    user = u'Linedwell'
    getRecentEdits(user)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
