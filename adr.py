#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de mise à jour de statut de relecteur

# Auteur: Orikrin

# Adapté depuis un script de Linedwell
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

import pywikibot
import time

# Déclarations
site = pywikibot.Site('fr','wikipedia')
statuts = ['libre','occupe','pause']
title = u'Utilisateur:Orikrin1998/AdR'


#Exécution
def main(args):
    if len(args) > 1: #argv[0] = nom du script
        stat = args[1]
        if stat in statuts:
            if stat == "occupe":
                stat = u"occupé"
            page = pywikibot.Page(site,title)
            pageTemp = stat
            summary = u"Mise à jour : " + stat
        
            if page.get() == pageTemp:
                print u"Aucune mise à jour nécessaire."
            else:
                page.text = pageTemp
                page.save(summary)
                print u"Action effectuée."
        else:
            print u"Statut '%s' inexistant\nStatuts disponibles : %s" %(stat,str(statuts))
    else:
        print "usage: python " + args[0] + " <statut>"
        sys.exit(2)


if __name__ == "__main__":
    try:
        main(sys.argv)
    finally:
        pywikibot.stopme()
