import bs4
import csv
import gensim
import numpy as np
import csv
import pandas as pd
import json
import re



"Import XML file"
def make_text(file):
    #text_list=文書のリスト
    #corpus:コーパス
    #dictionary:単語とid
    soup = bs4.BeautifulSoup(open(file,encoding='utf-8'), 'xml')
    abs = soup.find("text").find_all("ab")
    text_list = []
    for n_abs in abs:
        text = []
        select_words = n_abs.find_all(["name","seg","rs"])
        for s in select_words:
            if "seg" in str(s):
                tx = s.text.replace(" ", "").replace("\n", "")
                text.append(tx)
            else:
                role = s["ref"]
                if "none" not in role:
                    #noneの場合何もしない
                    tx = role.replace("#","")
                    text.append(tx)
        text_list.append(text)

    dictionary = gensim.corpora.Dictionary(text_list)
    corpus = [dictionary.doc2bow(text) for text in text_list]

    #make time list
    time_list = []
    time_abs = soup.find('text').find_all('head')
    for t_abs in time_abs:
        time_list.append(t_abs.text.replace(" ", "").replace("\n", ""))

    return text_list, time_list, dictionary, corpus


"make chara list"
def make_chara(file):
    #chara_list:登場人物のリスト
    person = pd.read_csv(file)
    person_label = person['Label']
    chara = person_label[~person_label.duplicated()]
    chara = chara.reset_index(drop=True)
    chara_list = []
    for i in range(len(chara)):
        chara_list.append(chara[i].split('、')[0])
        if "、" in chara[i]:
            chara_list.append(chara[i].split('、')[1]+chara[i].split('、')[0])
    return chara_list

def get_name(x):
  split = x.split("、")
  answer = x
  if len(split) == 2:
    answer = split[1] + split[0]
  return answer

def get_first_name(x):
  split = x.split("、")
  answer = x
  if len(split) == 2:
    answer = split[0]
  return answer

def get_family_name(x):
  split = x.split("、")
  answer = x
  if len(split) == 2:
    answer = split[1]
  return answer

#copy from https://wtnvenga.hatenablog.com/entry/2018/05/27/113848
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)

def ngram_count(text, all_word_list):
    #単語ないで一番頻度が高い単語を抽出
    leng = len(text)
    max_count = 10
    ini_index =0
    bow_list =[]
    for i in range(leng-3):
        n_count = all_word_list.count(text[i:i+3])
        if n_count >= 3:
            bow_list.append(text[i:i+3])
    return bow_list
def ngram2_count(text, all_word_list):
    #単語ないで一番頻度が高い単語を抽出
    leng = len(text)
    max_count = 10
    ini_index =0
    bow_list =[]
    for i in range(leng-3):
        n_count = all_word_list.count(text[i:i+2])
        if n_count >= 3:
            bow_list.append(text[i:i+2])
    return bow_list

def remove_unrelated(word_list):
    new_text_list = []
    for words in word_list:
        s1 = words.replace("〈", "")
        s2 = s1.replace("〉", "")
        new_text_list.append(s2)
    return new_text_list

def fix_xml(word_list):
    words_list = []
    for words in word_list:
        l = re.split('[、\u3000」・「  ]',words)
        tmp = [i for i in l if not len(i) == 0]
        while '  'in tmp:
            tmp.remove('  ')
        words_list.append(tmp)
        #その前に()がある場所で要素を分割したい
    new_words_lists = []
    for words in words_list:
        new_words_list = []
        for w in words:
            if '（' in w:
                s = re.findall(".*?）",w)
                for s_w in s:
                    new_words_list.append(s_w)
            else:
                new_words_list.append(w)
        new_words_lists.append(new_words_list)
    return new_words_lists

#名前だけのものをすべて苗字まで含め()で囲う
def revise_wordlist(text_list):
    chara = chara_list['name']
    for i,c in enumerate(chara):
        for j,text in enumerate(text_list):
            for k,t in enumerate(text):
                if c in t:
                    if not pattern1[i] is None:
                        if pattern1[i] in t:
                            text_list[j][k] = t.replace(pattern1[i], '（' + full_name[i]+'）')
                        elif not full_name[i] in t:
                            if not '（' in t:
                                text_list[j][k] = t.replace(c, '（' + full_name[i]+'）')
    return text_list
