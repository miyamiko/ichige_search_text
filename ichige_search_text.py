import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# keywordのindexを複数抽出
def find_indices(string, sub_string):
    indices = []
    start = 0
    while start < len(string):
        pos = string.find(sub_string, start)
        if pos == -1:
            break
        indices.append(pos)
        start = pos + 1
    return indices
#AND検索関数、list_of_strings例['apple', 'banana', 'cherry', 'date']から
# search_terms例['ap', 'le']の要素が全て含まれているlist_of_stringsの要素抽出、例の出力['apple']
#1今回、list_of_stringsを1要素のリスト[1個の記事だけ]で使えば、ある記事にsearch_termsが全て含まれているかの判定ができる
def and_search(list_of_strings, search_terms):
    return [s for s in list_of_strings if all(term in s for term in search_terms)]
st.title('イチゲブログ内検索（テキストのみ版）')
st.caption('イチゲブログ内を検索できます。事前にJupiterNotebookでブログをスクレーピングし、すべての記事をpandasからcsvへ変換して保存。そのcsvをpandasに戻し検索しています。')
st.markdown('###### 詳細は')
link = '[イチゲブログ](https://kikuichige.com/17869/)'
st.markdown(link, unsafe_allow_html=True)

#csvをデータフレームで開く
df_info = pd.read_csv('text_ichige_all.csv',index_col=0)
#withを使うことによりst.form_submit_buttonが実行（押）されるまでリロードされなくなる。
with st.form(key='search_form'):
    st.markdown('###### 検索ワード:red[（表示ボタンが表示されるまでお待ちください。数分かかる場合があります。）]')
    #st.text_inputの第一引数-ラベル、第二引数-初期値
    keyword=st.text_input('検索したいワード（半角で複数キーワードを書いてAND検索もできます。例python Django　全てのキーワードが含まれているページから第一引数で検索します。完全一致なので半角、全角は区別されます）')
    keywords=keyword.split(' ')
    dup_url = st.checkbox('重複URL削除')
    des=None
    destinations=[]
    result_sentences=[]
    #記事数分繰り返す
    for i in range(len(df_info)):
        #c=i番目の記事
        c=df_info.iloc[i,1]
        #keywordsが全てcに含まれているときだけ実行される。AND検索の機能。and_searchの第一引数はリストなので[c]で文字列をリストにする
        if and_search([c],keywords) != []:
            #先頭の1個目のワードで検索する。場所がはなれているので1個目以外は検出しない仕様にした。ただし含まれていないと検索されないのでAND検索になっている。
            # index = c.find(keywords[0])#index=keywordの位置
            indexes = find_indices(c, keywords[0])#indexs=keywordの位置すべて

            for index in indexes:
                if index != -1:#検出できた場合
                    des=str(df_info.iloc[i,0])
                    destinations.append(des)
                    
                    if des:#これがないとdestinationと数が合わない
                        #前後文字抽出
                        px=40
                        mx=40
                        if index-px<0:
                            px=index
                        if index+mx>len(c):
                            mx=len(c)-index
                        result_sentence= c[index-px:index+mx]#キーワード前px後mxの長さの文字列抽出
                        result_sentences.append(result_sentence)                   
    #2つのリストで片方のリストで重複があった場合もう1方でも対応する要素を削除
    destinations1 = []
    result_sentences1 = []
    #重複URL削除モード
    if dup_url:
        for i, item in enumerate(destinations):
            #重複していないURLのみ保存
            if item not in destinations1:
                destinations1.append(item)
                #urlに対応するセンテンスを保存
                result_sentences1.append(result_sentences[i])
    #重複URLありモード
    else:
        destinations1 = destinations
        result_sentences1 = result_sentences        
    submit_btn=st.form_submit_button('表示')

    if submit_btn:
        # st.text(f'モードは{zokusei}')
        result_suu=len(destinations1)
        st.text(f'検索結果数{str(result_suu)}')
        for i in range(result_suu):
            #検索結果、文字列
            sentence = f'{result_sentences1[i]}'
            st.markdown(sentence, unsafe_allow_html=True)
            #検索結果、URL
            link = f'[{destinations1[i]}]({destinations1[i]})'
            st.markdown(link, unsafe_allow_html=True)