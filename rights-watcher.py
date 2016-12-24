#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de suivi des modifications de droits utilisateur sur Vikidia.

# (C) Linedwell, 2011-2016
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html


import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

from datetime import datetime

import pywikibot
from pywikibot import pagegenerators

import mailer


# Déclarations
sites = {
    'fr' : pywikibot.Site('fr','vikidia'),
    'it' : pywikibot.Site('it','vikidia'),
    'de' : pywikibot.Site('de','vikidia'),
    'en' : pywikibot.Site('en','vikidia'),
    'es' : pywikibot.Site('es','vikidia'),
    'ru' : pywikibot.Site('ru','vikidia'),
    'ca' : pywikibot.Site('ca','vikidia'),
    'eu' : pywikibot.Site('eu','vikidia'),
    'scn' : pywikibot.Site('scn','vikidia'),
    #'test' : pywikibot.Site('test','vikidia'),
    'central' : pywikibot.Site('central','vikidia'),
}

### debug ###
for s in sites:
    sites[s].login()
### end debug

#Recuperation des journaux de modification de droits "sensibles"
def rights_logs(end):
    watched_rights = ["bureaucrat","sysop","nuker","abusefilter","bot","checkuser","oversight","developer"]
    report = ""
    
    for s in sites:
        site = sites[s]
        logevents = site.logevents(logtype="rights",end=end)

        for le in logevents:
            oldgroups = le.oldgroups
            newgroups = le.newgroups
            
            #Différence symétrique entre les deux listes, on regarde quels droits ont été retirés/ajoutés
            diff = list(set(oldgroups).symmetric_difference(set(newgroups)))
            
            # Si l'un des droits modifiés figure dans la liste des droits surveillés
            if (set(diff).intersection(watched_rights)):
            
                report += "[" + site.code + "][" + str(le.timestamp()) + "] " + le.user() + " -> " + le.page().title()  + " (" + str(oldgroups) + " -> " + str(newgroups) + ")\n"

    return report

#Envoie par mail le rapport de modification des droits
def mail_report(report):
    if report != "":
	#print report
        mailer.send('[RW] Modification de droits sur Vikidia.',report)

#Exécution
def main():
    last_check_file = 'rights-watcher.last'
    file = open(last_check_file,'r')
    last_check = file.read()
    file.close()

    report = rights_logs(last_check)
    mail_report(report)
    
    now = datetime.utcnow()
    file = open(last_check_file,'w')
    file.write(now.isoformat())
    file.close()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
