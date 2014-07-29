#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script assurant la diffusion des notifications de W3PO à ses abonnés

# (C) Linedwell, 2011-2014
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys, getopt
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot

# Déclarations
site = pywikibot.getSite('fr','wikipedia')
nbrModif = 0
nbrTotal = 0

# Retourne la liste des personnes à qui envoyer la notification
def getSubscribers(group,hs):

    pageGroup = pywikibot.Page(site,u"Utilisateur:Orikrin1998/Blog/Abonnés/"+group.title()+"s")
    pageTotal = pywikibot.Page(site,u"Utilisateur:Orikrin1998/Blog/Abonnés/Wikipédia seulement")
    
    pageHS = pywikibot.Page(site,u"Utilisateur:Orikrin1998/Blog/Abonnés/Tous les articles")
    
    if not hs:
        subscribers = set(list(pageGroup.linkedPages(namespaces=3)) + list(pageTotal.linkedPages(namespaces=3)) + list(pageHS.linkedPages(namespaces=3)))
    
    if hs:
        subscribers = set(list(pageHS.linkedPages(namespaces=3)))

    return subscribers

# Retourne le bandeau de notification adapté
def getBanner(group, link):
    dict = {
        'article' : "Utilisateur:Orikrin1998/Blog/Annonce",
        'sondage' : "Utilisateur:Orikrin1998/Blog/Sondage",
    }
    
    template = "{{" + dict[group] + "|lien=" + link + "|date=~~~~~}}"

    return template


#Exécution
def main():
    
    type = ''
    link = ''
    hs = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h', ['hs'])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--hs'):
            hs = True


    if len(args) == 2:
        if args[0] in ("article", "sondage"):
            type = args[0]
        else:
            print "type incorrect : attendu 'blog' ou 'sondage'"
            sys.exit(2)

        if args[1] != '':
            link = args[1]
        else:
            print "lien obligatoire"
            sys.exit(2)

    else:
        print u"usage : python " + sys.argv[0] + " [--hs] type_de_billet lien"
        sys.exit(2)
    
    banner = getBanner(type,link)
    
    subscribers = getSubscribers(type,hs)

    for sub in subscribers:
        message = "\n\n== Du nouveau sur W3PO ==\n" + banner
        sub.text += message
        sub.save(u"Du nouveau sur W3PO",botflag=False)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
