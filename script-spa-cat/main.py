#!/usr/bin/python3 -S
# -*- coding: utf-8 -*-

import config, sys, codecs, re, unicodedata
import xml.etree.ElementTree as ET
from collections import defaultdict

classes = ["adj", "adv", "n",  "np", "vblex", "ij"]
langs = ["spa", "cat"]
author = ""
#sys.stdin = codecs.getreader("utf-8")(sys.stdin)
#sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

def findparadigm(lang, classe, word):
   if classe == ("vblex"):
      return ""
   for e in lt_dict_root[lang+"_"+classe].iter('e'):
      if (e.attrib.get('lm') == word):
         return e.find('par').attrib.get('n')
   return ""

def guessparadigm(lang, classe, word):
   # paradigmes més freqüents
   if (lang == "spa"):
      if (classe == "adj"):
         if (word.endswith("dor")):
            return "abrumador__adj"
         if (word.endswith("o")):
            return "absolut/o__adj"
         if (word.endswith("és")):
            return "aragon/és__adj"
         if (word.endswith("ista") or word.endswith("e")):
            return "abundante__adj"
         if (word.endswith("ar") or word.endswith("al")):
            return "abdominal__adj"
         if (word.endswith("í")):
            return "marroquí__adj"
      if (classe == "vblex"):
         if word.endswith("gar"):
            return "aleg/ar__vblex"
         if word.endswith("uar"):
            return "situ/ar__vblex"
         if word.endswith("zar"):
            return "abalan/zar__vblex"
         if word.endswith("car"):
            return "ata/car__vblex"
         if word.endswith("guar"):
            return "averig/uar__vblex"
         if word.endswith("ar"):
            return "abandon/ar__vblex"
         if word.endswith("gir"):
            return "diri/gir__vblex"
         if word.endswith("uir"):
            return "atribu/ir__vblex"
         if word.endswith("ir"):
            return "abat/ir__vblex"
   if (lang == "cat"):
      if (classe == "adj"):
         if (word.endswith("dor")):
            return "absolut__adj"
         if (word.endswith("c")):
            return "acadèmi/c__adj"
         if (word.endswith("ista")):
            return "agrícol/a__adj"
         if (word.endswith("ant")):
            return "abdominal__adj"
         if (word.endswith("at") or word.endswith("it")):
            return "triparti/t__adj"
         if (word.endswith("ós")):
            return "aliment/ós__adj"
         if (word.endswith("iu")):
            return "abusi/u__adj"
      if (classe == "vblex"):
         if word.endswith("jar"):
            return "agreu/jar__vblex"
         if word.endswith("gar"):
            return "afalag/ar__vblex"
         if word.endswith("çar"):
            return "abalan/çar__vblex"
         if word.endswith("iar") or word.endswith("uar"):
            return "acarici/ar__vblex"
         if word.endswith("car"):
            return "abo/car__vblex"
         if word.endswith("ar"):
            return "abander/ar__vblex"
         if word.endswith("ir"):
            return "abarat/ir__vblex"
   return "???"

def find_paradigm2(lang, paradigm):
   paradigmlist = []
   if lang == "spa":
      if paradigm == "averigü/ar__vblex" or paradigm == "ampli/ar__vblex" or paradigm == "situ/ar__vblex":
         return "alí/ar__vblex"
      if paradigm == "atletismo__n":
         return "alrededores__n"
      if paradigm =="cuaresma__n":
         return "afueras__n"
      paradigmlist = paradigms["spa"][classe]
   if lang == "cat":
      if paradigm == "atletisme__n":
         return "afores__n"
      if paradigm =="q__n":
         return "escombraries__n"
      paradigmlist = paradigms["cat"][classe]
   #print(paradigmlist)
   for p in paradigmlist:
      psense = unicodedata.normalize('NFKD', p).encode('ASCII', 'ignore').decode("utf-8")
      #print(paradigm,p,psense)
      if paradigm == psense and p != psense:
         return p
   return ""

def accent_last_vowel(word):
   accented_vowel = {
      'a': 'á',
      'e': 'é',
      'i': 'í',
      'o': 'ó',
      'u': 'ú'
   }
   l = len(word)
   i = 0
   while i < l:
      i += 1
      if word[l - i] in 'aeiou':
         wordlist=list(word)
         wordlist[l - i] = accented_vowel[wordlist[l - i]]
         return ''.join(wordlist)
   return word

