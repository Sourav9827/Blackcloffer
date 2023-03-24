import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import string


df = pd.read_excel('input.xlsx')

directory = "scrapped_data_folder"

l, uid = [], []

for index, row in df.iterrows():
    url = row['URL']
    url_id = row['URL_ID']
    
    # Make a request to the URL and get the content
    response = requests.get(url)
    content = response.content
    
    # Use BeautifulSoup to extract the article text
    soup = BeautifulSoup(content, 'html.parser')
    article = soup.find('div', class_='td-ss-main-content')
    if article:
        title = article.find('h1')
        if title == None:
            markup = "<h1>Error Page<h1>"
            soup2 = BeautifulSoup(markup)
            title = soup2.h1
        paras = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paras])
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f'{url_id}.txt')
        # Save the article text in a text file with URL_ID as the file name
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(title.get_text() + ' ' + text)
            
        print(f'Article extracted from {url} and saved as {url_id}.txt')
    else:
        l.append(url)
        uid.append(url_id)
        print(f'Could not extract article from {url}')

unscrapped_url = pd.DataFrame(data = zip(uid, l), columns = ['URL_ID', 'URL'])

print(unscrapped_url)

l2, uid2 = [], []

for index, row in unscrapped_url.iterrows():
    url = row['URL']
    url_id = row['URL_ID']
    
    # Make a request to the URL and get the content
    response = requests.get(url)
    content = response.content
    
    # Use BeautifulSoup to extract the article text
    soup = BeautifulSoup(content, 'html.parser')
    article = soup.find('div', class_='td_block_wrap tdb_single_content tdi_186 td-pb-border-top td_block_template_1 td-post-content tagdiv-type')
    if article:
        title = soup.find('h1')
        if soup.title.get_text == 'Page not found | Blackcoffer Insights':
            markup = "<h1>Error Page<h1>"
            soup2 = BeautifulSoup(markup)
            title = soup2.h1
        paras = soup.find_all('p')
        text = ' '.join([para.get_text() for para in paras])
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, f'{url_id}.txt')
        # Save the article text in a text file with URL_ID as the file name
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(title.get_text() + ' ' + text)
            
        print(f'Article extracted from {url} and saved as {url_id}.txt')
    else:
        l2.append(url)
        uid2.append(url_id)
        print(f'Could not extract article from {url}')

unscrapped_url2 = pd.DataFrame(data = zip(uid2, l2), columns = ['URL_ID', 'URL'])

print(unscrapped_url2)

for index, row in unscrapped_url2.iterrows():
    url = row['URL']
    url_id = row['URL_ID']
    file_path = os.path.join(directory, f'{url_id}.txt')
    with open(file_path, 'w', encoding='utf-8') as file:
            file.write("Page not found | Blackcoffer Insights")

print("Scrapping Done")

#Data Cleaning

folder_path = '/StopWords'
stopwords_articles = []

for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        with open(os.path.join(folder_path, filename), 'r') as file:
            stopwords_articles.extend(file.read().split())

folder_path = '/scrapped_data_folder'
data = []

for filename in os.listdir(folder_path):
    if filename.endswith('.txt'):
        with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as file:
            text = file.read()
        url_id = os.path.splitext(filename)[0]
        data.append((url_id, text))

df_text = pd.DataFrame(data, columns=['URL_ID', 'text'])

df_url = pd.read_excel('../input.xlsx')

df_text['URL_ID'] = df_text['URL_ID'].astype('int64')

df = pd.merge(df_url, df_text, on = "URL_ID")

def process_articles(article, stopwords_articles):
    stemmer = nltk.PorterStemmer()
    article = re.sub(r'\$\w*', '', article)
    article = re.sub(r'^RT[\s]+', '', article)
    article = re.sub(r'https?:\/\/.*[\r\n]*', '', article)
    article = re.sub(r'#', '', article)
    article = article.lower()
    tokenizer = nltk.TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
    article_tokens = tokenizer.tokenize(article)

    article_clean = []
    for word in article_tokens:
        if (word not in stopwords_articles and word not in string.punctuation):
            stem_word = stemmer.stem(word)
            article_clean.append(stem_word)
    article_clean=' '.join(article_clean)
    return article_clean

df['text_cleaned']=df['text']

