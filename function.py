import numpy as np
from vncorenlp import VnCoreNLP
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime
import re
import torch

STOPWORDS = 'vietnamese-stopwordsv3.txt'
with open(STOPWORDS, "r") as ins:
    stopwords = []
    for line in ins:
        dd = line.strip('\n')
        stopwords.append(dd)
    stopwords = set(stopwords)
dict_sent = pd.read_csv('dict_sentiment_v2.csv')
vncorenlp = VnCoreNLP("VnCoreNLP-master/VnCoreNLP-1.1.1.jar", annotators="wseg", max_heap_size='-Xmx500m')

def filter_vt(train_sentences, dict_sent):
    for i in range(len(dict_sent)):
        for word in train_sentences.split():
            if (word == dict_sent.iloc[i, 0]):
                train_sentences = train_sentences.replace(dict_sent.iloc[i, 0], dict_sent.iloc[i, 1])
    return train_sentences


def filter_stop_words(train_sentences, stop_words):
    new_sent = [word for word in train_sentences.split() if word not in stop_words]
    train_sentences = ' '.join(new_sent)

    return train_sentences


def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                        u"\U0001F600-\U0001F64F"  # emoticons
                                        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                        u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                        "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)



def negation_handling(text):
    negation = False
    delims = "?.,!:;"
    result = []
    words = text.split()
    for word in words:
        stripped = word.strip(delims).lower()
        negated = "không_" + stripped if negation else stripped
        if negation == True:
            negation = not negation
        result.append(negated)
        if any(neg in word for neg in ["không", "chưa", "chẳng", 'có chắc']):
            negation = not negation
    for word in result:
        if word in ['không', 'chẳng', 'chưa', 'có chắc']:
            result.remove(word)
    result = ' '.join(result)
    return result


# tạo intensification: ví dụ câu: Tôi rất thích đi học -> Tôi rất_thích đi học
def intensification_handling(text):
    negation = False
    delims = "?.,!:;"
    result = []
    words = text.split()
    for word in words:
        stripped = word.strip(delims).lower()
        negated = "rất_" + stripped if negation else stripped
        if negation == True:
            negation = not negation
        result.append(negated)
        if any(neg in word for neg in ["rất", "khá", "hơi"]):
            negation = not negation
    for word in result:
        if word in ['rất', 'hơi', 'khá']:
            result.remove(word)
    result = ' '.join(result)
    return result


def preprocess(text, tokenized=True, lowercased=True):
    # text = ViTokenizer.tokenize(text)
    # text = ' '.join(vncorenlp.tokenize(text)[0])
    #text = filter_vt(text, dict_sent)
    text = filter_stop_words(text, stopwords)
    text = deEmojify(text)
    text = text.lower() if lowercased else text
    text = negation_handling(text)
    text = intensification_handling(text)
    if tokenized:
        pre_text = ""
        sentences = vncorenlp.tokenize(text)
        for sentence in sentences:
            pre_text += " ".join(sentence)
        text = pre_text
    return text


def pre_process_features(X, y, tokenized=True, lowercased=True):
    X = [preprocess(str(p), tokenized=tokenized, lowercased=lowercased) for p in list(X)]
    for idx, ele in enumerate(X):
        if not ele:
            np.delete(X, idx)
            np.delete(y, idx)
    return X, y


def clean_tags(soup):
    for tag in soup.find_all(["span"]):
        tag.decompose()
def delete_block(comment):
    if comment.find('blockquote') != None:
        com_full = comment.get_text(strip=True)
        com_full = com_full.replace('\t','')
        com_full = com_full.replace('\n','')
        a=len(com_full)
        com_block=comment.find('blockquote').get_text()
        com_block=com_block.replace('\t','')
        com_block=com_block.replace('\n','')
        b=len(com_block)
        com = com_full[(b-1):]
    else:
        com = comment.get_text(strip=True)
        com = com.replace('\t','')
        com = com.replace('\n','')
    return com
def get_comment(url):
    r= requests.get(url).text
    soup = bs(r,'html.parser')
    get_com = soup.find_all(class_='bbWrapper')
    clean_tags(soup)
    comment_info=[]
    for i in get_com:
        comment_info.append(delete_block(i))
    return comment_info
def get_time(url):
    r= requests.get(url).text
    soup = bs(r,'html.parser')
    get_time=soup.find_all(class_='message-attribution-main')
    time_info=[]
    for i in get_time:
        i=i.get_text()
        i=i.replace('\n','')
        time_info.append(i)
    return time_info
def get_list(comment_full):
    list_com=[]
    for i in comment_full:
        for a in i:
            com= a
            for co in com:
                list_com.append(co)
    return list_com
def get_url_com(url):
    list_=[]
    comment_fu=[]
    nums = (np.arange(1, 20))
    Pages = []
    for num in nums:
        Pages.append('page-' + str(num))

    comment_fu=[]
    for i in Pages:
        if i == 'page-1':
            rela_url=url
        else:
            try:
                rela_url=url+i
            except Exception as e:
                print(None)
        #print(rela_url)
        comment_fu.append(get_comment(rela_url))
    return comment_fu
def get_url_time(url):
    list_=[]
    nums = (np.arange(1, 20))
    Pages = []
    for num in nums:
        Pages.append('page-' + str(num))

    comment_fu=[]
    for i in Pages:
        if i == 'page-1':
            rela_url=url
        else:
            try:
                rela_url=url+i
            except Exception as e:
                print(None)
        #print(rela_url)
        comment_fu.append(get_time(rela_url))
    return comment_fu
def convert(data):
    for index, i in enumerate(data.comment):
        if type(i) == list:
            a=' '.join(i)
            data.comment[index]= a
    for index, i in enumerate(data.time):
        i=i.replace(',','')
        date = datetime.strptime(i, '%b %d %Y')
        data.time[index]=date
def clean_comment(com):
    com=re.sub("\W"," ",com)
    REGEX2= re.compile(r"[\"']")
    com=REGEX2.sub('',com)
    return com


class BuildDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels=None):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)