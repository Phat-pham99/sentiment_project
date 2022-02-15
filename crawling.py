from function import get_url_com, get_url_time, get_list, convert, clean_comment
import pandas as pd
from googlesearch import search
import re

def crawling_data(t):
    gg = []
    base = []
    query = 'vozforum ' + t
    gg = search(query, num_results=10)
    for url in gg:
        if (url[0:21] == 'https://vozforum.org/'):
            url = url.split('page-')[0]
            base.append(url)
    comment_full=[]
    time_full=[]
    for url in base:
        comment_full.append(get_url_com(url))
        time_full.append(get_url_time(url))
    list_com=get_list(comment_full)
    list_time=get_list(time_full)
    data=pd.DataFrame({'time':list_time,'comment':list_com})
    convert(data)
    data.comment=data.comment.apply(clean_comment)
    data=data.drop_duplicates(subset='comment',keep='first').reset_index()
    data=data.drop(columns='index')
    comt=[]
    for i in data.comment:
        if 'You must be registered for see images' in i:
            i = i.replace('You must be registered for see images','')
        if 'You must be registered for see links' in i:
            i=i.replace('You must be registered for see links','')
        if 'You must be registered for see medias' in i:
            i = i.replace('You must be registered for see medias','')
        if 'Được gửi từ' in i:
            i = i.replace('Được gửi từ','')
        else:
            pass
        i= re.sub(r'\w*for','',i)
        comt.append(i)
    return data

