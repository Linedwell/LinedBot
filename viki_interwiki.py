#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script d'ajout des liens interwiki
# Auteur: Linedwell
# Licence: <à définir>

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot
from pywikibot import pagegenerators
import time,re
import itertools

# Déclarations
site = {
	'fr' : pywikibot.getSite('fr','vikidia'),
    'en' : pywikibot.getSite('simple','wikipedia'),
	'es' : pywikibot.getSite('es','vikidia'),
	'it' : pywikibot.getSite('it','vikidia'),
	'ru' : pywikibot.getSite('ru','vikidia'),
}

summary = {
    'fr' : u'[[Vikidia:Robot|Robot]] : mise à jour des interwikis',
    'it' : u'Bot : interwiki update',
    'es' : u'Bot : interwiki update',
    'en' : u'Bot : interwiki update',
    'ru' : u'Bot : interwiki update',
}


nbrModif = 0
nbrTotal = 0

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
        page.put(pageTemp,summary[pageLang])


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
        
            #retrait des interviki non valides (non liés depuis le viki source)
            for liw in localIwList:
                if not liw in linkList:
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
                pageLoc.put(pageLocTemp, summary[a.site.lang])


#Récupération de la liste des interwikis "réguliers"
def getInterwiki(page):
    text = page.text
    for linkmatch in pywikibot.link_regex.finditer(pywikibot.removeDisabledParts(text)):
        linktitle = linkmatch.group("title")
        link = pywikibot.Link(linktitle, page.site)

        try:
            if link.site != page.site:
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
    wpPage = pywikibot.Page(pywikibot.getSite(page.site.lang,"wikipedia"),page.title())
    wpLink = ''

    if wpPage.exists():
        wpLink = u"[[wp:" + wpPage.title() + "]]"
                         
    m = re.search(r"\[\[wp\:(?P<ln>.*)\]\]",pageTemp)

    if m != None:
        oldWpPage = pywikibot.Page(pywikibot.getSite(page.site.lang,"wikipedia"),m.group('ln'))
        if not oldWpPage.exists():
            pageTemp.replace(m.group(),wpLink)

    else:
        pageTemp += '\n' + wpLink

    return pageTemp





#Exécution
def main():
    timeStart = time.time()
    lang = 'fr'
    page = pywikibot.Page(site[lang],u'Utilisateur:Linedwell/Brouillon')
    inter(page)
    timeEnd = time.time()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()