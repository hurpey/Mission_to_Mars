## > Exported and Cleaned Mission_to_Mars_Challenge.ipynb code to scraping.py <

# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd  
import datetime as dt 

def scrape_all():
     Initiate headless driver
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    # Set executable path and initialize the chrome browser in splinter 
    #executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    #browser = Browser('chrome', **executable_path)
   
    # Since these are pairs 
    news_title, news_paragraph= mars_news(browser)
    hemisphere_image_urls=hemisphere(browser)
    # Run all scraping functions and store results in dictionary 
    data={
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere_image_urls,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


## > SCRAPE MARS NEWS <

def mars_news(browser):

    # visit the mars nasa news site 
    url= 'https://redplanetscience.com/'
    browser.visit(url)

    #Optional delay for website 
    # Here we are searching for elements with a specific combination of tag (ul) and (li) and attriobute (item_lit) and (slide)
    # Ex. being <ul class= "item_list">
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # HTML Parser. Convert the brpwser html to a soup object and then quit the browser
    html= browser.html 
    news_soup= soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        #slide_elem looks for <ul /> tags and descendents <li />
        # the period(.) is used for selecting classes such as item_list
        slide_elem = news_soup.select_one('ul.item_list li.slide')
        # slide_elem.find("div", class_="content_title")
        # Chained the (.find) to slide_elem which says this variable holds lots of info, so look inside to find this specific entity
        # Get Title
        news_title = slide_elem.find('div', class_= 'content_title').get_text()
        # Get article body 
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
        

    except AttributeError:
        return None,None

    return news_title, news_p


## > SCRAPE FEATURED IMAGES <

def featured_image(browser):

    # Visit URL 
    url= 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full_image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()
    
     # Find the more info button and click that 
    # is_element_present_by_text() method to search for an element that has the provided text
    browser.is_element_present_by_text('more info', wait_time=1)

    # will take our string 'more info' and add link associated with it, then click
    more_info_elem=browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url 
        # The 'figure.lede' references the <figure /> tag and its class=lede
        # the 'a' is the next tag nested inside the <figure /> tag, as well as the 'img' tag 
        # the .get('src') pulls the link to the image

        # WE are telling soup to go to figure tag, then within that look for an 'a' tag then within that look for a 'img' tag
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None
    # Need to get the FULL URL: Only had relative path before
    img_url= f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


## > SCRAPE FACTS ABOUT MARS <

def mars_facts():
    
    # Add try/except for error handling
    try:
        # Creating DF by telling function to look for first html table in site it encounters by indexing it to zero
        df=pd.read_html('https://galaxyfacts-mars.com')[0]

    # BaseException, catches multiple types of errors
    except BaseException:
        return None
    
    # Assigning columns, and set 'description' as index 
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    #Convert back to HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


## > SCRAPE HEMISPHERE <

def hemisphere(browser):
    url='https://marshemispheres.com/'
    browser.visit(url)


    hemisphere_image_urls = []

    imgs_links= browser.find_by_css("a.product-item h3")

    for x in range(len(imgs_links)):
        hemisphere={}

        # Find elements going to click link 
        browser.find_by_css("a.product-item h3")[x].click()

        # Find sample Image link
        sample_img= browser.find_link_by_text("Sample").first
        hemisphere['img_url']=sample_img['href']

        # Get hemisphere Title
        hemisphere['title']=browser.find_by_css("h2.title").text

        #Add Objects to hemisphere_img_urls list
        hemisphere_image_urls.append(hemisphere)

        # Go Back
        browser.back()
    return hemisphere_image_urls

if __name__== "__main__":
    # If running as script, print scrapped data
    print(scrape_all())