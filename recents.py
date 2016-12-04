#!/usr/bin/python
# -*- coding: utf-8 -*-
# Ce script parcourt la [[Catégorie:Événement récent]] et ses sous-catégories pour retirer le bandeau au bout de 15j


# (C) Linedwell, 2011-2016
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import mylogging

import re, time
from datetime import date, datetime, timedelta

import sqlite3, hashlib

import pywikibot
from pywikibot import pagegenerators, textlib

import callback
#import ignoreList
import logger

# Déclarations
site = pywikibot.Site('fr','wikipedia')
nbrModif = 0
nbrTotal = 0
#ignoreList = ignoreList.ignoreList
ignorePage = pywikibot.Page(site,u"Utilisateur:LinedBot/Ignore")
ignoreList = list(ignorePage.linkedPages())

# Modification du wiki
def removeTemplate(pagesList,catname,delay,sinceAdd=False,checkTalk=False):
    global nbrModif,nbrTotal
    
    log = u''
    summary = u''
    templateFound = False
    limit = calcLimit(delay)
    motif = motifFinder(catname)
    regex = [re.compile(m) for m in motif]
    
    for page in pagesList:
        if not page in ignoreList:
            
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

            	lastEdit = page.editTime()

            	if sinceAdd:
            		added_timestamp = db_check_add(page,motif)
            		if added_timestamp:
            			lastEdit = added_timestamp
      
                if lastEdit < limit:
                    if checkTalk:
                        talk = page.toggleTalkPage()
                    if not checkTalk or not talk.exists() or talk.editTime() < limit:
                        nbrTotal += 1
                        duration = calcDuration(lastEdit)
                        c = callback.Callback() #(re)init de c
                        for m in motif:
                            parser = re.compile(r'{{' + m + r'({{1er}}|{{date.*?}}|.)*?}}(\s*?|(?={{))',re.I | re.U | re.DOTALL)
                            searchResult = parser.search(pageTemp) #On cherche si le motif {{m}} existe dans la page
                            if searchResult:
                            	templateFound = True
                                templateResult = searchResult.group()
                                pageTemp = parser.sub('',pageTemp,1) #Retire la 1re occurrence du motif dans la page
                                
                                templateResult = templateResult.replace('\r\n','') #Retire les sauts de ligne contenus dans le modèle avant de l'ajouter au résumé
                                templateResult = templateResult.replace('\n','') #Correspond au second type de retour à la ligne
                                
                                if sinceAdd and added_timestamp:
                                	summary = u"Retrait du bandeau %s (ajouté il y a %s jours)." %(templateResult,duration.days)
                                else:
                                	summary = u"Retrait du bandeau %s (non modifié depuis %s jours)." %(templateResult,duration.days)
                                
                                c = callback.Callback()
                                
                                page.text = pageTemp
                                page.save("[[WP:Bot|Robot]] : " + summary, callback=c)
                                break
                            else:
                            	templateFound = False
                                summary = u"Aucun modèle trouvé correspondant au motif: " + str(motif)
                
                        if c.error == None and templateFound:
                            nbrModif += 1
                            status = "{{Y&}}"
                        else:
                            status = "{{N&}}"
                        log += u"*%s [[%s]] : %s\n" %(status,page.title(),summary.replace('{{','{{m|'))
			db_del_entry(page.title(),motif)
        else:
            pywikibot.output(u"Page %s in ignore list; skipping."
                                 % page.title(asLink=True))

    return log
	

