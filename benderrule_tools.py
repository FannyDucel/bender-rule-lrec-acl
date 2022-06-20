#!/usr/bin/env python
# coding: utf-8

# In[2]:


from nltk.tokenize import word_tokenize
import pandas as pd
from langdetect import detect
import glob
import re
import json
import tqdm

def read_file(path):
    with open(path, encoding="utf-8", errors="ignore") as f:
        chaine = f.read()
    return chaine

def get_list_lang(lang="en"):
    liste_langues_en_txt = read_file(f"DATA/liste_langues_{lang}.txt")
    liste_langues_en_txt = liste_langues_en_txt.replace("\n",",")
    liste_langues_en_txt = liste_langues_en_txt.replace("  ","")
    liste_langues_en_txt = liste_langues_en_txt.replace('"',"")
    liste_langues_en_txt = liste_langues_en_txt.lower()
    liste_langues_en_txt = liste_langues_en_txt.split(",")
    return liste_langues_en_txt

def br_appliquee(liste_chemins,liste_langues,langue="french"):
    """Prend en entrée la liste de chemins des articles -créée avec la fonction chemin_corpus(chemin)- 
    + la liste de langues -créée avec la fonction liste_langues(fichierjson)
    Renvoie un dictionnaire de dictionnaires de forme {chemin: {langue_citée: nb_occurrence}}"""
    
    dico_br_app = {}
    for chemin in tqdm.tqdm(liste_chemins):
        chemin_propre = chemin.split("\\")[-1]
        chaine = read_file(chemin).lower()
        chaine_l_propre = re.sub(r'[^\w]',' ', chaine)
        liste_mots_tok = word_tokenize(chaine_l_propre, language=langue)
        #TODO: optimize with sets
        for mot in liste_mots_tok:
            for lg in liste_langues:
                if mot == lg:
                    dico_br_app.setdefault(chemin_propre, {})
                    dico_br_app[chemin_propre].setdefault(lg, 0)
                    dico_br_app[chemin_propre][lg]+=1

    return dico_br_app
def chemin_corpus(chemin_dossier,langue="fr",taln_ou_acl="taln"):
    """Prend en entrée le chemin du corpus ("archives_Boudin_txt/*/*/actes/*")
    Renvoie une liste contenant les chemins des articles en français"""
    
    liste_chemins = []

    for chemin in tqdm.tqdm(glob.glob(chemin_dossier)):
        chaine = read_file(chemin)
        if detect(chaine)==langue:
            ###POUR EXCLURE LES DOCUMENTS QUI NE SONT PAS VRAIMENT ARTICLES (souvent très courts)
            if taln_ou_acl=="taln":
                tirets = chemin.split("-")
                type_art = tirets[-2]
                if type_art != "demo" and type_art !="invite":
                    liste_chemins.append(chemin)
            if taln_ou_acl=="acl":
                if "P" in chemin:
                    if "the" in chaine:
                        liste_chemins.append(chemin)
                        
            if taln_ou_acl=="lrec":
                if "the" in chaine:
                    liste_chemins.append(chemin)
    return liste_chemins

def chemins_annotes(fichier_csv, cas_bender,nbheader=2,taln_ou_acl="taln"):
    """Prend en entrée le chemin vers le fichier csv qui contient le tableau d'annotation manuelle ("annotation_csv.csv")
    + le cas de figure d'application de la règle de Bender ('Appliquée', 'Non-appliquée', ...)
    + le nb_header à préciser ntmt pour langue traitée car une ligne en-dessous 
    Retourne la liste des chemins d'articles concernés"""
    
    dataset = pd.read_csv(fichier_csv,header=nbheader)
    annotes_cas = dataset.loc[dataset[cas_bender].notnull()]
    liste_annotes_cas = list(annotes_cas.iloc[:,1].values)
    if taln_ou_acl == "taln":
        url = "http://talnarchives.atala.org/TALN/"
    if taln_ou_acl == "acl":
        url = "https://aclanthology.org/"
    if taln_ou_acl == "lrec":
        url = "http://www.lrec-conf.org/proceedings/"
    
    chemins_annotes_cas = []
    for chemin in liste_annotes_cas:
        if type(chemin)==str:
            if url not in chemin and taln_ou_acl=="lrec":
                chemin = "http://www.lrec-conf.org/proceedings/"+chemin
            if url in chemin:
                dossiers = chemin.split("/")
                chemin_propre = dossiers[-1]
                chemin_propre = chemin_propre.replace(".pdf",".txt")
                chemins_annotes_cas.append(chemin_propre)
                
    return chemins_annotes_cas

def dico_br_appliquee_phrases(liste_chemins_annotes,liste_langues,chemins_annotes_appliquee):#,langue="french"):
    #faire deux dicos : 
