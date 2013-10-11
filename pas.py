#!/usr/bin/python
# -*- coding: utf-8 -*-
# author [[fr:User:Linedwell]]

import sys, getopt
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import re
import time
import pywikibot
from pywikibot import pagegenerators

#Variables globales
site = pywikibot.Site('fr','wikipedia')

delimiterBegin = u'= Propositions =\n'
delimiterEnd = u'= <small>Avertissements</small> =\n'
    
delimiterBeginRegex = u'=\s*Propositions\s*=\n'
delimiterEndRegex = u'=\s*<small>Avertissements</small>\s*=\n'

#Créé la section PàS du lendemain
def pasNewSection(pageTemp):
    global summary
    
    month = [u'janvier',u'février',u'mars',u'avril',u'mai',u'juin',u'juillet',u'août',u'septembre',u'octobre',u'novembre',u'décembre']
    pad = 1 #nombre de jours de decalage que l'on souhaite
    dateD = time.localtime(time.time() + pad * 24 * 3600)
    year = int(dateD.tm_year)
    monthNum = int(dateD.tm_mon)
    dayNum = int(dateD.tm_mday)
    
    if pageTemp.find(u'== ' + str(dayNum) + ' ' + month[monthNum - 1] + ' ==') == -1: #La section de dans 'pad' n'existe pas encore
        pageTempBegin, pageTempEnd = re.split(delimiterEndRegex,pageTemp)
        pageTempEnd = delimiterEnd + pageTempEnd
        
        newSection = u'== ' + str(dayNum) + ' ' + month[monthNum - 1] + ' ==\n'
        newSection += u'{{En-tête section PàS|' + str(dayNum)+ '|' + month[monthNum - 1] + '|' + str(year) + '}}\n\n'
        newSection += u'{{Boîte déroulante/début|titre=Requêtes traitées}}\n{{Boîte déroulante/fin}}\n\n'
        
        pageTemp = pageTempBegin + newSection + pageTempEnd
        
        if summary != u'':
            summary += u" ; initialisation de la section PàS du " + str(dayNum) + ' ' + month[monthNum - 1]
        else:
            summary += u"initialisation de la section PàS du " + str(dayNum) + ' ' + month[monthNum - 1]
    
    else:
        print u"Aucune modification, la section du " + str(dayNum) + " " + month[monthNum - 1] + " existe."

    return pageTemp

def pasRemoveSection(pageTemp):
    global summary

    pageTempBegin, pageTempBody = re.split(delimiterBeginRegex,pageTemp)
    pageTempBegin += delimiterBegin
    
    pageTempBody, pageTempEnd = re.split(delimiterEndRegex,pageTempBody)
    pageTempEnd = delimiterEnd + pageTempEnd
    
    section = re.split('(==\s*\d* \w*\s*==\n)',pageTempBody,flags=re.U)
    parser = re.compile(ur'\{\{En-tête section PàS\|.*?\}\}\s*\{\{Boîte déroulante\/début\|.*?\}\}', re.U | re.I | re.M)
    
    pageTempBody = u''
    count = 0

    for i in range(2,len(section),2):
        result = parser.search(section[i])
        if result:
            section[i] = section[i-1] = ''
            count += 1

    if count > 0:
        for s in section:
            pageTempBody += s

        pageTemp = pageTempBegin + pageTempBody + pageTempEnd
        summary = u"archivage de " + str(count) + " section(s)"

    return pageTemp

def main(argv):
    global summary
    
    archiveOnly = False
    try:
        opts, args = getopt.getopt(argv, 'a',['archive'])
    except getopt.GetoptError:
        print "usage: pas.py [-a]"
        exit(2)

    for opt, args in opts:
        if opt in ('-a', '--archive'):
            archiveOnly = True

    summary = u''
    target = u'Wikipédia:Pages à supprimer'
    page = pywikibot.Page(site,target)
    pageTemp = page.get()
    pageTempNew = pasRemoveSection(pageTemp)

    if not archiveOnly:
        pageTempNew = pasNewSection(pageTempNew)

    if pageTempNew != pageTemp:
            page.put(pageTempNew,"[[WP:Bot|Robot]] : " + summary)

    else:
        print "Aucune action aujourd'hui, archivage et section du lendemain non requis."

    #raw_input()
    


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    finally:
        pywikibot.stopme()