#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de mise à jour de statut

# Auteur: Orikrin

# Adapté depuis un script de Linedwell
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

import pywikibot

# Déclarations
site = pywikibot.Site('fr','wikipedia')
statuts = ['online','offline','away','busy','patrol','redact','wikislow','invisible']
title = u'Utilisateur:Orikrin1998/Statut'


#Exécution
def main(args):
    if len(args) > 1: #argv[0] = nom du script
        stat = args[1]
        if stat in statuts:
            page = pywikibot.Page(site,title)
            pageTemp = u"{{statut|" + stat + "|" + title + "}}"
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
