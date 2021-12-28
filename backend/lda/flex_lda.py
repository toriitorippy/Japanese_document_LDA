
import bs4
import csv
import gensim
import csv
import pandas as pd
import sys
import json
sys.path.append('../public')
# from lda.constants  import *
from collections import Counter
from lda.my_modules import *
import codecs
import re
import sentencepiece as spm


#FLDAはFlex_LDAの略
class FLDA:
    def __init__(self, num_topics, random_state, xml_file, csv_file):
        self.num_topics = num_topics
        self.iterations = 300
        self.passes = 50
        self.random_state = 0 #後で変えられるようにする
        self.time_list = [] #修正
        self.make_csv=False
        self.make_json=True
        #ファイル読み込み
        xml_file_path = './data/xml/' + xml_file
        csv_file_path = './data/csv/' + csv_file
        soup = bs4.BeautifulSoup(open(xml_file_path,encoding='utf-8'), 'xml')
        abs = soup.find("text").find_all("ab")
        self.text_list = []
        for n_abs in abs:
            self.text_list.append(n_abs.get_text().replace("\u3000",""))
        csv_input = pd.read_csv(filepath_or_buffer=csv_file_path, sep=",")
        csv_input = csv_input[:8681]
        s = csv_input["人名"]
        print(s)
        csv_input["name"] = s.map(get_name)
        csv_input["first_name"] = s.map(get_first_name)
        csv_input["family_name"] = s.map(get_family_name)
        bow = []
        new_text = []
        first_name = csv_input["first_name"]
        name = csv_input["name"]
        family_name = csv_input["family_name"]
        self.chara_list= name
        kani = csv_input["注記（官職　表記など）"]
        for i in range(len(self.text_list)):
            this_bow = []
            text = self.text_list[i]
            for j in range(len(csv_input)):
                if first_name[j] in self.text_list[i]:
                    text = text.replace(first_name[j], "")
                if name[j] not in this_bow:
                    this_bow.append(name[j])
                if family_name[j] in self.text_list[i]:
                    text = text.replace(family_name[j], "")
                if type(kani[j]) == str:
                    kani_list = kani[j].split(" ")
                for k in kani_list:
                    if k in self.text_list[i]:
                        text = text.replace(k, "")
                    if name[j] not in this_bow:
                        this_bow.append(name[j])
            new_text.append(text)
            bow.append(this_bow)
        person_bow = bow #一旦人物だけ回避
        # 学習の実行
        print(*new_text, sep="\n", file=codecs.open("./data/new/word_list.txt", "w", "utf-8"))
        spm.SentencePieceTrainer.Train(
        '--input=./data/new/word_list.txt --model_prefix=sentencepiece --vocab_size=8000 --character_coverage=0.9995'
        )
        sp = spm.SentencePieceProcessor()
        sp.Load("./data/model/sentencepiece.model")
        remove = ["一","ニ","三","四","五","六","七","九","十","日","八","▁","「",")","〉","、"]
        word_bow = []
        for i in range(len(new_text)):
            this_word = []
            aaa = sp.EncodeAsPieces(self.text_list[i])
            for w in aaa:
                if len(w) >= 2:
                    flag = True
                for r in remove:
                    if r in w:
                        flag = False
                if flag:
                    this_word.append(w)
            word_bow.append(this_word)
        new_bow = []
        for i in range(len(person_bow)):
            new_bow.append(person_bow[i]+word_bow[i])
        self.text_list = new_bow
        dictionary = gensim.corpora.Dictionary(new_bow)
        corpus = [dictionary.doc2bow(text) for text in new_bow]
        self.dictionary = dictionary
        self.corpus = corpus


    #lda実行
    def run_LDA(self):
        print("run lda")
        lda = gensim.models.ldamodel.LdaModel(
            corpus=self.corpus,
            num_topics=self.num_topics,
            id2word=self.dictionary,
            iterations=self.iterations,
            passes=self.passes,
            random_state=self.random_state,
            per_word_topics=True #文書何の単語のトピックを抽出するか
        )
        lda.save('./data/model/{}_lda'.format(self.num_topics))
        return lda
    
    def get_result(self):
        #run lda
        lda = gensim.models.ldamodel.LdaModel.load('./data/model/{}_lda'.format(self.num_topics))
        # lda = self.run_LDA()
        #wordとrateのリストを返す
        top_chara_list = []
        top_words_list = []
        for k in range(self.num_topics):
            tmp_list = []
            tmp2_list=[]
            x = lda.show_topic(k,1000)
            for i in range(1000):
                if x[i][0] in self.chara_list:
                    tmp_list.append(x[i])
                else:
                    tmp2_list.append(x[i])
            top_chara_list.append(tmp_list)
            top_words_list.append(tmp2_list)
        lda_document = lda.get_document_topics(bow=self.corpus, minimum_probability=0, minimum_phi_value=None, per_word_topics=True)

        if self.make_csv:
            #人物と単語の上位30単語出力(select=0)
            self.make_top_data(0,top_chara_list,top_words_list)
            #人物と単語の上位30数値(select=1)
            self.make_top_data(1,top_chara_list,top_words_list)
            #文書ごとのトピックの割合
            self.per_document_topic(lda_document)
            #年号ごとのトピックの割合
            self.per_nengo_topic(lda_document)
            #めんどくさいのでここからはcsvでやらない
            # #単語ごとのトピックの割合
            # self.per_word_topic()
            # #トピックごとの文書の割合
            # self.per_topic_term()
            # #文書ごとの単語整形

        if self.make_json:
            # 人物と単語の上位30単語出力
            self.make_top_data_json(top_chara_list,top_words_list)
            #lda_document保存
            self.make_document_json(lda_document)
            #単語ごとのトピック割合
            self.per_word_topic_json(lda)
            #年号ごとのトピックの割合
            # self.per_document_topic_json(lda_document)


    "for make csv function"
    def make_top_data(self,select,top_chara_list,top_words_list):
        topic = []
        for j in range(30):
            tmp_list = []
            for i in range(self.num_topics):
                tmp_list.append(top_chara_list[i][j][select])
                tmp_list.append(top_words_list[i][j][select])
            topic.append(tmp_list)
        #csvの保存方法を整えておく
        if select == 0:
            with open('./data/csv/0120/{}_topics_word.csv'.format(self.num_topics), 'w', newline="") as f:
                writer = csv.writer(f)
                writer.writerows(topic)
        if select == 1:
            with open('./data/csv/0120/{}_topics_word_rate.csv'.format(self.num_topics), 'w', newline="") as f:
                writer = csv.writer(f)
                writer.writerows(topic)

    def per_document_topic(self,lda_document):
        document_list = []
        for d in range(len(self.text_list)):
            document_list.append([lda_document[d][0][i][1] for i in range(self.num_topics)])
        with open('./data/csv/0120/{}_document_topic.csv'.format(self.num_topics), 'w', newline="") as f:
            writer = csv.writer(f)
            writer.writerows(document_list)

    def per_nengo_topic(self,lda_document):
        nengo_list = []
        for time in self.time_list:
            if '年' in time:
                nengo = str(time).split('年')[0] + '年'
                if nengo not in nengo_list:
                    nengo_list.append(nengo)
        nengo_list.remove('年')
        kamakura_time_list = ['建久','嘉禄','安貞','寛喜','貞永','天福','文暦','嘉禎','暦仁','延応','仁治','寛元','宝治','建長','康元','正嘉','正元','文応','弘長','文永','建治','弘安','正応','永仁','正安','乾元','嘉元','徳治','延慶','応長','正和','文保','元応','元亨','正中','嘉暦','元徳','元弘','正慶','延元','貞和','延文','康応','応永','大永','天文','文明']
        nengo_true_list = [[]]*len(kamakura_time_list)
        nengo_index =[0]*len(nengo_list)
        for i in range(len(nengo_list)):
            gou = nengo_list[i][0] + nengo_list[i][1]
            gou_index = kamakura_time_list.index(gou)
            nengo_index[i] = gou_index
        true_nengo_list = []
        for i in range(46):
            tmp_nengo_list = []
            for j in range(len(nengo_index)):
                if nengo_index[j] ==i:
                    tmp_nengo_list.append(nengo_list[j])
            newlist = sorted(tmp_nengo_list)
            true_nengo_list += newlist
        number_of_nengo_list = [0]*len(true_nengo_list)
        for i in range(len(self.time_list)):
            try:
                nengo_str = str(self.time_list[i]).split('年')[0] + '年'
                number_of_nengo_list[true_nengo_list.index(nengo_str)] += 1
            except:
                print(self.time_list[i])
        all_topic_rate = []
        for k in range(len(true_nengo_list)):
            num = 0
            topic_rate=[0]*self.num_topics 
            for i in range(len(self.time_list)):
                if true_nengo_list[k] in self.time_list[i]:
                    if not lda_document[i][0][0][1] == lda_document[i][0][1][1] :
                        num += 1
                        for j in range(self.num_topics):
                            topic_rate[j] += lda_document[i][0][j][1]
            if not num ==0:
                all_topic_rate.append([w/num for w in topic_rate])
            else:
                all_topic_rate.append([w for w in topic_rate])
        with open('./data/csv/0120/{}_nengo_topic.csv'.format(self.num_topics), 'w', newline="",encoding='shift_jis') as f:
            writer = csv.writer(f, lineterminator="\n") # writerオブジェクトの作成 改行記号で行を区切る
            writer.writerows(all_topic_rate) 

    "for make json function"
    def make_top_data_json(self,top_chara_list,top_words_list):
        data_dict = {"chara":top_chara_list,"words":top_words_list}
        with open('./data/json/{}_lda_top.json'.format(self.num_topics), 'w') as f:
            json.dump(data_dict, f,cls = MyEncoder)
    
    def make_document_json(self,lda_document):
        doc_dict = {}
        for i in range(len(lda_document)):
            doc_dict[i] = lda_document[i]
        with open('./data/json/{}_doc.json'.format(self.num_topics), 'w') as f:
            json.dump(doc_dict, f,cls = MyEncoder)

    def per_word_topic_json(self,lda):
        word_dict = {}
        for i in range(len(self.dictionary)):
            word_dict[self.dictionary[i]] = lda.get_document_topics(self.dictionary.doc2bow([self.dictionary[i]]))
        with open('./data/json/{}_per_word.json'.format(self.num_topics), 'w') as f:
            json.dump(word_dict, f,cls = MyEncoder)

    def per_document_topic_json(self,lda_document):
        nengo_list = []
        for time in self.time_list:
            if '年' in time:
                nengo = str(time).split('年')[0] + '年'
                if nengo not in nengo_list:
                    nengo_list.append(nengo)
        nengo_list.remove('年')
        kamakura_time_list = ['建久','嘉禄','安貞','寛喜','貞永','天福','文暦','嘉禎','暦仁','延応','仁治','寛元','宝治','建長','康元','正嘉','正元','文応','弘長','文永','建治','弘安','正応','永仁','正安','乾元','嘉元','徳治','延慶','応長','正和','文保','元応','元亨','正中','嘉暦','元徳','元弘','正慶','延元','貞和','延文','康応','応永','大永','天文','文明']
        nengo_true_list = [[]]*len(kamakura_time_list)
        nengo_index =[0]*len(nengo_list)
        for i in range(len(nengo_list)):
            gou = nengo_list[i][0] + nengo_list[i][1]
            gou_index = kamakura_time_list.index(gou)
            nengo_index[i] = gou_index
        true_nengo_list = []
        for i in range(46):
            tmp_nengo_list = []
            for j in range(len(nengo_index)):
                if nengo_index[j] ==i:
                    tmp_nengo_list.append(nengo_list[j])
            newlist = sorted(tmp_nengo_list)
            true_nengo_list += newlist
        number_of_nengo_list = [0]*len(true_nengo_list)
        for i in range(len(self.time_list)):
            try:
                nengo_str = str(self.time_list[i]).split('年')[0] + '年'
                number_of_nengo_list[true_nengo_list.index(nengo_str)] += 1
            except:
                print(self.time_list[i])
        all_topic_rate = {}
        for k in range(len(true_nengo_list)):
            num = 0
            topic_rate=[0]*self.num_topics 
            for i in range(len(self.time_list)):
                if true_nengo_list[k] in self.time_list[i]:
                    if not lda_document[i][0][0][1] == lda_document[i][0][1][1] :
                        num += 1
                        for j in range(self.num_topics):
                            topic_rate[j] += lda_document[i][0][j][1]
            if not num ==0:
                all_topic_rate[true_nengo_list[k]] = [w/num for w in topic_rate]
            else:
                all_topic_rate[true_nengo_list[k]] = [w for w in topic_rate]

        with open('./data/json/{}_per_nengo.json'.format(self.num_topics), 'w') as f:
            json.dump(all_topic_rate, f, indent=1,cls = MyEncoder)

        with open('./data/json/nengo_data.json', 'w') as f:
            nengo_data = {"年号":true_nengo_list, "文書数":number_of_nengo_list}
            json.dump(nengo_data, f,cls = MyEncoder)   



if __name__ == '__main__':
    # for i in range(2,21):
    #     print(i)
    mlda = FLDA(10,0,"gumaiki.xml","person.csv")
    # mlda.run_LDA()
    mlda.get_result()