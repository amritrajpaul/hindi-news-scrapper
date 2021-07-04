import codecs
import requests
from bs4 import BeautifulSoup 
import pandas as pd
from selenium import webdriver
import datetime
import time
import sys
import xlwt
import openpyxl
import re
from progress.bar import Bar



stime = time.time()

def parse_article(links,saved_links_title):

    '''This function opens individual relevant article through the link provided from the parse() function below 
    and uses beautiful soup library to extract the article content and their published dates'''
    print("Begun extracting each article from fitered links --- %s seconds ---" % (time.time() - stime))
    saved_articles = []
    saved_headlines = []
    saved_article_dates =[]
    art_counter = 0
    for link in links:#saved_requestable_links:
        try:
            article = []
            article_content = requests.get(link).content
            article_soup = BeautifulSoup(article_content,'html.parser')
            paras = article_soup.findAll("p",{'style':"word-break:break-word"})
            dateandtime = article_soup.find("meta", {"property": "article:published_time"}).attrs['content']
            dateandtime = dateandtime[:-6]
            for para in paras:
                #article = ''.join(para.get_text())
                article.append(para.get_text())
            saved_articles.append(article)
            date_time_obj = datetime.datetime.strptime(dateandtime, '%Y-%m-%dT%H:%M:%S')
            saved_article_dates.append(date_time_obj)
            art_counter = art_counter + 1
            sys.stdout.write('\rArticles Parsed : {}/{} ...Time Elapsed:{} sec\n'.format(art_counter,len(links),(time.time() - stime)))#just for animation
            sys.stdout.flush()
        except Exception as e :
            print('Excepion Handled while Parsing article handled ! ',e)
            saved_articles.append(' ')
            tdate = datetime.date(1997,1,1)
            saved_article_dates.append(tdate)
    dic = {'Headlines':saved_links_title,'Articles':saved_articles}
    return dic,saved_article_dates
    #hin_df = pd.DataFrame(dic,index = saved_article_dates)
    #print("Done! --- %s seconds ---" % (time.time() - stime))
    #data = quandl.get("BSE/SENSEX", authtoken="xxxxxxxxxxxxxxx",start_date = hin_df.index.date[-1],end_date = hin_df.index.date[0])
    #data['sensex_open_to_close_price'] = ((data['Close'] - data['Open'])/data['Open'] )*100
    #data.to_excel('16000Sec_Scrapped_sensex_data.xlsx', sheet_name='Sheet1', index=True, encoding=None)
    #hin_df.to_excel('16000Sec_Scrapped_data.xlsx', sheet_name='Sheet1', index=True, encoding=None)
    #print('two xlsx file was created (Find them in the current program directory) :\n "16000Sec_Scrapped_sensex_data.xlsx" & "16000Sec_Scrapped_data.xlsx"')

def parse(keywords):

    '''This function opens the website scrolls down for 100 seconds then takes the page source code 
    to traverse and extract news Headlines and Executable Links of relevant articles using keywords,
    Then calls the above function parse_article() with executable link as a parameter'''
    home_link = 'https://www.bhaskar.com/business/'
    print("Begun Parsing and filtering links with keyword --- %s seconds ---" % (time.time() - stime))
    driver = webdriver.Chrome('C:\Program Files\Google\Chrome\Application\chromedriver')
    #url = 'https://www.bhaskar.com/business/'
    driver.get(home_link)
    time.sleep(10)
    prev_height = driver.execute_script('return document.body.scrollHeight;')
    limit = 0
    set_limit = 5 #This limit stands for the number of scroll operation to occur
    set_sleep = 1
    while limit < set_limit: #Increase this limit for scraping more article
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(set_sleep)
        new_height = driver.execute_script('return document.body.scrollHeight;')
        #if limit > 1000:
         #   if new_height == prev_height:
          #      break
        prev_height = new_height
        limit += 1
        sys.stdout.write('Selenium Scrolled : {}/{} ...Time Elapsed:{} sec\n'.format(limit,set_limit,(time.time() - stime)))
        sys.stdout.flush()
    markup = driver.page_source
    soup = BeautifulSoup(markup,'html.parser')
    links = driver.execute_script
    links = soup.findAll("li",{"class" : '_24e83f49 e54ee612'})
    saved_links = []
    saved_links_title =[]
    saved_requestable_links = []
    for link in links:
        for keyword in keywords:
            if keyword in link.text:
                if link not in saved_links: #this condition stops duplicate links
                    saved_links.append(link)
                    saved_links_title.append(link.text)
                    saved_requestable_links.append(str(home_link) + str(link('a')[0]['href']))
    print("\nDone! --- %s seconds ---" % (time.time() - stime))
    print('{} articles to be passed for scraping'.format(len(saved_requestable_links)))
    dic = {}
    dates = []
    dic ,dates= parse_article(saved_requestable_links,saved_links_title)
    return dic,dates

search = ['सेंसेक्स']
dictionary,dates = parse(search)
news_dataframe = pd.DataFrame(dictionary,index = dates)
news_dataframe.index.name = 'Publish_datetime'
news_dataframe.to_excel('Scrapped_news_data.xlsx', sheet_name='Headlines&Articles', index=True, encoding=None)
print('DataFrame sucessfully created: "news_dataframe"\n.xlsx file sucessfully created: "Scrapped_news_data"\nwith Articles & Headlines on {} indexed according to publish datetime'.format(search))
