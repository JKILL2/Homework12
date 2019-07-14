# Import dependencies
from bs4 import BeautifulSoup as bs
import pymongo
from splinter import Browser
import pandas as pd
from selenium import webdriver
import time

# Set up splinter
def init_browser():
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    content = {}
    browser = init_browser()

    # Url of site to be scraped
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)
    time.sleep(2)
    html = browser.html

    # create a beautifulsoup object
    soup = bs(html, 'html.parser')

    # save latest news title and summary
    content["news_title"] = soup.find("div", class_="content_title").text
    content["news_blurb"] = soup.find("div", class_="article_teaser_body").text

    # URL of JPL images scraped
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)
    time.sleep(2)
    html = browser.html

    # create a beautifulsoup object
    soup = bs(html, 'html.parser')

    # find the link to the featured image
    partial_link = soup.find("a", class_="button")["data-link"]
    root_url = "https://www.jpl.nasa.gov"
    details_link = root_url + partial_link

    # create beautifulsoup object
    browser.visit(details_link)
    time.sleep(2)
    html = browser.html
    soup = bs(html, 'html.parser')

    # find image url
    image_url = soup.find('figure', class_="lede").a["href"]

    # save the featured image url
    content["featured_image_url"] = root_url + image_url

    # scrape the latest weather tweet from the Mars weather twitter feed
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)
    time.sleep(2)
    html = browser.html

    # create beautifulsoup object
    soup = bs(html, 'html.parser')

    # save the Mars weather tweet
    content["mars_weather"] = soup.find('p', class_="tweet-text").text

    # scrape the table containing facts about the planet
    url = "http://space-facts.com/mars/"
    browser.visit(url)
    time.sleep(3)
    html = browser.html

    # create beautifulsoup object
    soup = bs(html, 'html.parser')

    # scrape all the tables into a pandas dataframe
    mars_facts = pd.read_html(url)[1]
    mars_facts.columns = ["Description", "Value"]

    # remove the index column
    mars_facts.set_index("Description", inplace = True)

    # convert to HTML
    mars_facts_html = mars_facts.to_html(classes="table table-striped")
    
    # save the Mars facts table
    content["mars_facts_html"]= mars_facts_html

    # URL of the page to be scraped
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    time.sleep(2)
    html = browser.html

    # create a beautifulsoup object
    soup = bs(html, 'html.parser')
    
    # path selector to find headers
    xpath = "//div[@class='description']//a[@class='itemLink product-item']/h3"

    # the results are the 4 headers to the detail pages
    results = browser.find_by_xpath(xpath)

    # placeholder
    hemisphere_image_urls = []

    # loop through all 4 links
    for i in range(4):
        
        # load the html from the browser again and create beautifulsoup object
        html = browser.html
        soup = bs(html, 'html.parser')
        
        # find the new splinter elements
        results = browser.find_by_xpath(xpath)
        
        # save the name of the hemisphere
        header = results[i].html

       # click on the header to go to the hemisphere details page 
        details_link = results[i]
        details_link.click()
        time.sleep(2)
        
        # load hemisphere details page into beautifulsoup
        html = browser.html
        soup = bs(html, 'html.parser')
        
        # save image url
        hemisphere_image_urls.append({"title": header, "image_url": soup.find("div", class_="downloads").a["href"]})
        
        # go back to the original page
        browser.back()
        time.sleep(2)

    content["hemisphere_image_urls"] = hemisphere_image_urls

    browser.quit()

    return content