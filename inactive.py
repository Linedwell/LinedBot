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

import time
from datetime import date, datetime, timedelta

import pywikibot

# Déclarations
site = pywikibot.getSite('fr','vikidia')
nbrModif = 0
nbrTotal = 0


def getInactiveSysops(limit):
    
    inactiveSysops = []
    
    sysopList = site.allusers(group="sysop")

    for sysop in sysopList:
        sysopName = sysop[u'name']
        uc = site.usercontribs(user=sysopName)

        for c in uc:
            lastEdit = datetime.strptime(c[u'timestamp'],"%Y-%m-%dT%H:%M:%SZ")
            if lastEdit < limit:
                inactiveSysops.append(u"{{u|"+ sysopName + "}} : inactif depuis le " + str(lastEdit))
            break

    print inactiveSysops



#Retourne la date avant laquelle on considère obsolète l'usage du modèle
def calcLimit(delay):
    today = datetime.utcnow()
    limite = today - timedelta(days=delay)
    return limite

#Retourne le temps écoulé entre une date et le jour courant
def calcDuration(date):
    today = datetime.utcnow()
    duration = today - date
    return duration


#Exécution
def main():
    timeStart = time.time()
    limit = calcLimit(1)
    getInactiveSysops(limit)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