for i in range(len(df)):
    df['text_cleaned'][i] = process_articles(df['text_cleaned'][i], stopwords_articles)

df.to_csv("/data_folder/cleaned_data.csv", index=False)

#Text Analysis

cleaned_df = pd.read_csv("/data_folder/cleaned_data.csv")

nltk.download('punkt')

with open('/MasterDictionary/positive-words.txt', 'r') as file:
    positive_text = file.readlines()
positive_words = [word.strip() for word in positive_text]

with open('/MasterDictionary/negative-words.txt', 'r') as file:
    negative_text = file.readlines()
negative_words = [word.strip() for word in negative_text]

score_df = cleaned_df.copy()

def positive_score(text):
    tokens = word_tokenize(text)
    positive_tokens = [token for token in tokens if token in positive_words]
    return len(positive_tokens)

def negative_score(text):
    tokens = word_tokenize(text)
    negative_tokens = [token for token in tokens if token in negative_words]
    return len(negative_tokens)

score_df['POSITIVE SCORE'] = score_df['text_cleaned'].apply(positive_score)

score_df['NEGATIVE SCORE'] = score_df['text_cleaned'].apply(negative_score)

score_df['POLARITY SCORE'] = (score_df['POSITIVE SCORE'] - score_df['NEGATIVE SCORE']) / ((score_df['POSITIVE SCORE'] + score_df['NEGATIVE SCORE']) + 0.000001)

score_df['SUBJECTIVITY SCORE'] = (score_df['POSITIVE SCORE'] + score_df['NEGATIVE SCORE']) / (len(word_tokenize('text_cleaned')) + 0.000001)

def avg_length_sentence(para):
    sentence = sent_tokenize(para)
    s = 0
    for i in range(len(sentence)):
        s = s + len(sentence[i])
    return s / len(sentence)

score_df['AVG SENTENCE LENGTH'] = score_df['text'].apply(avg_length_sentence)

def count_complex_words(text):
    words = word_tokenize(text)
    complex_words = [word for word in words if len(word) > 2 and nltk.probability.FreqDist(word.lower()).N() > 2]
    return len(complex_words)

score_df['PERCENTAGE OF COMPLEX WORDS'] = 0
for i in range(len(score_df)):
    score_df['PERCENTAGE OF COMPLEX WORDS'][i] = count_complex_words(score_df['text_cleaned'][i]) * 100 / len(word_tokenize(score_df['text_cleaned'][i]))

score_df['FOG INDEX'] = 0.4 * (score_df['AVG SENTENCE LENGTH'] + score_df['PERCENTAGE OF COMPLEX WORDS'])

score_df['AVG NUMBER OF WORDS PER SENTENCE'] = 0
for i in range(len(score_df)):
    score_df['AVG NUMBER OF WORDS PER SENTENCE'][i] = len(word_tokenize(score_df['text_cleaned'][i])) / len(sent_tokenize(score_df['text'][i]))

score_df['COMPLEX WORD COUNT'] = score_df['text_cleaned'].apply(count_complex_words)

score_df['WORD COUNT'] = score_df['text_cleaned'].apply(len)

nltk.download('cmudict')

def count_syllables(word):
    vowels = re.findall(r'[aeiouy]+', word.lower())
    count = len(vowels) - len(re.findall(r'(?:es|ed)$', word.lower()))
    return max(count, 1)

def syllables_per_word(text):
    words = text.split()
    syllable_counts = [count_syllables(word) for word in words]
    return sum(syllable_counts) / len(words)

score_df['SYLLABLE PER WORD'] = score_df['text'].apply(syllables_per_word)

def count_pronouns(text):
    pattern = r'\b(i|we|my|ours|us)\b'
    matches_US = re.findall(r'\b(US)\b', text)
    matches = re.findall(pattern, text, re.IGNORECASE)
    return len(matches) - len(matches_US)

score_df['PERSONAL PRONOUNS'] = score_df['text'].apply(count_pronouns)

def avg_word_length(text):
    s=0
    for i in text.split():
        s = s+len(i)
    return s/len(text.split())

score_df['AVG WORD LENGTH'] = score_df['text'].apply(avg_word_length)

score_df.to_csv('/data_folder/Final.csv', index=False)

score_df.drop(['text','text_cleaned'], axis=1).to_csv('/data_folder/Submission.csv', index=False)



