def exists(lang, classe, word):
   for e in dict_root[lang].iter('e'):
      if e.find('par') is not None:
         if (e.attrib.get('lm') == word) and e.find('par').attrib.get('n').endswith('__'+classe):
            return e.find('par').attrib.get('n')
   return ""

def exists_in_bilingual(classe, spaword, catword):
   #TODO: comprova si és en les dues bandes per separat
   for e in dict_root["spa-cat"].iter('e'):
      spaworddict=""
      catworddict=""
      if e.find('p'):
         if e.find('p').find('l'):
            if e.find('p').find('l').find('s').attrib.get('n') != classe:
               continue
            if e.find('p').find('l').text:
               spaworddict = e.find('p').find('l').text
               if e.find('p').find('l').find('g'):
                  for t in e.find('p').find('l').find('g').findall('b'):
                     spaworddict += ' ' + t.tail
            else:
               continue
         if e.find('p').find('r'):
            if e.find('p').find('r').text:
               catworddict = e.find('p').find('r').text
               if e.find('p').find('r').find('g'):
                  for t in e.find('p').find('r').find('g').findall('b'):
                     catworddict += ' ' + t.tail
            else:
               continue
            if spaword == spaworddict and catword == catworddict:
               return "sí"
      elif e.find("i"):
         if e.find("i").text == spaword and (spaword == catword) and e.find('i').find('s').attrib.get('n') == classe:
            return "sí"
   return ""

def my_stem(word, paradigma):
   #print(word, paradigma)
   if "/" not in paradigma:
      return fix_spaces(word)
   m = re.search('/(.+?)_', paradigma)
   if m:
      found = m.group(1)
      if word.endswith(found):
         return fix_spaces(word[:-len(found)])
   return "ERROR!"

def fix_spaces(word):
   return word.replace(u' ', u'<b/>')

def extract_extras(l):
   result=""
   lparts = l.strip().replace(",", " ").split(u" ")
   for lpart in lparts:
      if lpart == "m":
         result += '<s n="m"/>'
      if lpart == "f":
         result += '<s n="f"/>'
      if lpart == "mf":
         result += '<s n="mf"/>'
      if lpart == "sg":
         result += '<s n="sg"/>'
      if lpart == "pl":
         result += '<s n="pl"/>'
      if lpart == "sp":
         result += '<s n="sp"/>'
      if lpart == "GD":
         result += '<s n="GD"/>'
      if lpart == "ND":
         result += '<s n="ND"/>'
   return result

def extract_g(s, para):
   if para.startswith("multi_n"):
      return ""
   ss = s.strip()
   if ":" in ss:
      return ""
   if extract_extras(ss):
      return ""
   ss = fix_spaces(ss)
   if ss:
      return '<b/>' + ss
   return ""

def paradigm_relation(classe, paradigm_spa, paradigm_cat):
   cat_type = ""
   spa_type = ""
   if paradigm_cat in paradigms["cat"][classe]:
      cat_type = paradigms["cat"][classe][paradigm_cat]
      cat_type = cat_type.replace("-adjsupfpl-adjsupfsg-adjsupmpl-adjsupmsg", "").replace("nacr","")
   if paradigm_spa in paradigms["spa"][classe]:
      spa_type = paradigms["spa"][classe][paradigm_spa]
      spa_type = spa_type.replace("-adjsupfpl-adjsupfsg-adjsupmpl-adjsupmsg", "").replace("nacr","")
   
   if cat_type == spa_type:
         return ""
   #print(spa_type + "_" + cat_type)
   cat_type = simplify_type(cat_type)
   spa_type = simplify_type(spa_type)
   #print(spa_type + "_" + cat_type)

   relacio = spa_type + "_" + cat_type
   if relacio == "nfsg_nmsg" or relacio == "nfpl_nmpl":
      return "f_m"
   if relacio == "nmsg_nfsg" or relacio == "nmpl_nfpl":
      return "m_f"

   return spa_type + "_" + cat_type

def simplify_type (t): 
   if t == "nfpl-nfsg":
      return "f"
   if t == "nmpl-nmsg":
      return "m"
   if t == "nfpl-nfsg-nmpl-nmsg" or t == "adjfpl-adjfsg-adjmpl-adjmsg":
      return "m-f"
   if t == "nmfpl-nmfsg" or t == "adjmfpl-adjmfsg" or t == "adjmfpl-adjmfsg-adv":
      return "mf"
   if t == "nmfsp" or t == "adjmfsp":
      return "mfsp"
   if t == "nfsp":
      return "fsp"
   if t == "nmsp":
      return "msp"
   if t == "nfsg-nmfpl-nmsg" or t == "adjfsg-adjmfpl-adjmsg":
      return "addicte"
   if t == "adjfpl-adjmfsg-adjmpl":
      return "precoç"
   return(t)

