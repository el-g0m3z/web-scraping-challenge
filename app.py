import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from flask import Flask, render_template, jsonify, request, redirect


# Setting up URL Variables
NASA_URL = "https://mars.nasa.gov/news/"

JPL_IMG_URL_ROOT = "https://www.jpl.nasa.gov"
JPL_IMG_URL = JPL_IMG_URL_ROOT + "/spaceimages/?search=&category=Mars"

TWITTER_URL = "https://twitter.com/marswxreport?lang=en"

FACTS_URL = "http://space-facts.com/mars/"

ASTRO_URL_ROOT = "https://astrogeology.usgs.gov"
ASTRO_URL = ASTRO_URL_ROOT + "/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

# Function to scrape Website using Selenium and Return a BEAUTIFUL Soup
def s_scrape(url):
    driver = webdriver.Firefox()
    driver.get(url)
    driver.implicitly_wait(10)
    soup = BeautifulSoup(driver.page_source, "lxml")
    driver.close()
    return soup


# Function to scrape Website using Requests and Return a BEAUTIFUL Soup
def r_scrape(url):
    r = requests.get(url).text
    return BeautifulSoup(r, "lxml")


# Put everything into a single function to return a dictionary of everything.
def scrape():
    data = {}

    # Selenium driver to get soups
    nasa_soup = s_scrape(NASA_URL)
    facts_soup = s_scrape(FACTS_URL)
    astro_soup = s_scrape(ASTRO_URL)

    # Requests to get remaining soups
    jpl_soup = r_scrape(JPL_IMG_URL)
    twitter_soup = r_scrape(TWITTER_URL)

    ##Search through soups to find text
    ## add information to data dictionary.

    # Nasa Mars Latest Article title and teaser
    news_title = nasa_soup.body.find("div", class_="content_title").text
    news_p = nasa_soup.body.find("div", class_="article_teaser_body").text
    nasa_latest = {"title": news_title, "teaser": news_p}
    data["nasa"] = nasa_latest

    # Featured Image from JPL
    featured_image_url = JPL_IMG_URL_ROOT + jpl_soup.body.find("article")["style"].split(" ")[
        1
    ].strip("url").strip(";(')")
    data["featured_image"] = featured_image_url

    # Twitter
    mars_weather = twitter_soup.body.find(
        "p", class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"
    ).text
    data["mars_weather"] = mars_weather

    # Mars Facts Table
    facts_df = pd.read_html(
        str(facts_soup.body.find("table", id="tablepress-p-mars-no-2"))
    )[0]
    facts_df.columns = ["description", "value"]
    facts_df = facts_df.set_index("description").to_html()
    data["facts_table"] = facts_df

    # Astropedia
    # Find Title and url to hemisphere pages.
    astro_h = astro_soup.find_all("h3")
    astro_d = [{"title": h.text, "url": ASTRO_URL_ROOT + h.parent["href"]} for h in astro_h]

    # Visit each url found above and add the img_url to the appropriate dictionary.
    for h in astro_d:
        soup = s_scrape(h["url"])
        img = soup.find("a", target="_blank")
        h.update({"img_url": img["href"]})
    data["hemispheres"] = astro_d

    return data


if __name__ == "__main__":
    scrape()
