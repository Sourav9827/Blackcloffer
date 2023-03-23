import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

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
            file.write(title.get_text() + '\n\n' + text)
            
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
            file.write(title.get_text() + '\n\n' + text)
            
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
    with open(file_path, 'w', encoding='utf-8') as file:
            file.write("Page not found | Blackcoffer Insights")