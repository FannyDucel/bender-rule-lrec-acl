# bender-rule-lrec-acl

The objective of this project is to verify how the Bender Rule isapplied in NLP conferences. The Bender Rule states that NLP researchers must mention explicitly the language they are working even if it is English (Bender 2011, 2019).

This repository contains all data and code to reproduce the experiments presented in Ducel *et al.* LREC 2022 and TALN 2022 (see references below).

**DATA**

We propose all annotaed datasets both in JSON and in CSV format (in the DATA/ directory):
- Three annotated a the article level:
  - DATA/420-acl_annotation_bender  : 420 annotated articles from ACL (used in both LREC and TALN articles)
  - DATA/550-lrec_annotation_bender : 550 annotated articles from LREC (used in the LREC article)
  - DATA/127-taln_annotation_bender : 127 annotated articles from TALN (used in TALN article)
- One annotated at the sentence level :
  - DATA/data_classif1_en420f.json  : ACL sentences used to train the sentence classifier mentioned in the articles

The data used for computing the inter-annotator agreement :
- accord_interannotateur2.csv

**CODE**
- classifiers_clean.ipynb : Jupyter Notebook for the LREC article (LREC VS ACL datasets)
- classifiers_clean-fr.ipynb : Jupyter Notebook for the TALN article (TALN VS ACL datasets)

**RESSOURCES**

We provide all the resources used for the above mentioned papers.

First the list of language names used :
- DATA/liste_langues_en.txt (for LREC 2022)
- DATA/liste_langues_fr.txt (for TALN 2022)
- DATA/liste_langues_de.txt (not sued yet)

Second, the list of language resources listed in LREMAP at the time of the experiments :
- DATA/corpus_lremap.json

**MISC**
- csv2json.py : transforms CSV files in JSON format

**REFERENCES**

*Do we Name the Languages we Study? The# BenderRule in LREC and ACL articles*, Fanny Ducel, Karën Fort, Gaël Lejeune and Yves Lepage, LREC 2022 [](https://hal.archives-ouvertes.fr/hal-03680561/)

*Langues «par défaut»? Analyse contrastive et diachronique des langues non citées dans les articles de TALN et d'ACL*, Fanny Ducel, Karën Fort, Gaël Lejeune and Yves Lepage, TALN 2022 [](https://hal.inria.fr/hal-03680565) 

*On achieving and evaluating language-independence in NLP*, Emily Bender, Linguistic Issues in Language Technology, 6(3), 2011

*The #BenderRule: On naming the languages we study and why it matters*, Emily Beder, The Gradient, 2019

