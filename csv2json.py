import json
import sys
import re
def clean_dic(dic):
  dic["Titre"] = re.sub("XX", ", ", dic["Titre"])
  for classe in ["Non-Aplicable","Appliquée","Déductible","Non-déductible"]:
    if dic[classe]!="":
      if "class"in dic:
        print(dic["Titre"])
        print("error, déjà une classe")
        1/0
      dic["class"] = classe
  if classe not in dic:
      print(dic["Titre"])
      print("error, pas de classe")
      1/0
  return dic

path = sys.argv[1]

with open(path) as f:
  lignes = f.readlines()
print(len(lignes)-1, "instances")
entetes2 = re.split(",", re.sub("\n", "", lignes[0]))
dic_entetes = {}
for cpt, el in enumerate(entetes2):
    if len(el)==0:
      pass
    dic_entetes[cpt] = el
dic_out = {}
import os
for l in lignes[1:]:
  l = re.sub(", ", "XX", l)
  elems = re.split(",", l)
  dic= {dic_entetes[cpt]:elems[cpt] for cpt in range(len(elems))}
  dic = clean_dic(dic)
  if "lrec" in path:
    conf = "lrec_annotes2"
  elif "acl" in path:
    conf = "acl"
  annee = dic["Année"]
  filename = re.split("/", dic["URL"])[-1]
  filename = re.sub("\.pdf", ".txt", filename)
  ID = f"{conf}/{annee}/{filename}"
  if os.path.exists(ID) == False:
    if os.path.exists(ID.lower()):
      ID = ID.lower()
    else:
      print(ID, "missing")
      continue
  dic_out[ID] = dic
path_out = re.sub("csv", "json", path)
if path==path_out:
  print("error with file names")
  1/0
print("NB instances", len(dic_out))
for class_name in ["Non-Aplicable","Appliquée","Déductible","Non-déductible"]:
  print(class_name, len([x for x in dic_out if dic_out[x]["class"]==class_name]))
import json
with open(path_out, "w") as w:
  w.write(json.dumps(dic_out, indent=2, ensure_ascii=False))