def check_anomalies(classe, spapar, catpar):
   if catpar not in paradigms["cat"][classe] or spapar not in paradigms["spa"][classe]:
      return ""
   if ("adjsup" in paradigms["cat"][classe][catpar] and "adjsup" not in paradigms["spa"][classe][spapar]) or ("adjsup" not in paradigms["cat"][classe][catpar] and "adjsup" in paradigms["spa"][classe][spapar]):
      return "Un paradigma té superlatiu i l'altre no!"
   if ("nacr" in paradigms["cat"][classe][catpar] and "nacr" not in paradigms["spa"][classe][spapar]) or ("nacr" not in paradigms["cat"][classe][catpar] and "nacr" in paradigms["spa"][classe][spapar]):
      return "Un paradigma és acrònim i l'altre no!"
   return ""

def is_superlative(classe, spapar, catpar):
   if ("adjsup" in paradigms["cat"][classe][catpar] and "adjsup" in paradigms["spa"][classe][spapar]):
      return True;
   else:
      return False;

# Llegeix diccionaris existents d'Apertium
dict_root = defaultdict()
paradigms = {}
paradigms_lists = {}
for lang in langs:
   paradigms[lang]={}
   paradigms_lists[lang]={}
   for classe in classes:
      paradigms[lang][classe]={}
      paradigms_lists[lang][classe] = []

for lang in langs:
   mytree = ET.parse(config.FILES[lang+'-dict'])
   dict_root[lang] = mytree.getroot()
   for pardef in dict_root[lang].iter('pardef'):
      for classe in classes:
         if pardef.attrib.get('n').endswith('__'+classe):
            mylist = []
            if classe in ["n", "adj"]:
               mylist = []
               for e in pardef.findall('e'):
                  if e.attrib.get('r') == None:
                     sstring = ""
                     for s in e.find('p').find('r').findall('s'):
                        sstring += s.attrib.get("n")
                     mylist.append(sstring)
               mylist=list(set(mylist))
               mylist.sort()
            paradigms[lang][classe][pardef.attrib.get('n')] = "-".join(mylist)

spacat_tree = ET.parse(config.FILES['spa-cat-dict'])
dict_root["spa-cat"] = spacat_tree.getroot()

for lang in langs:
   paradigms[lang]['n']["multi_nm__n"] = "nmpl-nmsg"
   paradigms[lang]['n']["multi_nf__n"] = "nfpl-nfsg"
'''
for lang in langs:
   for classe in ["n","adj"]: 
      for key,value in paradigms[lang][classe].items():
         print (key+"\t"+value+"\n")
'''

# Imprimeix llista de paradigmes en el fitxer paradigmes.txt
for lang in langs:
   for classe in classes: 
      paradigms_lists[lang][classe] = list(paradigms[lang][classe].keys())
      paradigms_lists[lang][classe].sort(key=lambda x:unicodedata.normalize('NFKD', x.replace("/","").lower()))
maxlen = 0
for lang in langs:
   for classe in classes:
      maxlen = max (maxlen,len(paradigms_lists[lang][classe]))
filepara = codecs.open("paradigmes.txt","w", "utf-8")
filepara.write(str(len(classes))+"\n")
for lang in langs:
   for classe in classes:
      filepara.write(classe+"\t")
filepara.write("\n")
for i in range(maxlen):
   for lang in langs:
      for classe in classes:  
         if i < len(paradigms_lists[lang][classe]):
            filepara.write(paradigms_lists[lang][classe][i])
         filepara.write("\t")
   filepara.write("\n")
filepara.close()

# Llegeix altres diccionaris: LT
lt_dict_root = defaultdict()
for lang in langs:
   for classe in ["n", "adj"]:
      f = open(config.FILES[lang+"-"+classe+"-lt"],"r")
      lt_dict_root[lang+"_"+classe] = ET.fromstringlist(["<root>", f.read(), "</root>"])

# Llegeix entrada
#0 spa   1 spa-cat  2 cat   3 missatge 4 paradigma   5 paraula spa 6 <g>   7 classe   8 sentit   9 paraula cat 10 <g>   11 paradigma 12 cat/val

