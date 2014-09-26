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

month = [u'',u'janvier',u'février',u'mars',u'avril',u'mai',u'juin',u'juillet',u'août',u'septembre',u'octobre',u'novembre',u'décembre']

def getInactiveSysops(limit):
    
    inactiveSysops = []
    
    sysopList = site.allusers(group="sysop")

    for sysop in sysopList:
        sysopName = sysop[u'name']
        uc = site.usercontribs(user=sysopName)

        for c in uc:
            lastEdit = datetime.strptime(c[u'timestamp'],"%Y-%m-%dT%H:%M:%SZ")
            duration = calcDuration(lastEdit)
            if lastEdit < limit:
                hrdate = u"" + str(lastEdit.day) + " " + month[int(lastEdit.month)] + " " + str(lastEdit.year)
                print hrdate
                inactiveSysops.append(u"{{u|" + sysopName + u"}} : inactif depuis le " + hrdate + u" (" + str(duration.days) + u" jours)")
            break

    return inactiveSysops

def reportInactiveSysops(list):
    
    if len(list) > 0:
        
        currentYear = datetime.utcnow().year

        report = u"\n\n== Administrateurs inactifs depuis au moins un an ==\n\n"

        for s in list:
            report += s + "\n"
        
        page = pywikibot.Page(site,u"Vikidia:Demandes aux bureaucrates/" + str(currentYear))
        page.text = page.text + report
        summary = "[[VD:Robot|Robot]] : Administrateurs inactifs"

        print page.text


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
    limit = calcLimit(50)
    inactiveSysops = getInactiveSysops(limit)
    reportInactiveSysops(inactiveSysops)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
