#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de maintenance pour vikidia
# Auteur: Linedwell
# Licence: <à définir>

import sys, getopt
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import re, time

import pywikibot
from pywikibot import pagegenerators

import callback
import logger


# Déclarations
site = pywikibot.getSite('fr','vikidia')
nbrModif = 0
nbrTotal = 0

# Traitement des nouvelles pages
def newPages(all=False):
    global nbrModif, nbrTotal
    
    log = u''
    
    ignorePage = pywikibot.Page(site,u'Utilisateur:LinedBot/Ignore')
    ignoreList = list(ignorePage.linkedPages())

    
    homonCat =  pywikibot.Category(site,u'Homonymie')
    ebaucheCat = pywikibot.Category(site,u'Ébauche')
    ebaucheCat = set(ebaucheCat.subcategories(recurse=3))
    hiddenCat = pywikibot.Category(site,u'Catégorie cachée')
    hiddenCat  = set(hiddenCat.subcategories())
    
    deadendPagesList = list(pagegenerators.DeadendPagesPageGenerator(site=site))
    lonelyPagesList = list(pagegenerators.LonelyPagesPageGenerator(site=site))
    
    
    if all:
        pagesList = pagegenerators.AllpagesPageGenerator(namespace=0,includeredirects=False,site=site)
    else:
        pagesList = pagegenerators.NewpagesPageGenerator(total=50,site=site)

    for page in pagesList:
        
        try:
            pageTemp = page.get()
            
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
            
            
            # On ne s'occupe de la page que si elle n'est pas une homonymie
            catTest = page.categories()
            if not homonCat in catTest:
                
                #On ne traite l'ajout de bandeau que si la page n'est pas ignorée
                jobList = []
                if not page in ignoreList:
                    
                    # s'il existe des références, on retire le job 'orphelin'
                    if page in lonelyPagesList:
                        jobList.append(u'orphelin')
                    
                    # s'il n'existe aucune catégorie (directe), on ajoute le job 'catégoriser'
                    cat = page.categories()
                    realCat = list(set(cat) - set(hiddenCat) - set(ebaucheCat))
                
                    nbCat = len(list(realCat))
                    if nbCat == 0:
                        jobList.append(u'catégoriser')
                    
                    # si la page ne pointe vers aucune autre, on l'indique en impasse
                    if page in deadendPagesList:
                        jobList.append(u'impasse')
                    
                    """
                    # si la page fait plus de 2000 octets et ne contient aucun lien externe
                    if len(pageTemp) > 2000 and len(list(page.extlinks())) == 0:
                        jobList.append(u'sourcer')
                    """
            
                else:
                    print u'Skipping [[' + page.title() + ']], page in ignore list.'


                pageTemp, oldJobList = removeBanner(pageTemp)
                jobList = updateJobList(oldJobList, jobList)
                job = u''

            
                # Différence symétrique entre les deux listes, on regarde si des éléments ne sont pas contenus dans les deux listes : (A-B)+(B-A)
                diff = list(set(oldJobList).symmetric_difference(set(jobList)))

                if diff != []:
                    nbrTotal += 1
                    if len(jobList) > 0:
                        job = ','.join(jobList)
                        banner = u'{{Maintenance|job=' + job + '|date=~~~~~}}\n\n'
                        pageTemp = banner + pageTemp
                    summary = u'[[VD:Robot|Robot]] : Mise à jour du bandeau de maintenance.'

                    c = callback.Callback()
                    page.put(pageTemp,summary,callback=c)

                    if c.error == None:
                        nbrModif += 1

                    log +=u'*' + '{{Utilisateur:LinedBot/ExtLinker|' + page.title() + u'}} : Mise à jour du bandeau {{m|maintenance}} avec les paramètres suivants : ' + job + '\n'

    return log



# Retrait du bandeau si besoin
def removeBanner(pageTemp):
    parser = re.compile(r'\{\{Maintenance\|job=(?P<jb>.*?)\|.*?\}\}(?P<fin>\r\n|\n|\ )',re.I | re.U | re.DOTALL)
    searchResult = parser.search(pageTemp)
    oldJobList = []
    if searchResult:
        jobT = searchResult.group('jb')
        jobT = ''.join(jobT.split()) # on retire tous les espaces de la chaine
        oldJobList = jobT.split(',') # on convertit la chaine en list
        pageTemp = parser.sub('',pageTemp,1)
    return pageTemp, oldJobList

# Retourne une jobList mise à jour (catégories appliquées par le bot + utilisateurs)
def updateJobList(oldJobList, newJobList):
    botJobList = [u'catégoriser',u'impasse',u'orphelin',u'sourcer']
    
    tempJobList = list(oldJobList)
    for j in botJobList:
        if j in oldJobList:
            tempJobList.remove(j)
    newJobList = list(set(newJobList+tempJobList))
    return newJobList


# Exécution
def main(argv):
    
    all = False
    
    try:
        opts, args = getopt.getopt(argv, 'a', ['all'])
    except getopt.GetoptError:
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-a', '--all'):
            all = True

    log = u''
    timeStart = time.time()
    log += newPages(all)
    timeEnd = time.time()
    logger.setValues(nbrTotal,nbrModif)
    logger.editLog(site,log)
    print str(nbrModif) + u' (of ' + str(nbrTotal) + ') pages were modified in '+ str(round(timeEnd - timeStart,2)) + 's.'


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        pywikibot.stopme()