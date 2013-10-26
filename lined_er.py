#!/usr/bin/python
# -*- coding: utf-8 -*-
# Ce script parcourt la [[Catégorie:Événement récent]] et ses sous-catégories pour retirer le bandeau au bout de 15j
# Auteur : Linedwell
# Licence : <à définir>

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import re, time
from datetime import date, datetime, timedelta

import pywikibot
from pywikibot import pagegenerators

import callback
import ignoreList
import lined_log

# Déclarations
site = pywikibot.getSite('fr','wikipedia')
nbrModif = 0
nbrTotal = 0
ignoreList = ignoreList.ignoreList

# Modification du wiki
def removeTemplate(pagesList,catname,delay,checkTalk=False):
    global nbrModif,nbrTotal
    
    log = u''
    summary = u''
    limit = calcLimit(delay)
    motif = motifFinder(catname)
    
    for page in pagesList:
        if not page.title() in ignoreList:
            
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
            
                if page.editTime() < limit:
                    if checkTalk:
                        talk = page.toggleTalkPage()
                    if not checkTalk or (talk.exists() and talk.editTime() <= limit):
                        nbrTotal += 1
                        lastEdit = page.editTime()
                        duration = calcDuration(lastEdit)
                        for m in motif:
                            parser = re.compile(r'\{\{' + m + r'.*?\}\}(?P<fin>\r\n|\n|\ )',re.I | re.U | re.DOTALL)
                            searchResult = parser.search(pageTemp) #On cherche si le motif {{m}} existe dans la page
                            if searchResult:
                                templateResult = searchResult.group()
                                pageTemp = parser.sub('',pageTemp,1) #Retire la 1re occurrence du motif dans la page
                                
                                templateResult = templateResult.replace('\r\n','') #Retire les sauts de ligne contenus dans le modèle avant de l'ajouter au résumé
                                templateResult = templateResult.replace('\n','') #Correspond au second type de retour à la ligne
                                
                                summary = u"Retrait du bandeau " + templateResult + u" (non modifié depuis " + str(duration.days) + " jours)."
                                
                                c = callback.Callback()
                                
                                page.put(pageTemp,"[[WP:Bot|Robot]] : " + summary, callback=c)
                                break
                            else:
                                summary = u'Aucun modèle trouvé correspondant au motif: ' + str(motif)
                
                        if c.error == None:
                            nbrModif += 1
                            status = '{{Y&}}'
                        else:
                            status = '{{N&}}'
                        log += u'*' + status + ' [[' + page.title() + ']] : ' + summary.replace('{{','{{m|') + '\n'
        else:
            print u'Skipping [[' + page.title() + ']], page in ignore list.'

    return log
	

#Retourne le motif correspondant au(x) modèle(s) catégorisant(s) dans la catégorie donnée 	
def motifFinder(catname):
	motif = []
	if catname == u'Événement récent':
		motif = [u'(Section )?[Éé]v[éè]nement[_ ]récent']

	elif catname == u'Mort récente':
		motif = [u'Mort[_ ]récente?', u'Décès[_ ]récent']
		
	elif catname == u'Élection récente':
		motif = [u'[Éé]lection[_ ]récente']
		
	elif catname == u'Compétition sportive récente':
		motif = [u'Compétition[_ ]sportive[_ ]récente', u'[Éé]v[éè]nement[_ ]sportif[_ ]récent']
	
	elif catname == u'Wikipédia:Triple révocation':
		motif = [u'Règle[_ ]des[_ ]3[_ ]révocations', u'Règle[_ ]des[_ ]3[_ ]reverts', u'Règle[_ ]des[_ ]3[_ ]réverts', u'Règle[_ ]des[_ ]trois[_ ]reverts', u'Règle[_ ]des[_ ]trois[_ ]réverts', u'R3R', u'3RR']
		
	elif catname == u'Article en travaux':
		motif = [u'En[_ ]travaux', u'En[_ ]construction', u'Pas[_ ]fini', u'Travail[_ ]de[_ ]groupe']
		
	elif catname == u'Article en cours':
		motif = [u'En[_ ]cours', u'Plusieurs[_ ]en[_ ]cours']
		
	return motif

#Retourne la date avant laquelle on considère obsolète l'usage du modèle
def calcLimit(delay):
	today = datetime.today()
	limite = today - timedelta(seconds=delay)
	return limite
	
#Retourne le temps écoulé entre une date et le jour courant
def calcDuration(date):
	today = datetime.today()
	duration = today - date
	return duration
	
# Récupération des pages de la catégorie
def crawlerCat(category, delay,subcat=False,checkTalk=False):
    log = u''
    cat = pywikibot.Category(site,category)
    pagesInCat = list(cat.articles(False))
    pagesList = pagegenerators.PreloadingGenerator(pagesInCat) # On génère la liste des pages incluses dans la catégorie
    pagesList = pagegenerators.NamespaceFilterPageGenerator(pagesList,[0]) #On ne garde que les articles (Namespace 0)
    log += removeTemplate(pagesList,cat.title(withNamespace=False),delay,checkTalk)
    
    if subcat:
        subcat -= 1
        subcategories = list(cat.subcategories())
        for subc in subcategories:
            log += crawlerCat(subc.title(withNamespace=False), delay, subcat, checkTalk)

    return log

# Exécution
def main():
    log = u''
    timeStart = time.time()
    log += crawlerCat(u'Événement récent',1296000,1,False) #15 jours, inclusion des sous-catégories de 1er niveau
    log += crawlerCat(u'Catégorie:Wikipédia:Triple révocation',2592000,False,True) #30 jours, inclusion des PdD associées aux articles
    log += crawlerCat(u'Article en travaux',864000,False,True) #10 jours, inclusion des PdD associées aux articles
    log += crawlerCat(u'Article en cours',432000,False,True) #5 jours, inclusion des PdD associées aux articles
    timeEnd = time.time()
    lined_log.setValues(nbrTotal,nbrModif)
    lined_log.editLog(site,log)

    print str(nbrModif) + u' (of ' + str(nbrTotal) + ') pages were modified in '+ str(round(timeEnd - timeStart,2)) + 's.'


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