fspa = codecs.open("spa.txt", "w", "utf-8")
fcat = codecs.open("cat.txt", "w", "utf-8")
fspacat = codecs.open("spa-cat.txt", "w", "utf-8")
foutput = codecs.open("output.txt", "w", "utf-8")

isFirstLine = True

inputFilename=sys.argv[1] 
finput = open(inputFilename, 'r') 

for i in finput:
   if isFirstLine:
      isFirstLine = False
      continue
   i = i.replace(u"\t",u";")
   parts = i.strip().split(u";")
   #print(i)
   for i in range(len(parts)):
      parts[i]=parts[i].strip()
      parts[i]=parts[i].replace("’", "'")
   if len(parts) < 12:
      continue
   classe = parts[7]
   #print(classe)
   parts[3] = ""
   gspa = extract_g(parts[6],parts[4])
   gcat = extract_g(parts[10],parts[11])
   gspaf = ""
   gcatf = ""
   gspafb = ""
   gcatfb = ""
   if gspa:
      gspaf = '<p><l>{0}</l><r><g>{0}</g></r></p>'.format(gspa)
      gspafb = '<g>{0}</g>'.format(gspa)
   if gcat:
      gcatf = '<p><l>{0}</l><r><g>{0}</g></r></p>'.format(gcat)
      gcatfb = '<g>{0}</g>'.format(gcat)
   gspa = gspa.replace("<b/>", " ")
   gcat = gcat.replace("<b/>", " ")
   if parts[7] in classes:
      parts[1] = exists_in_bilingual(parts[7], parts[5] + gspa, parts[9] + gcat)
      if parts[7] in ["n", "adj", "vblex"]:
         p = exists("spa", parts[7], parts[5] + gspa)
         if p:
            if len(parts[4])>1 and p != parts[4]:
               parts[3] += "Conflicte paradigma Apertium spa1!"
            parts[0] = "sí"
            parts[4] = p
         else:
            p = exists("spa", parts[7], parts[5])
            if p:
               if len(parts[4])>1 and p != parts[4]:
                  parts[3] += "Conflicte paradigma Apertium spa1!"
               parts[4] = p
            else:
               parts[0] = ""
               p = findparadigm("spa", parts[7], parts[5])
               if p:
                  if len(parts[4])>1 and p != parts[4]:
                     parts[3] += "Conflicte paradigma LT spa!"
                  else:
                     parts[4] = p
               elif not parts[4]:
                  parts[4] = guessparadigm("spa", parts[7], parts[5])
         p = exists("cat", parts[7], parts[9] + gcat)   
         if p:
            if len(parts[11])>1 and p != parts[11]:
               parts[3] += "Conflicte paradigma Apertium cat1!"
            parts[2] = "sí"
            parts[11] = p
         else:
            p = exists("cat", parts[7], parts[9])
            if p:
               if len(parts[11])>1 and p != parts[11]:
                  parts[3] += "Conflicte paradigma Apertium cat1!"
               parts[11] = p
            else:
               parts[2] = ""
               p = findparadigm("cat", parts[7], parts[9])
               if p:
                  if len(parts[11])>1 and p != parts[11]:
                     parts[3] += "Conflicte paradigma LT cat!"
                  else:
                     parts[11] = p
               elif not parts[11]:
                  parts[11] = guessparadigm("cat", parts[7], parts[9])
      if parts[7] in ["adv"]:
         p = exists("spa", parts[7], parts[5])
         if p:
            parts[0] = "sí"
            parts[4] = p
         else:
            parts[4] = "ahora__adv"
         p = exists("cat", parts[7], parts[9])   
         if p:
            parts[2] = "sí"
            parts[11] = p
         else:
            parts[11] = "ahir__adv"
      if parts[7] in ["np"]:
         p = exists("spa", parts[7], parts[5])
         if p:
            parts[0] = "sí"
            parts[4] = p
         elif not parts[4]:
            parts[4] = "???"
         p = exists("cat", parts[7], parts[9])   
         if p:
            parts[2] = "sí"
            parts[11] = p
         elif not parts[11]:
            parts[11] = "???"
   else:
      parts[3] += "Classe gramatical incorrecta. "


   # Escriu eixida
   if parts[7] in classes:
      if parts[4] not in paradigms["spa"][parts[7]] and parts[4] != "???":
         parts[3] += "Paradigma spa erroni! "
      if parts[11] not in paradigms["cat"][parts[7]] and parts[11] != "???":
         parts[3] += "Paradigma cat erroni! "
      parts[3] += check_anomalies(parts[7], parts[4], parts[11])
      authorformated = ''
      if author:
         authorformated = ' a="{0}"'.format(author)
      if not parts[0] and parts[5]:
         spacenumber = 16 - len(authorformated) - len(parts[5]) - len(gspa)
         if spacenumber < 0:
            spacenumber = 0
         myparadigm = parts[4]
         if myparadigm == "multi_nm__n":
            myparadigm = "atletismo__n"
         elif myparadigm == "multi_nf__n":
            myparadigm = "cuaresma__n"
         fspa.write(u'<e lm="{1}{6}"{0}>{4}<i>{2}</i><par n="{3}"/>{5}</e>\n'.format(authorformated, parts[5], my_stem(parts[5],myparadigm), myparadigm, ' '*spacenumber, gspaf, gspa))
         if parts[7] == "vblex":
            p2 = find_paradigm2("spa",myparadigm)
            parts[3] += p2
            if p2:
               fspa.write(u'<e lm="{1}{6}"{0}>{4}<p><l>{7}</l><r>{2}</r></p><par n="{3}"/>{5}</e>\n'.format(authorformated, parts[5], my_stem(parts[5],p2) , p2, ' '*spacenumber, gspaf, gspa, accent_last_vowel(my_stem(parts[5],p2))))     
         elif parts[4].startswith("multi_n"):
            if fix_spaces(parts[6]) == "":
               parts[3] += "Forma de plural spa buida!"
            p2 = find_paradigm2("spa",myparadigm)
            parts[3] += p2
            if p2:
               fspa.write(u'<e lm="{1}{6}"{0}>{4}<p><l>{7}</l><r>{2}</r></p><par n="{3}"/>{5}</e>\n'.format(authorformated, parts[5], my_stem(parts[5],p2) , p2, ' '*spacenumber, gspaf, gspa, fix_spaces(parts[6])))     
      m = re.search(':(.+)', parts[6])
      if m and parts[5]:
         secondform = m.group(1)
         spacenumber = 16 - 7 - len(authorformated) - len(parts[5]) - len(gspa)
         fspa.write(u'<e lm="{1}"{0} r="LR">{4}<p><l>{6}</l><r>{2}</r></p><par n="{3}"/>{5}</e>\n'.format(authorformated, parts[5], my_stem(parts[5],parts[4]) , parts[4], ' '*spacenumber, gspaf, my_stem(secondform,parts[4])))
         if parts[7]== "vblex":
            p2 = find_paradigm2("spa",parts[4])
            parts[3] += p2
            if p2:
               fspa.write(u'<e lm="{1}{6}"{0} r="LR">{4}<p><l>{7}</l><r>{2}</r></p><par n="{3}"/>{5}</e>\n'.format(authorformated, parts[5], my_stem(parts[5],p2) , p2, ' '*spacenumber, gspaf, gspa, accent_last_vowel(my_stem(secondform,p2))))     
      
      isCatval = False
      catvalVer1 = ""
      catvalVer2 = ""
      if ":val:" in parts[10]:
         isCatval = True
         catvalVer1 = ' v="cat"'
         catvalVer2 = ' v="val_gva val_uni"'

      if not parts[2] and parts[9]:
         spacenumber = 16 - len(authorformated) - len(parts[9]) - len(gcat) - len(catvalVer1)
         if spacenumber < 0:
            spacenumber = 0
         myparadigm = parts[11]
         if myparadigm == "multi_nm__n":
            myparadigm = "atletisme__n"
         elif myparadigm == "multi_nf__n":
            myparadigm = "q__n"
         fcat.write(u'<e lm="{1}{6}"{7}{0}>{4}<i>{2}</i><par n="{3}"/>{5}</e>\n'.format(authorformated, parts[9], my_stem(parts[9],myparadigm), myparadigm, ' '*spacenumber, gcatf, gcat, catvalVer1))
         if parts[11].startswith("multi_n"):
            if fix_spaces(parts[10]) == "":
               parts[3] += "Forma de plural cat buida!"
            p2 = find_paradigm2("cat",myparadigm)
            parts[3] += p2
            if p2:
               fcat.write(u'<e lm="{1}{6}"{0}>{4}<p><l>{7}</l><r>{2}</r></p><par n="{3}"/>{5}</e>\n'.format(authorformated, parts[9], my_stem(parts[9],p2) , p2, ' '*spacenumber, gcatf, gspa, fix_spaces(parts[10])))     
      m = re.search(':(.+)', parts[10])
      if m and parts[9]:
         secondform = m.group(1)
         secondform = secondform.replace("val:","")  
         if catvalVer2 == "":
            catvalVer2 = ' r="LR"'
         spacenumber = 16 -7 - len(authorformated) - len(parts[9]) - len(gcat) - len(catvalVer2)
         fcat.write(u'<e lm="{1}"{0}{7}>{4}<p><l>{6}</l><r>{2}</r></p><par n="{3}"/>{5}</e>\n'.format(authorformated, parts[9], my_stem(parts[9],parts[11]) , parts[11], ' '*spacenumber, gcatf, my_stem(secondform,parts[11]),catvalVer2))
      
      #Escriu bilingüe
      if not parts[1] and parts[5] and parts[9]:
         relacio = paradigm_relation(parts[7], parts[4], parts[11])
         parts[3] += relacio
         if (not relacio) or relacio == "m_f" or relacio == "f_m":
            if parts[8] == '<':
               entrada = '<e r="RL">'
            elif parts[8] == '>':
               entrada = '<e r="LR">'
            else:
               entrada = '<e>       '
            if parts[12]:
               entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
            extraspa = extract_extras(parts[6])
            extracat = extract_extras(parts[10])
            if not extraspa and not extracat:
               if relacio == "f_m":
                  extraspa = '<s n="f"/>'
                  extracat = '<s n="m"/>'
               if relacio == "m_f":
                  extraspa = '<s n="m"/>'
                  extracat = '<s n="f"/>'
            spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
            fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         elif relacio == 'mf_m-f':
            if parts[8] != '<':
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="mf"/>'
               extracat = '<s n="GD"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
            if parts[8] != '>':
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="mf"/>'
               extracat = '<s n="m"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="mf"/>'
               extracat = '<s n="f"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         elif relacio == 'm-f_mf': 
            if parts[8] != '>':
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="GD"/>'
               extracat = '<s n="mf"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
            if parts[8] != '<':
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="m"/>'
               extracat = '<s n="mf"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="f"/>'
               extracat = '<s n="mf"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         elif relacio == "m-f_mfsp":
            if parts[8] != '<':
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = ''
               extracat = '<s n="mf"/><s n="sp"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
            if parts[8] != '>':
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="GD"/><s n="ND"/>'
               extracat = '<s n="mf"/><s n="sp"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         elif relacio == "mf_mfsp":
            if parts[8] != '<':
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = ''
               extracat = '<s n="mf"/><s n="sp"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
            if parts[8] != '>':
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="mf"/><s n="ND"/>'
               extracat = '<s n="mf"/><s n="sp"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         elif relacio == "fsp_f" or relacio == "msp_m" or relacio == "fsp_m" or relacio == "msp_f": #dosis, éxtasis
            if relacio.startswith("f"):
               generespa = '<s n="f"/>'
            else:
               generespa = '<s n="m"/>'
            if relacio.endswith("f"):
               generecat = '<s n="f"/>'
            else:
               generecat = '<s n="m"/>'
            if parts[8] != '<':
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = generespa + '<s n="sp"/>'
               extracat = generecat + '<s n="ND"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
            if parts[8] != '>':
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = generespa + '<s n="sp"/>'
               extracat = generecat + '<s n="sg"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = generespa + '<s n="sp"/>'
               extracat = generecat + '<s n="pl"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         elif relacio == "mfsp_m-f":
            if parts[8] != '>':
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="mf"/><s n="sp"/>'
               extracat = ''
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
            if parts[8] != '<':
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="mf"/><s n="sp"/>'
               extracat = '<s n="GD"/><s n="ND"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         elif relacio == "mfsp_mf":
            if parts[8] != '>':
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="mf"/><s n="sp"/>'
               extracat = ''
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
            if parts[8] != '<':
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = '<s n="mf"/><s n="sp"/>'
               extracat = '<s n="mf"/><s n="ND"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))         
         elif relacio == "f_fsp" or relacio == "m_msp" or relacio == "f_msp" or relacio == "m_fsp": #campus, càries
            if relacio.startswith("f"):
               generespa = '<s n="f"/>'
            else:
               generespa = '<s n="m"/>'
            if relacio.endswith("fsp"):
               generecat = '<s n="f"/>'
            else:
               generecat = '<s n="m"/>'
            if parts[8] != '<':
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = generespa + '<s n="sg"/>'
               extracat = generecat + '<s n="sp"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
               entrada = '<e r="LR">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = generespa + '<s n="pl"/>'
               extracat = generecat + '<s n="sp"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
            if parts[8] != '>':
               entrada = '<e r="RL">'
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = generespa + '<s n="ND"/>'
               extracat = generecat + '<s n="sp"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         elif relacio == 'm-f_addicte':
            versiof = ''
            if parts[12]:
               versiof = ' vr="'+parts[12]+'"'
            if parts[8] == '<':
               fspacat.write((u'<e r="RL"{3}><p><l>{0}<s n="{2}"/><s n="m"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="m"/><s n="sg"/></r></p></e>\n'+
   '<e r="RL"{3}><p><l>{0}<s n="{2}"/><s n="f"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="f"/><s n="sg"/></r></p></e>\n'+
   '<e r="RL"{3}><p><l>{0}<s n="{2}"/><s n="GD"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="pl"/></r></p></e>\n').format(fix_spaces(parts[5]),fix_spaces(parts[9]),parts[7],versiof))
            elif parts[8] == '>':
               fspacat.write((u'<e r="LR"{3}><p><l>{0}<s n="{2}"/><s n="m"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="m"/><s n="sg"/></r></p></e>\n'+
   '<e r="LR"{3}><p><l>{0}<s n="{2}"/><s n="f"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="f"/><s n="sg"/></r></p></e>\n'+
   '<e r="LR"{3}><p><l>{0}<s n="{2}"/><s n="m"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="pl"/></r></p></e>\n'+
   '<e r="LR"{3}><p><l>{0}<s n="{2}"/><s n="f"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="pl"/></r></p></e>\n').format(fix_spaces(parts[5]),fix_spaces(parts[9]),parts[7],versiof))
            else:
               fspacat.write((u'<e>       <p><l>{0}<s n="{2}"/><s n="m"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="m"/><s n="sg"/></r></p></e>\n'+
   '<e{3}>       <p><l>{0}<s n="{2}"/><s n="f"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="f"/><s n="sg"/></r></p></e>\n'+
   '<e r="LR"{3}><p><l>{0}<s n="{2}"/><s n="m"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="pl"/></r></p></e>\n'+
   '<e r="LR"{3}><p><l>{0}<s n="{2}"/><s n="f"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="pl"/></r></p></e>\n'+
   '<e r="RL"{3}><p><l>{0}<s n="{2}"/><s n="GD"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="pl"/></r></p></e>\n').format(fix_spaces(parts[5]),fix_spaces(parts[9]),parts[7],versiof))
            if is_superlative(parts[7], parts[4], parts[11]):
               if parts[8] == '<':
                  entrada = '<e r="RL">'
               elif parts[8] == '>':
                  entrada = '<e r="LR">'
               else:
                  entrada = '<e>       '
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = extract_extras(parts[6])
               extracat = extract_extras(parts[10])
               if not extraspa and not extracat:
                  if relacio == "f_m":
                     extraspa = '<s n="f"/>'
                     extracat = '<s n="m"/>'
                  if relacio == "m_f":
                     extraspa = '<s n="m"/>'
                     extracat = '<s n="f"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/><s n="sup"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/><s n="sup"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         elif relacio == 'mf_addicte':
            versiof = ''
            if parts[12]:
               versiof = ' vr="'+parts[12]+'"'
            if parts[8] != '>':
               fspacat.write((u'<e r="RL"{3}><p><l>{0}<s n="{2}"/><s n="mf"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="m"/><s n="sg"/></r></p></e>\n'+
   '<e r="RL"{3}><p><l>{0}<s n="{2}"/><s n="mf"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="f"/><s n="sg"/></r></p></e>\n'+
   '<e r="RL"{3}><p><l>{0}<s n="{2}"/><s n="mf"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="pl"/></r></p></e>\n').format(fix_spaces(parts[5]),fix_spaces(parts[9]),parts[7],versiof))
            if parts[8] != '<':
               fspacat.write((u'<e r="LR"{3}><p><l>{0}<s n="{2}"/><s n="mf"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="GD"/><s n="sg"/></r></p></e>\n'+
   '<e r="LR"{3}><p><l>{0}<s n="{2}"/><s n="mf"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="pl"/></r></p></e>\n').format(fix_spaces(parts[5]),fix_spaces(parts[9]),parts[7],versiof))
            if is_superlative(parts[7], parts[4], parts[11]):
               if parts[8] == '<':
                  entrada = '<e r="RL">'
               elif parts[8] == '>':
                  entrada = '<e r="LR">'
               else:
                  entrada = '<e>       '
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = extract_extras(parts[6])
               extracat = extract_extras(parts[10])
               if not extraspa and not extracat:
                  if relacio == "f_m":
                     extraspa = '<s n="f"/>'
                     extracat = '<s n="m"/>'
                  if relacio == "m_f":
                     extraspa = '<s n="m"/>'
                     extracat = '<s n="f"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/><s n="sup"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/><s n="sup"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         
         elif relacio == 'mf_precoç':
            versiof = ''
            if parts[12]:
               versiof = ' vr="'+parts[12]+'"'
            if parts[8] == '<':
               fspacat.write((u'<e r="RL"><p><l>{0}<s n="{2}"/><s n="mf"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="f"/><s n="pl"/></r></p></e>\n'+
   '<e r="RL"><p><l>{0}<s n="{2}"/><s n="mf"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="m"/><s n="pl"/></r></p></e>\n'+
   '<e r="RL"><p><l>{0}<s n="{2}"/><s n="mf"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="sg"/></r></p></e>\n').format(fix_spaces(parts[5]),fix_spaces(parts[9]),parts[7],versiof))
            elif parts[8] == '>':
               fspacat.write((u'<e r="LR"><p><l>{0}<s n="{2}"/><s n="mf"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="GD"/><s n="pl"/></r></p></e>\n'+
   '<e r="LR"><p><l>{0}<s n="{2}"/><s n="mf"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="sg"/></r></p></e>\n').format(fix_spaces(parts[5]),fix_spaces(parts[9]),parts[7],versiof))
            else:
               fspacat.write((u'<e r="LR"><p><l>{0}<s n="{2}"/><s n="mf"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="GD"/><s n="pl"/></r></p></e>\n'+
   '<e r="RL"><p><l>{0}<s n="{2}"/><s n="mf"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="f"/><s n="pl"/></r></p></e>\n'+
   '<e r="RL"><p><l>{0}<s n="{2}"/><s n="mf"/><s n="pl"/></l><r>{1}<s n="{2}"/><s n="m"/><s n="pl"/></r></p></e>\n'+
   '<e>       <p><l>{0}<s n="{2}"/><s n="mf"/><s n="sg"/></l><r>{1}<s n="{2}"/><s n="mf"/><s n="sg"/></r></p></e>\n').format(fix_spaces(parts[5]),fix_spaces(parts[9]),parts[7],versiof))
            if is_superlative(parts[7], parts[4], parts[11]):
               if parts[8] == '<':
                  entrada = '<e r="RL">'
               elif parts[8] == '>':
                  entrada = '<e r="LR">'
               else:
                  entrada = '<e>       '
               if parts[12]:
                  entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
               extraspa = extract_extras(parts[6])
               extracat = extract_extras(parts[10])
               if not extraspa and not extracat:
                  if relacio == "f_m":
                     extraspa = '<s n="f"/>'
                     extracat = '<s n="m"/>'
                  if relacio == "m_f":
                     extraspa = '<s n="m"/>'
                     extracat = '<s n="f"/>'
               spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
               fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/><s n="sup"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/><s n="sup"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         



         else:
            parts[3] += "Revisar!!"
            if parts[4] in paradigms["spa"][parts[7]] and parts[11] in paradigms["cat"][parts[7]] and paradigms["spa"][parts[7]][parts[4]] != paradigms["cat"][parts[7]][parts[11]]:
               parts[3] += "Els paradigms no encaixen! "

            if parts[8] == '<':
               entrada = 'REVISAR!!<e r="RL">'
            elif parts[8] == '>':
               entrada = 'REVISAR!!<e r="LR">'
            else:
               entrada = 'REVISAR!!<e>       '
            if parts[12]:
               entrada = entrada.replace('>', ' vr="'+parts[12]+'">')
            extraspa = extract_extras(parts[6])
            extracat = extract_extras(parts[10])
            spacenumber = 23 - len(fix_spaces(parts[5])) - len(fix_spaces(parts[7])) - len(extraspa)
            fspacat.write(u'{0}<p><l>{1}{8}<s n="{2}"/>{3}</l>{4}<r>{5}{9}<s n="{6}"/>{7}</r></p></e>\n'.format(entrada, fix_spaces(parts[5]), parts[7], extraspa, ' '*spacenumber,fix_spaces(parts[9]),parts[7],extracat,gspafb,gcatfb))
         
   foutput.write(u"\t".join(parts))
   foutput.write(u"\n")

finput.close()
