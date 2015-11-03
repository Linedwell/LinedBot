#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script assurant la diffusion des notifications de W3PO à ses abonnés

# (C) Linedwell, 2011-2015
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys, getopt
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot

import cgi
import urllib2

# Déclarations
site = pywikibot.Site('fr','wikipedia')
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

#Retourne le titre associé à l'URL
def getURLTitle(url):
    webPage = urllib2.urlopen(url)
    _, params = cgi.parse_header(webPage.headers.get('Content-Type', ''))
    encoding = params.get('charset', 'utf-8')
    text = webPage.read().decode(encoding)
    tt = text.split("<title>") [1]
    titleFull = tt.split("</title>") [0]
    title = titleFull.split(" | Blog d'un geek polyglotte") [0]

    return title


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
        if args[0] in ('article', 'sondage', 'interview'):
            type = args[0]
        else:
            print "type incorrect : attendu 'article', 'sondage' ou 'interview'"
            sys.exit(2)

        if args[1] != '':
            link = args[1]
        else:
            print "lien obligatoire"
            sys.exit(2)

    else:
        print u"usage : python " + sys.argv[0] + " [--hs] type_de_billet lien"
        sys.exit(2)
    
    banner = "{{Utilisateur:Orikrin1998/Blog/Annonce|type=" + type + "|lien=" + link + "|date=~~~~~}}"
    billTitle = getURLTitle(link)
    if type == "interview":
        billTitle = "Interview de " + billTitle
    
    subscribers = getSubscribers(type,hs)

    for sub in subscribers:
        try:
            subTemp = sub.get()
        
        except pywikibot.NoPage:
            pywikibot.output(u"Page %s does not exist; skipping."
                             % page.title(asLink=True))
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        except pywikibot.LockedPage:
            pywikibot.output(u"Page %s is locked; skipping."
                             % page.title(asLink=True))
        else:
            message = u"\n\n== Du nouveau sur W3PO : " + billTitle + " ==\n" + banner
            sub.text += message
            sub.save(u"Du nouveau sur W3PO",minor=False)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
