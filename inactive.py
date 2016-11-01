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

import logging
logging.basicConfig(filename='log/inactive.log', format='%(asctime)s :: %(levelname)s :: %(message)s', level=logging.INFO)

import time
from datetime import date, datetime, timedelta

import sqlite3

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
    'template' : u"\n\n{{subst:Utente:LinedBot/NotificaAdminInattivo|%s|%s}}\n",
    'section' : u"\n\n== Amministratori inattivi da al meno un anno ==\n\n",
    'notifsummary' : "[[Vikidia:Bot|Bot]] : Notifica di sospensione prossima degli strumenti di amministratore",
    'reportsummary' : "[[Vikidia:Bot|Bot]] : Lista dei amministratori inattivi da più di un anno",
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
            print "%s : %s" %(sysopName, calcDuration(lastEdit))
            break
    return sysopLastEdit

#Retourne la liste des administrateurs inactifs depuis <hardlimit>, notifie ceux inactifs depuis <softlimit>
def getInactiveSysops(list):
    hardlimit = calcLimit(dico['hard'])
    softlimit = calcLimit(dico['soft'])
    inactiveSysopsHard = []
    inactiveSysopsSoft = []

    for sysop in sorted(list.iterkeys()):
        lastEdit = list[sysop]
        if lastEdit < hardlimit:
            inactiveSysopsHard.append([sysop,lastEdit])
        elif lastEdit < softlimit:
            inactiveSysopsSoft.append([sysop,lastEdit])

    return inactiveSysopsHard, inactiveSysopsSoft

#Notifie la liste des admins ayant presque atteint le seuil d'inactivité de la possible suspension de leurs outils
def notifySysop(list):
    if len(list) > 0:
        site = dico['site']
        for i in list:
            sysop, lastEdit = i
            page = pywikibot.Page(site,u"User talk:"+sysop)
            status = db_check_status(sysop,lastEdit)
            if not status:
                duration = calcDuration(lastEdit)
                hrdate = u"%s %s %s (%s %s)" %(lastEdit.day,dico['month'][int(lastEdit.month)],lastEdit.year,duration.days,dico['days'])
                deadline = lastEdit + timedelta(days=dico['hard'])
                hrdeadline = u"%s %s %s" %(deadline.day,dico['month'][int(deadline.month)],deadline.year)
                notif = dico['template'] %(hrdate,hrdeadline)
            
                summary = dico['notifsummary']
                page.text = page.text + notif
                page.save(summary,minor=False)
                db_upsert_status(sysop,lastEdit,"N")
                
            else:
                print u"%s already notified; skipping." % page.title(asLink=True)



#Envoie sur VD:DB la liste des administrateurs inactifs ainsi que la durée de leur inactivité
def reportInactiveSysops(list):
    page = pywikibot.Page(dico['site'],dico['page'])
    
    if len(list) > 0:
        section = dico['section']
        report = ''

        for i in list:
            sysop, lastEdit = i
            status = db_check_status(sysop,lastEdit)
            
            # Si l'administrateur n'a pas déjà été reporté pour cette absence
            if not status or not status[0] == "R":
                db_upsert_status(sysop,lastEdit,"R")
                duration = calcDuration(lastEdit)
                hrdate = u"%s %s %s (%s %s)" %(lastEdit.day,dico['month'][int(lastEdit.month)],lastEdit.year,duration.days,dico['days'])
                report += u"* {{u|" + sysop + u"}} : " + dico['since'] + hrdate + "\n"
            else:
                print u"%s already reported; skipping." % sysop
        
        if len(report):
            page.text = page.text + section + report
            summary = dico['reportsummary']
            page.save(summary,minor=False,botflag=False)
        else:
            print u"Nobody to report."

# Vérifie si l'admin a déjà été notifié / signalé pour inactivité
def db_check_status(sysop, lastEdit):
    table = "inactive_%s" %dico['site'].lang
    conn = sqlite3.connect('db/inactive.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT status FROM """ + table + """
    WHERE username = ? AND
    lastedit = ?
    """,[sysop,str(lastEdit)])
    result = cursor.fetchone()
    conn.close()
    return result

# Ajoute (INSERT) ou modifie (UPDATE) le statut du signalement d'un admin
def db_upsert_status(sysop,lastEdit,status):
    table = "inactive_%s" %dico['site'].lang
    conn = sqlite3.connect('db/inactive.db')
    cursor = conn.cursor()
    cursor.execute("""
    INSERT OR IGNORE INTO """ + table + """(username,lastedit,status)
    VALUES(?,?,?)
    """,[sysop,str(lastEdit),status])
    cursor.execute("""
    UPDATE """ + table + """
    SET status = ?
    WHERE username = ? AND
    lastedit = ?
    """,[status,sysop,str(lastEdit)])
    conn.commit()
    conn.close()

#Lanceur principal
def inactiveSysopsManager(loc):
    global dico
    dico = loc
    dico['site'].login()
    sysopLastEdit = getSysopsLastEdit()
    inactiveSysopsHard, inactiveSysopsSoft = getInactiveSysops(sysopLastEdit)
    
    notifySysop(inactiveSysopsSoft)
    reportInactiveSysops(inactiveSysopsHard)


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
    inactiveSysopsManager(dicoIT)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
