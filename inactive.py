#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script relevant les sysops absents depuis un temps donné

# (C) Linedwell, 2011-2016
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
dico = ''
currentYear = datetime.utcnow().year
currentMonth = datetime.utcnow().month

dicoFR = {
    'site' : pywikibot.Site('fr','vikidia'),
    'page' : u"Vikidia:Demandes aux bureaucrates/%s" % str(currentYear),
    'month' : [u'',u'janvier',u'février',u'mars',u'avril',u'mai',u'juin',u'juillet',u'août',u'septembre',u'octobre',u'novembre',u'décembre'],
    'days' : u"jours",
    'since' : u" inactif depuis le ",
    'template' : u"\n\n{{subst:Utilisateur:LinedBot/NotifAdminInactif|%s|%s}}\n",
    'section' : u"\n\n== Administrateurs inactifs depuis au moins un an ==\n\n",
    'notifsummary' : "[[VD:Robot|Robot]] : Notification de prochaine suspension des outils",
    'reportsummary' : "[[VD:Robot|Robot]] : Liste des administrateurs inactifs depuis au moins un an",
    'hard' : 365,
    'soft' : 300,
}

itmonth = [u'',u'gennaio',u'febbraio',u'marzo',u'aprile',u'maggio',u'giugno',u'luglio',u'agosto',u'settembre',u'ottobre',u'novembre',u'dicembre']

dicoIT = {
    'site' : pywikibot.Site('it','vikidia'),
    'page' : u"Vikidia:Richieste agli amministratori/%s %s" % (str(itmonth[currentMonth]), str(currentYear)),
    'month' : [u'',u'gennaio',u'febbraio',u'marzo',u'aprile',u'maggio',u'giugno',u'luglio',u'agosto',u'settembre',u'ottobre',u'novembre',u'dicembre'],
    'days' : u"giorni",
    'since' : u" inattivo dal ",
    'template' : u"\n\n{{subst:Utilisateur:LinedBot/NotifAdminInactif|%s|%s}}\n",
    'section' : u"\n\n== Amministratori inattivi da al meno un anno ==\n\n",
    'notifsummary' : "[[VD:Bot|Bot]] : Notifica di sospensione prossima degli strumenti di amministratore",
    'reportsummary' : "[[VD:Bot|Bot]] : Lista dei amministratori inattivi da più di un anno",
    'hard' : 365,
    'soft' : 300,
}

#BUGFIX
#site.login()
#END OF FIX

#Retourne la liste des administrateurs ainsi que la date de leur dernière contribution
def getSysopsLastEdit():
    site = dico['site']
    sysopList = site.allusers(group="sysop")
    sysopLastEdit = {}

    for sysop in sysopList:
        sysopName = sysop[u'name']
        uc = site.usercontribs(user=sysopName,total=1)

        for c in uc:
            lastEdit = datetime.strptime(c[u'timestamp'],"%Y-%m-%dT%H:%M:%SZ")
            sysopLastEdit[sysopName] = lastEdit
            break

    return sysopLastEdit

#Retourne la liste des administrateurs inactifs depuis <hardlimit>, notifie ceux inactifs depuis <softlimit>
def getInactiveSysops(list):
    hardlimit = calcLimit(dico['hard'])
    softlimit = calcLimit(dico['soft'])
    inactiveSysops = []

    for sysop in sorted(list.iterkeys()):
        lastEdit = list[sysop]
        duration = calcDuration(lastEdit)
        print "%s : %s" %(sysop,str(duration))
        hrdate = u"%s %s %s (%s %s)" %(lastEdit.day,dico['month'][int(lastEdit.month)],lastEdit.year,duration.days,dico['days'])
        
        if lastEdit < hardlimit:
            inactiveSysops.append(u"* {{u|" + sysop + u"}} : " + dico['since'] + hrdate)
        elif lastEdit < softlimit:
            deadline = lastEdit + timedelta(days=365)
            hrdeadline = u"%s %s %s" %(deadline.day,dico['month'][int(deadline.month)],deadline.year)
            notifySysop(sysop,hrdate,hrdeadline)

    return inactiveSysops

#Notifie un admin ayant presque atteint le seuil d'inactivité de la possible suspension de ses outils
def notifySysop(sysop,hrdate,hrdeadline):
    notif = dico['template'] %(hrdate,hrdeadline)
    site = dico['site']
    page = pywikibot.Page(site,u"User talk:"+sysop)
    
    if page.userName() == site.user():
        print u"%s already warned; skipping." % page.title(asLink=True)
    
    else:
        summary = dico['notifsummary']
        print page.text + notif
        #page.text = page.text + notif
        #page.save(summary,minor=False)


#Envoie sur VD:DB la liste des administrateurs inactifs ainsi que la durée de leur inactivité
def reportInactiveSysops(list):
    
    if len(list) > 0:
        report = dico['section']

        for s in list:
            report += s + "\n"
        
        page = pywikibot.Page(dico['site'],dico['page'])
        page.text = page.text + report
        summary = dico['reportsummary']
        
        page.save(summary,minor=False,botflag=False)


#Lanceur principal
def inactiveSysopsManager(loc):
    global dico
    dico = loc
    sysopLastEdit = getSysopsLastEdit()
    inactiveSysops = getInactiveSysops(sysopLastEdit)
    reportInactiveSysops(inactiveSysops)


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
    inactiveSysopsManager(dicoFR)
    #inactiveSysopsManager(dicoIT)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