#Retourne le motif correspondant au(x) modèle(s) catégorisant(s) dans la catégorie donnée 	
def motifFinder(catname):
	motif = []
	if catname == u"Événement récent":
		motif = [u'(Section )?[Éé]v[éè]nements?[_ ]récents?']

	elif catname == u"Mort récente":
		motif = [u'Mort[_ ]récente?', u'Décès[_ ]récent']
		
	elif catname == u"Scrutin récent":
		motif = [u'Scrutin[_ ]récent', u'[EÉé]lection[_ ]récente']
		
	elif catname == u"Compétition sportive récente":
		motif = [u'Compétition[_ ]sportive[_ ]récente', u'[Éé]v[éè]nement[_ ]sportif[_ ]récent']
	
	elif catname == u"Wikipédia:Triple révocation":
		motif = [u'Règle[_ ]des[_ ]3[_ ]révocations', u'Règle[_ ]des[_ ]3[_ ]reverts', u'Règle[_ ]des[_ ]3[_ ]réverts', u'Règle[_ ]des[_ ]trois[_ ]reverts', u'Règle[_ ]des[_ ]trois[_ ]réverts', u'R3R', u'3RR']
		
	elif catname == u"Article en travaux":
		motif = [u'(En[_ ])?travaux', u'En[_ ]construction', u'Pas[_ ]fini', u'Travail[_ ]de[_ ]groupe']
		
	elif catname == u"Article en cours":
		motif = [u'En[_ ]cours', u'Plusieurs[_ ]en[_ ]cours']
		
	return motif

#Retourne la date avant laquelle on considère obsolète l'usage du modèle
def calcLimit(delay):
	today = datetime.utcnow()
	limite = today - timedelta(seconds=delay)
	return limite
	
#Retourne le temps écoulé entre une date et le jour courant
def calcDuration(date):
	today = datetime.utcnow()
	duration = today - date
	return duration


#Retourne la date à laquelle le motif donné est apparu dans la page
#Fonction adaptée de https://github.com/Toto-Azero/Wikipedia/blob/master/pywikibot/mort_recente.py
#(C) Toto Azéro

def find_add(page,motif):
	regex = [re.compile(m) for m in motif]
	death_found = True
	maxrevision = 100
	history = page.getVersionHistory(total=maxrevision)

	if len(history) == 1:
		[(id, timestamp, user, comment)] = history
		return (pywikibot.User(site, user), id, timestamp)
	
	pywikibot.output(u"=====================================")
	pywikibot.output(u"Page : %s" % page.title())

	oldid = None
	requester = None
	timestamp = None
	previous_timestamp = None

	for (id, timestamp, user, comment) in history:

		pywikibot.output("Analyzing id %i: timestamp is %s and user is %s" % (id, timestamp, user))
	
		text = page.getOldVersion(id)
		try:	
			templates_params_list = textlib.extract_templates_and_params(text)
		except Exception:
			pywikibot.output("Skipping id %i; page content is hidden" % (id))
			continue

		death_found = False
		for (template_name, dict_param) in templates_params_list:
			try:
				template_page = pywikibot.Page(pywikibot.Link(template_name, site, defaultNamespace=10), site)
				
                # TODO : auto-finding redirections
				if any(r.match(template_page.title(withNamespace=False)) for r in regex):
					death_found = True
					break
			except Exception, myexception:
				pywikibot.output(u'An error occurred while analyzing template %s' % template_name)
				pywikibot.output(u'%s %s'% (type(myexception), myexception.args))
	
		if oldid:
		 	print("id is %i ; oldid is %i" % (id, oldid))
		else:
		 	print("id is %i ; no oldid" % id)
		if not death_found:
			if id == oldid:
				pywikibot.output(u"Last revision does not contain any %s template!" % motif)
				return None
			else:
				pywikibot.output(u"-------------------------------------")
				triplet = (requester, oldid, previous_timestamp)
				try:
					pywikibot.output(u"Page : %s" % page.title())
					pywikibot.output(u"Found it: user is %s; oldid is %i and timestamp is %s" % triplet)
				except:
					pass
				return triplet
		else:
			requester = pywikibot.User(site, user)
			oldid = id
			previous_timestamp = timestamp

	# Si on arrive là, c'est que la version la plus ancienne de la page contenait déjà le modèle
	return (pywikibot.User(site, user), id, timestamp)

