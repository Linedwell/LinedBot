#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script d'ajout des liens interwiki

# (C) Linedwell, 2011-2015
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html


import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot
from pywikibot import pagegenerators
import re
import itertools

# Déclarations
site = {
	'fr' : pywikibot.Site('fr','vikidia'),
    'en' : pywikibot.Site('en','vikidia'),
	'es' : pywikibot.Site('es','vikidia'),
	'it' : pywikibot.Site('it','vikidia'),
	'ru' : pywikibot.Site('ru','vikidia'),
}

summary = {
    'fr' : u"[[Vikidia:Robot|Robot]] : mise à jour des interwikis",
    'it' : u"Bot : interwiki update",
    'es' : u"Bot : interwiki update",
    'en' : u"Bot : interwiki update",
    'ru' : u"Bot : interwiki update",
}

projects = ['commons', 'incubator', 'mediawiki', 'meta', 'species', 'test',
            'wikibooks', 'wikidata', 'wikinews', 'wikipedia', 'wikiquote',
            'wikisource', 'wikiversity', 'wiktionary']


def inter(page):
    pageTemp = page.get()
    iwList = list(getInterwiki(page))
    ewList = list(getExterwiki(page))
    
    pageLang = page.site.lang
    
    allList = []
    allList.append(pywikibot.Link(page.title(), page.site))
    
    #premier tour pour récupérer la liste des intervikis (valides)
    for iw in iwList:
        lang = iw.site.lang
        pageExt = pywikibot.Page(site[lang],iw.title)
        if not pageExt.exists():
            link = iw.astext()
            pageTemp = pageTemp.replace(link+'\n','')
            pageTemp = pageTemp.replace(link,'') #necessaire si dernier lien
        else:
            allList.append(iw)

    pageTemp = updateWPlink(page,pageTemp)

    if page.get() != pageTemp:
        page.text = pageTemp
        page.save(summary[pageLang])


    #second tour pour la mettre à jour sur tous les autres vikis
    for a in allList[1:]:
        linkList = list(allList)
        linkList.remove(a)
        
        pageLoc = pywikibot.Page(a.site,a.title)
        
        localIwList = list(getInterwiki(pageLoc))
        localEwList = list(getExterwiki(pageLoc))
        
        try:
            pageLocTemp = pageLoc.get()
                
        except pywikibot.NoPage:
            pywikibot.output(u"Page %s does not exist; skipping."
                                     % pageLoc.title(asLink=True))
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                                     % pageLoc.title(asLink=True))
        except pywikibot.LockedPage:
            pywikibot.output(u"Page %s is locked; skipping."
                                     % pageLoc.title(asLink=True))
        else:
        
            #retrait des interviki non valides
            for liw in localIwList:
                pageExt = pywikibot.Page(liw)
                if not pageExt.exists():
                    link = liw.astext()
                    pageLocTemp = pageLocTemp.replace(link+'\n','')
                    pageLocTemp = pageLocTemp.replace(link,'') #necessaire si dernier lien

            for lew in localEwList:
                if not lew in ewList:
                    pageLocTemp = pageLocTemp.replace(lew+'\n','')
                    pageLocTemp = pageLocTemp.replace(lew,'') #necessaire si dernier lien


            #ajout des nouveaux interviki
            for lnk in linkList:
                if not lnk in localIwList:
                    link = lnk.astext(onsite=a.site) #on force le lien à être "vu" depuis le wiki de destination
                    pageLocTemp += '\n' + link

            for lnk in ewList:
                if not lnk in localEwList:
                    pageLocTemp += '\n' + lnk

            pageLocTemp = updateWPlink(pageLoc,pageLocTemp)

            if pageLoc.get() != pageLocTemp:
                try:
                    pageLoc.text = pageLocTemp
                    pageLoc.save(summary[a.site.lang])
                except UnicodeDecodeError:
                    print u"UnicodeDecodeError : Skipping " + pageLoc.title()


#Récupération de la liste des interwikis "réguliers"
def getInterwiki(page):
    text = page.text
    for linkmatch in pywikibot.link_regex.finditer(pywikibot.removeDisabledParts(text)):
        linktitle = linkmatch.group("title")
        link = pywikibot.Link(linktitle, page.site)

        try:
            if link.site != page.site:
                if not link.site.family.name in projects:
                    yield link
        except pywikibot.Error:
            continue

#Récupération de la liste des interwikis "exotiques"
def getExterwiki(page):
    text = page.text
    extraLang = ['nl','de']
    
    for el in extraLang:
        exIw = re.search(r"\[\[" + el + "\:(?P<ln>.*)\]\]", text)
        if exIw != None:
            yield u"[[" + el + ":" + exIw.group('ln') + "]]"


#Mise à jour de l'interwiki (éventuel) vers Wikipédia
def updateWPlink(page,pageTemp):
    pageTemp = pageTemp.replace("{{FULLPAGENAME}}",page.title()) #Nécessaire pour corriger les flemmards
    pageTemp = pageTemp.replace("{{PAGENAME}}",page.title()) #Nécessaire pour corriger les flemmards
    wpPage = pywikibot.Page(pywikibot.getSite(page.site.lang,"wikipedia"),page.title())
    wpLink = ''

    if wpPage.exists():
        wpLink = u"[[wp:" + wpPage.title() + "]]"
                         
    m = re.search(r"\[\[wp\:(?P<ln>.*?)\]\]",pageTemp)

    if m != None:
        oldWpPage = pywikibot.Page(pywikibot.getSite(page.site.lang,"wikipedia"),m.group('ln'))
        if not oldWpPage.exists():
            pageTemp.replace(m.group(),wpLink)

    else:
        pageTemp += '\n' + wpLink

    return pageTemp





#Exécution
def main():
    source = pywikibot.getSite('fr','vikidia')
    pagesList = pagegenerators.AllpagesPageGenerator(namespace=0,includeredirects=False,site=source,start=u"")
    for page in pagesList:
        print page.title()
        inter(page)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()