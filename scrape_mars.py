#!/usr/bin/env python
# coding: utf-8

# In[4]:


from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import pymongo
import pandas as pd
import datetime as dt
from pprint import pprint


# In[5]:


NASA_URL = "https://mars.nasa.gov/news/"

JPL_IMG_URL_ROOT = "https://www.jpl.nasa.gov"
JPL_IMG_URL = JPL_IMG_URL_ROOT+"/spaceimages/?search=&category=Mars"

TWITTER_URL = "https://twitter.com/marswxreport?lang=en"

FACTS_URL = "http://space-facts.com/mars/"

ASTRO_URL_ROOT = 'https://astrogeology.usgs.gov'
ASTRO_URL = ASTRO_URL_ROOT+"/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"


# # NASA Mars News

# In[6]:


nasa_soup = BeautifulSoup(requests.get(NASA_URL).text, "html.parser")

title_div = nasa_soup.body.find_all("div", class_="slide")[0]
nasa_title = title_div.find_all("div", class_="content_title")[0].a.text.strip()
nasa_desc = title_div.find("div", class_="rollover_description_inner").text.strip()


# In[15]:


print(nasa_title)
print(nasa_desc)


# # JPL Mars Space Images - Featured Image

# In[17]:


jpl_soup = BeautifulSoup(requests.get(JPL_IMG_URL).text, "html.parser")

image_container = jpl_soup.body.find_all("footer")[0].a
large_file_path = (
    str(image_container["data-fancybox-href"])
    .replace("medium", "large")
    .replace("_ip", "_hires")
)
featured_image_url = f"{JPL_IMG_URL_ROOT}{large_file_path}"
featured_image_url


# # Mars Weather Twitter Tweet

# In[19]:


twitter_soup = BeautifulSoup(requests.get(TWITTER_URL).text, "html.parser")

tweet_text_container = twitter_soup.body.find_all(
    "p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"
)

mars_weather = ""
for tweet in tweet_text_container:
    if tweet.text.startswith("InSight"):
        mars_weather = tweet.text[: tweet.text.find("pic.twitter.com")]
        break
mars_weather


# # Mars Facts

# In[20]:


space_soup = BeautifulSoup(requests.get(FACTS_URL).text, "html.parser")

mars_table_container = space_soup.body.find_all("table", id="tablepress-p-mars-no-2")[0]
mars_info_df = pd.read_html(str(mars_table_container))
mars_info_df


# # Mars Hemispheres

# In[22]:


driver = webdriver.Firefox()
driver.get(ASTRO_URL)
driver.implicitly_wait(10)
astro_soup = BeautifulSoup(driver.page_source, "lxml")
driver.close()
astro_h = astro_soup.find_all("h3")


# In[24]:


astro_dict = [{"title": h.text, "url": ASTRO_URL_ROOT + h.parent["href"]} for h in astro_h]
astro_dict


# In[26]:


driver = webdriver.Firefox()
for h in astro_dict:
    driver.get(h["url"])
    driver.implicitly_wait(10)
    soup = BeautifulSoup(driver.page_source, "lxml")
    img = soup.find("a", target="_blank")
    h.update({"img_url": img["href"]})
driver.close()
astro_dict


# In[ ]:




