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

#Retourne la liste des administrateurs ainsi que la date de leur dernière contribution
def getSysopsLastEdit():
    
    sysopList = site.allusers(group="sysop")
    sysopLastEdit = {}

    for sysop in sysopList:
        sysopName = sysop[u'name']
        uc = site.usercontribs(user=sysopName)

        for c in uc:
            lastEdit = datetime.strptime(c[u'timestamp'],"%Y-%m-%dT%H:%M:%SZ")
            sysopLastEdit[sysopName] = lastEdit
            break

    return sysopLastEdit

#Retourne la liste des administrateurs inactifs depuis <hardlimit>, notifie ceux inactifs depuis <softlimit>
def getInactiveSysops(list, hardlimit, softlimit):
    
    inactiveSysops = []

    for sysop in sorted(list.iterkeys()):
        lastEdit = list[sysop]
        duration = calcDuration(lastEdit)
        hrdate = u"%s %s %s (%s jours)" %(lastEdit.day,month[int(lastEdit.month)],lastEdit.year,duration.days)
        
        if lastEdit < hardlimit:
            inactiveSysops.append(u"* {{u|" + sysop + u"}} : inactif depuis le " + hrdate)
        elif lastEdit < softlimit:
            deadline = lastEdit + timedelta(days=365)
            hrdeadline = u"%s %s %s" %(deadline.day,month[int(deadline.month)],deadline.year)
            notifySysop(sysop,hrdate,hrdeadline)

    return inactiveSysops

#Notifie un admin ayant presque atteint le seuil d'inactivité de la possible suspension de ses outils
def notifySysop(sysop,hrdate,hrdeadline):
    notif = u"\n\n{{subst:Utilisateur:LinedBot/NotifAdminInactif|hrdate|hrdeadline}}\n"

    page = pywikibot.Page(site,u"Discussion utilisateur:"+sysop)
    page.text = page.text + notif
    
    summary = "[[VD:Robot|Robot]] : Notification de prochaine suspension des outils"

    page.save(summary,minor=False)


#Envoie sur VD:DB la liste des administrateurs inactifs ainsi que la durée de leur inactivité
def reportInactiveSysops(list):
    
    if len(list) > 0:
        
        currentYear = datetime.utcnow().year

        report = u"\n\n== Administrateurs inactifs depuis au moins un an ==\n\n"

        for s in list:
            report += s + "\n"
        
        page = pywikibot.Page(site,u"Vikidia:Demandes aux bureaucrates/" + str(currentYear))
        page.text = page.text + report
        summary = "[[VD:Robot|Robot]] : Liste des administrateurs inactifs depuis au moins un an"

        page.save(summary,minor=False)


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
    hardlimit = calcLimit(365) #Seuil pour lequel le retrait des outils sera demandé
    softlimit = calcLimit(300) #Seuil pour lequel une notification sera envoyée à l'admin
    
    sysopLastEdit = getSysopsLastEdit()
    inactiveSysops = getInactiveSysops(sysopLastEdit,hardlimit,softlimit)
    
    print inactiveSysops
    reportInactiveSysops(inactiveSysops)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
