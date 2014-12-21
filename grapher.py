#!/usr/bin/python
# -*- coding: utf-8 -*-
# Script de mise à jour de graphe

# (C) Linedwell, 2011-2015
#
# Distribué sous licence GNU GPLv3
# Distributed under the terms of the GNU GPLv3 license
# http://www.gnu.org/licenses/gpl.html

import sys
sys.path.insert(1, '..') #ajoute au PYTHONPATH le répertoire parent

import pywikibot

# Déclarations
site = pywikibot.Site('fr','wikipedia')
page = pywikibot.Page(site, u"Projet:Maintenance/Suivi d'admissibilité/graphe")

# Met à jour le graphe de la page passée en paramètre avec la nouvelle valeur
def update(val):
    last_values = file('_grapher.log','r').readlines()[-14:]
    last_values = [int(el.strip()) for el in last_values]
    last_values.append(val)
    
    #On fixe ymax (resp. ymin) à la valeur extrème trouvée +100 (resp. -100) arrondi à la centaine inférieure
    ymax = max(last_values) - max(last_values) % 100 + 100
    ymin = min(last_values) - min(last_values) % 100
    step = ymax - ymin
    step2= 100

    fields = """
 | coul_fond = white
 | largeur = 500
 | hauteur = 350
 | marge_g = 40
 | marge_d = 15
 | marge_h = 10
 | marge_b = 20
 | nb_series = 1
 | nb_abscisses = 15
 | y_max = {ymax}
 | y_min = {ymin}
 | grille = oui
 | pas_grille_principale = {step}
 | pas_grille_secondaire = {step2}
 | lb_x1 = -14 | lb_x2 = -13 | lb_x3 = -12 | lb_x4 = -11 | lb_x5 = -10
 | lb_x6 = -9 | lb_x7 = -8 | lb_x8 = -7 | lb_x9 = -6 | lb_x10 = -5
 | lb_x11 = -4 | lb_x12 = -3 | lb_x13 = -2 | lb_x14 = -1 | lb_x15 = 0
 | S01V01 = {val01}
 | S01V02 = {val02}
 | S01V03 = {val03}
 | S01V04 = {val04}
 | S01V05 = {val05}
 | S01V06 = {val06}
 | S01V07 = {val07}
 | S01V08 = {val08}
 | S01V09 = {val09}
 | S01V10 = {val10}
 | S01V11 = {val11}
 | S01V12 = {val12}
 | S01V13 = {val13}
 | S01V14 = {val14}
 | S01V15 = {val15}
 | points = non
"""
    
    context = {
        "ymax" : ymax,
        "ymin" : ymin,
        "step" : step,
        "step2": step2,
        "val01": last_values[0],
        "val02": last_values[1],
        "val03": last_values[2],
        "val04": last_values[3],
        "val05": last_values[4],
        "val06": last_values[5],
        "val07": last_values[6],
        "val08": last_values[7],
        "val09": last_values[8],
        "val10": last_values[9],
        "val11": last_values[10],
        "val12": last_values[11],
        "val13": last_values[12],
        "val14": last_values[13],
        "val15": last_values[14],

    }
    
    template = u"<noinclude>{{Mise à jour bot|Linedwell}}</noinclude>\n<center>\n{{Graphique polygonal" + fields.format(**context) + u"}}\n\n'''Évolution au cours des deux dernières semaines'''\n</center>"
    summary = "[[WP:Bot|Robot]] : mise à jour"

    page.text = template
    page.save(summary)
    
    gr_log = open('_grapher.log','w')
    for val in last_values:
        gr_log.write(str(val) + '\n')
    gr_log.close()

if __name__ == "__main__":
    try:
        main()
    finally:
        pywikibot.stopme()