# Vérifie si la date d'ajout du motif est déjà présente en base. Si oui, la retourne, sinon parcourt l'historique de la page
# et ajoute les informations à la base
def db_check_add(page, motif):
	hash_motif = hashlib.md5(str(motif)).hexdigest()

	conn = sqlite3.connect('db/recents.db')
	cursor = conn.cursor()
	cursor.execute("""
	SELECT * FROM recents
	WHERE page = ? AND
	pattern = ?
	""",[page.title(),hash_motif])
	result = cursor.fetchone()
	
	if not result:
		pywikibot.output(u"No timestamp for %s add to %s in DB; checking page revisions"%(motif,page.title()))
		_,_,added = find_add(page,motif)
		if not added:
			return None
		timestamp = added.strftime("%Y-%m-%d %H:%M:%S")
		cursor.execute("""
		INSERT INTO recents(page,added,pattern) VALUES(?,?,?)""", (page.title(),timestamp,hash_motif))
		conn.commit()
		return added
	else:
        	pywikibot.output(u"Timestamp for %s add to %s found in DB"%(motif,page.title()))
                
	conn.close()

# Supprime de la base les informations sur l'ajout du motif sur la page
def db_del_entry(page,motif):
	hash_motif = hashlib.md5(str(motif)).hexdigest()
        conn = sqlite3.connect('db/recents.db')
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM recents
        WHERE page = ? AND
        pattern = ?
        """,[page.title(),hash_motif])
	conn.commit()
	conn.close()

# Supprime de la base les entrées plus anciennes que X jours	
def db_clean_old(jours):
	today = datetime.utcnow()
	older = today - timedelta(seconds=jours * 86400)
	oldfrmt = older.strftime("%Y-%m-%d")
	conn = sqlite3.connect('db/recents.db')
        cursor = conn.cursor()
        cursor.execute("""
        DELETE FROM recents
        WHERE added < ?
        """,(oldfrmt,))
	conn.commit()
	conn.close()
	
# Récupération des pages de la catégorie
def crawlerCat(category, delay,sinceAdd=False,subcat=False,checkTalk=False):
    log = u''
    cat = pywikibot.Category(site,category)
    pagesInCat = list(cat.articles(False))
    pagesList = pagegenerators.PreloadingGenerator(pagesInCat) # On génère la liste des pages incluses dans la catégorie
    pagesList = pagegenerators.NamespaceFilterPageGenerator(pagesList,[0]) #On ne garde que les articles (Namespace 0)
    log += removeTemplate(pagesList,cat.title(withNamespace=False),delay,sinceAdd,checkTalk)
    
    if subcat:
        subcat -= 1
        subcategories = list(cat.subcategories())
        for subc in subcategories:
            log += crawlerCat(subc.title(withNamespace=False), delay, sinceAdd, subcat, checkTalk)

    return log

# Exécution
def main():
    log = u''
    timeStart = time.time()
    log += crawlerCat(category=u'Événement récent',delay=1296000,sinceAdd=True,subcat=1) #15 jours, inclusion des sous-catégories de 1er niveau
    log += crawlerCat(category=u'Catégorie:Wikipédia:Triple révocation',delay=2592000,checkTalk=True) #30 jours, inclusion des PdD associées aux articles
    log += crawlerCat(category=u'Article en travaux',delay=1296000,checkTalk=True) #15 jours, inclusion des PdD associées aux articles
    log += crawlerCat(category=u'Article en cours',delay=604800,checkTalk=True) #7 jours, inclusion des PdD associées aux articles

    timeEnd = time.time()
    logger.setValues(nbrTotal,nbrModif)
    logger.editLog(site,log)
    db_clean_old(60)

    pywikibot.output(u"%s (of %s) pages were modified in %s s."
    			%(nbrModif,nbrTotal,round(timeEnd-timeStart,2)))


if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