#un où on envoie les phrases qui contiennent un nom de langue qui est bien la langue étudiée (annotée manuellement comme appliquée)
#un où on envoie les phrases qui contiennent un nom de langue mais qui n'est pas la langue étudiée (annotée manuellement comme autre chose qu'appliquée)
    dico_phrases_nomlg = {"appliquée":[], "non-appliquée": []}
    stats = {}
    for chemin in tqdm.tqdm(liste_chemins_annotes):
            #nettoyer articles et chemins
        chemin_propre = chemin.split("/")[-1]
        chaine = read_file(chemin).lower()
        liste_phrases = chaine.split(".")
        for phrase in liste_phrases:
            for mot in phrase.split():
                for l in liste_langues:
                    if mot == l:
                        stats.setdefault(mot, 0)
                        stats[mot]+=1
                        if chemin_propre in chemins_annotes_appliquee:
                            if phrase not in dico_phrases_nomlg["appliquée"]:
                                dico_phrases_nomlg["appliquée"].append(phrase)
                        else: #if chemin_propre not in chemins_annotes_appliquee:
                            if phrase not in dico_phrases_nomlg["non-appliquée"]:
                                dico_phrases_nomlg["non-appliquée"].append(phrase)
    L = [[eff, mot] for mot, eff in stats.items()]
    print("10 most frequent languages : ")
    print(sorted(L)[-10:])
    return dico_phrases_nomlg


# In[3]:


from sklearn.linear_model import LogisticRegression
import time
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support

def classifiers_report(textes_en, classes_en):
    classifiers = []
    for pen in ["l1", "l2"]:
        classifiers.append(["LogReg_saga_pen=%s"%pen, 
                    LogisticRegression(multi_class="auto", solver="saga", 
                    max_iter=500, class_weight="balanced",
                    penalty = pen)])

    vectorizers=[
        ["Tfidf",TfidfVectorizer()],
        ["Count", CountVectorizer()]
    ]
    for nom_classif, algo in classifiers:
      print(nom_classif)
      for name, V in vectorizers:
        X1_en = V.fit_transform(textes_en)
        Train_V = V.fit(textes_en)
        Y1_en = classes_en
        X_train_en, X_test_en, y_train_en, y_test_en = train_test_split(X1_en, Y1_en, test_size=0.3, random_state=0)
        start = time.perf_counter()
        clf_en = algo.fit(X_train_en, y_train_en)
        end = time.perf_counter()
        print(name, "... %.2f seconds"%(round(end-start,3)))
        pred_en = clf_en.predict(X_test_en)

        conf_matrix_en = confusion_matrix(y_test_en, pred_en)
        report_en = classification_report(y_test_en,pred_en)
        print(report_en)
    return Train_V, clf_en

def resultats_conf(data_annote, names_LRE, liste_lang, Train_V, clf_en):
    stats_LRE = {}
    resultats = {}
    for conf_name, json_path in data_annote:
        print(conf_name)
        resultats[conf_name] = {"Sentence":[], "Baseline":[], "Baseline_LRE":[], "Sentence_LRE":[]}
        with open(json_path) as f:
            dic_conf = json.load(f)
        for path_article, infos_article in dic_conf.items():
            classe = infos_article["class"]
            if classe =="Non-déductible" or classe =="Non-Aplicable":
                classe="N/A"
            chaine = read_file(path_article)
            has_LRE = False
            for name in names_LRE:
                if name in chaine:
                    has_LRE = True
                    stats_LRE.setdefault(name,0)
                    stats_LRE[name]+=1
            chaine = chaine.lower()
            phrases = chaine.split(".")
            a_tester = []
            for phrase in phrases:
                for mot in phrase.split():
                    for l in liste_lang:
                        if mot == l:
                            a_tester.append(phrase)
            if len(a_tester)>0:
                pred_baseline = "Appliquée"
                pred_LRE = pred_baseline
                if classe =="Déductible":#pour avoir aussi les déductibles
                    pred_baseline = classe
                X_test2 = Train_V.transform(a_tester)
                Y_pred2 = clf_en.predict(X_test2)
            else:
                pred_baseline = "N/A"
                Y_pred2= [["N/A"]]
                if has_LRE==True:
                    pred_LRE = "Déductible"
                else:
                    pred_LRE = pred_baseline

            NB_pos = len([x for x in Y_pred2 if x== "appliquée"])
            if "appliquée" in Y_pred2:
                pred_sentence = "Appliquée"
                if classe =="Déductible":#pour avoir aussi les déductibles
                    pred_sentence = classe
            else:
                pred_sentence = "N/A"
            pred_sentence_LRE = pred_sentence
            if pred_sentence!="Appliquée":
                if pred_LRE=="Déductible":
                    pred_sentence_LRE = pred_LRE
                "Sentence_LRE"
            resultats[conf_name]["Sentence"].append([classe, pred_sentence])
            #, {"Phr_lg":len(a_tester), "Phr_lg_pos":NB_pos}])
            resultats[conf_name]["Baseline"].append([classe, pred_baseline])
            resultats[conf_name]["Baseline_LRE"].append([classe, pred_LRE])
            resultats[conf_name]["Sentence_LRE"].append([classe, pred_sentence_LRE])
    return resultats
