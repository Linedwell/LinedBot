#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script d'ajout des liens interwiki

# (C) Linedwell, 2011-2018
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html


import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

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
	'ca' : pywikibot.Site('ca','vikidia'),
}

summary = {
	'fr' : u"[[Vikidia:Robot|Robot]] : mise à jour des interwikis",
	'it' : u"Bot : interwiki update",
	'es' : u"Bot : interwiki update",
	'en' : u"Bot : interwiki update",
	'ru' : u"Bot : interwiki update",
	'ca' : u"Bot : interwiki update",
}

projects = ['commons', 'incubator', 'mediawiki', 'meta', 'species', 'test',
            'wikibooks', 'wikidata', 'wikinews', 'wikipedia', 'wikiquote',
            'wikisource', 'wikiversity', 'wiktionary']

### debug ###
for s in site:
    site[s].login()
### end debug


def inter(page):
    pageTemp = page.get()
    
    pageTemp = removeDuplicates(pageTemp)

    iwDict = getInterwiki(page)
    iwList = iwDict.values()
    ewList = list(getExterwiki(page))
    
    try:
        for iw in iwList:
            _errChk = pywikibot.Page(site[iw.site.lang],iw.title)
            _errChk.exists()
    except ValueError:
        pywikibot.output(u"Page %s has interwiki issues; skipping."
                                % page.title(asLink=True))
    
    else:
    
        #print "iw: " + str(iwList)
        #print "ew: " + str(ewList)
        
        #sys.exit(0)
        
        pageLang = page.site.lang
        
        allList = {page.site:pywikibot.Link(page.title(),page.site)}
        #allList.append(pywikibot.Link(page.title(), page.site))
        
        #premier tour pour récupérer la liste des intervikis (valides)
        for iw in iwList:
            lang = iw.site.lang
            pageExt = pywikibot.Page(site[lang],iw.title)
            if not pageExt.exists():
                link = iw.astext()
                pageTemp = pageTemp.replace(link+'\n','')
                pageTemp = pageTemp.replace(link,'') #necessaire si dernier lien
            else:
                allList.update({iw.site:iw})

        pageTemp = updateWPlink(page,pageTemp)

        if page.get() != pageTemp:
            page.text = pageTemp
            page.save(summary[pageLang])


        #second tour pour la mettre à jour sur tous les autres vikis
        for key in allList:
            if key == page.site:
                continue #On saute le wiki de départ
            linkList = dict(allList)
            del linkList[key]
            
            pageLoc = pywikibot.Page(allList[key])

            localIwDict = getInterwiki(pageLoc)
            localIwList = list(getInterwiki(pageLoc))
            localEwList = list(getExterwiki(pageLoc))

            try:
                pageLocTemp = pageLoc.get()
                pageLocTemp = removeDuplicates(pageLocTemp)
                    
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
                for liw in localIwDict:
                    pageExt = pywikibot.Page(localIwDict[liw])
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
                    if not lnk in localIwDict:
                        link = linkList[lnk].astext(onsite=allList[key].site) #on force le lien à être "vu" depuis le wiki de destination
                        pageLocTemp += '\n' + link

                for lnk in ewList:
                    if not lnk in localEwList:
                        pageLocTemp += '\n' + lnk

                pageLocTemp = updateWPlink(pageLoc,pageLocTemp)

                if pageLoc.get() != pageLocTemp:
                    try:
                        pageLoc.text = pageLocTemp
                        pageLoc.save(summary[allList[key].site.lang])
                    except UnicodeDecodeError:
                        print u"UnicodeDecodeError : Skipping " + pageLoc.title()


#Récupération de la liste des interwikis "réguliers"
def getInterwiki(page):
    text = page.text
    iwDict = {}
    
    for linkmatch in pywikibot.link_regex.finditer(pywikibot.textlib.removeDisabledParts(text)):
        
        linktitle = linkmatch.group("title")
        link = pywikibot.Link(linktitle, page.site)
        #print link.site

        try:
            if link.site != page.site:
                if not link.site.family.name in projects:
                    iwDict[link.site] = link
                    #yield link
        except pywikibot.Error:
            continue

    return iwDict


#Récupération de la liste des interwikis "exotiques"
def getExterwiki(page):
    text = page.text
    extraLang = ['nl', 'de']
    
    for el in extraLang:
        exIw = re.search(r"\[\[" + el + r"\:(?P<ln>.*)\]\]", text)
        if exIw != None:
            yield u"[[" + el + ":" + exIw.group('ln') + "]]"


#Mise à jour de l'interwiki (éventuel) vers Wikipédia
def updateWPlink(page,pageTemp):
    pageTemp = pageTemp.replace("{{FULLPAGENAME}}", page.title()) #Nécessaire pour corriger les flemmards
    pageTemp = pageTemp.replace("{{PAGENAME}}", page.title()) #Nécessaire pour corriger les flemmards
    pageTemp = pageTemp.replace("{{BASEPAGENAME}}", page.title()) #Nécessaire pour corriger les flemmards
    wpPage = pywikibot.Page(pywikibot.Site(page.site.lang, "wikipedia"),page.title())
    wpLink = ''

    if wpPage.exists():
        wpLink = u"[[wp:" + wpPage.title() + "]]"
                         
    m = re.search(r"\[\[wp\:(?P<ln>.*?)\]\]", pageTemp)

    if m != None:
        oldWpPage = pywikibot.Page(pywikibot.Site(page.site.lang, "wikipedia"),m.group('ln'))
        if not oldWpPage.exists():
            pageTemp.replace(m.group(), wpLink)

    else:
        pageTemp += '\n' + wpLink

    return pageTemp

#Retire les occurences multiples de liens vers la même langue
def removeDuplicates(pageTemp):
    for key in site:
        occurences = len(re.findall(r"\[\[" + key + r":.*?\]\]", pageTemp))
        if occurences > 1:
            pageTemp = re.sub(r"\[\[" + key + r":.*?\]\](\n)?", '', pageTemp, count=occurences-1, flags=re.I | re.U)
    return pageTemp


#Exécution
def main():
    source = pywikibot.getSite('fr', 'vikidia')
    pagesList = pagegenerators.AllpagesPageGenerator(namespace=0,includeredirects=False, site=source, start=u"")
    for page in pagesList:
        print page.title()
        inter(page)

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
