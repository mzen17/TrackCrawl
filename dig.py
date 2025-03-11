from selenium import webdriver
import random
import csv
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Base set up. Assumes
# 1) Chromedriver is in path.
# 2) Chrome is installed.

options = webdriver.ChromeOptions()
#options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
options.add_argument('--disable-gpu')  # Disable GPU acceleration
options.add_argument('--no-sandbox')  # Disable sandboxing for Linux
driver = webdriver.Chrome(options=options)
driver.set_page_load_timeout(10)


# function for obtaining tranco list when in CSV format.
with open("TrancoT1000.txt", newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    urls = [row[1] for row in reader if len(row) > 1]
    
# split urls based off of domain extension
top_eu_domains = ["de","uk","fr","it","es","nl","pl","be","se","at"]

normal_urls = []
gdpr_urls = []

for url in urls:
    ext = url.split(".")[-1]
    if ext in top_eu_domains:
        gdpr_urls.append(url)
    else:
        normal_urls.append(url)

print("URL Counts")
print(len(normal_urls))
print(len(gdpr_urls))

# Take Top 100 from each
scale = 10
normal_urls = normal_urls[:scale]
gdpr_urls = gdpr_urls[:scale]

def dig(url_list):
    pre_cookie_count = 0 # Amount of 3rd party cookies pre-interaction
    post_cookie_count = 0 # Amount of 3rd party cookies post-interaction
    jsa_count = 0 # Amount of 3rd party JavaScript found with Regex on DOM
    js_count = 0 # Total amount of 3rd party Javascript

    ec_count = 0 # number of errors on website (likely from robots.txt)

    for url in url_list:
        try:
            print("Fetching " + url)

            properURL = "https://" + url # urls don't contain https protocol; add it
            
            # Look at robots.txt. If doesn't exist, use try-except as fallback to track
            # that it doesn't exist.            
            #driver.get(properURL + "/robots.txt")

            driver.get(properURL)
            pre_interact_cookies = len(driver.get_cookies())

            #time.sleep(1) # pretend user loads page

            print("Simulating actions")
            
            # Window dimensions are used so click doesn't end outside the browser
            window_width = driver.execute_script("return window.innerWidth")
            window_height = driver.execute_script("return window.innerHeight")

            actions = ActionChains(driver)
            for _ in range(5):

                rand_x = random.randint(0, window_width - 1)
                rand_y = random.randint(0, window_height - 1)
                
                actions.move_by_offset(rand_x, rand_y).click().perform()
                
                # Reset mouse position (avoiding cumulative offsets)
                actions.move_by_offset(-rand_x, -rand_y).perform()


            post_interact_cookies = len(driver.get_cookies())
            print(pre_interact_cookies)
            print(post_interact_cookies)

            pre_cookie_count += pre_interact_cookies
            post_cookie_count += post_interact_cookies

            # due to random clicks possibly creating more tabs, clear all but 1 tab
            num_of_tabs = ...
            for x in range(1, num_of_tabs):
                self.driver.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'W')

        except Exception as e:
            print("Error on " + url + " | " + str(e))
            ec_count += 1

    return pre_cookie_count, post_cookie_count, jsa_count, js_count, ec_count

normals_with_no_cookies = dig(normal_urls)
gdpr_with_no_cookie = dig(gdpr_urls)

# update driver with cookie no
#driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {
#    "headers": {
#        "Sec-GPC": "1"  # 1 indicates "Do Not Sell" preference is enabled
#    }
#})

normals_with_cookies = dig(normal_urls)
gdpr_with_cookies = dig(gdpr_urls)

print("Note: all tuples should be interpreted as (cookie pre-interact, cookie post-interact, script count, analytical script count)")
print("Normal URLS with No Cookie Block: " + str(normals_with_no_cookies))
print("Normal URLS with Cookie Block: " + str(normals_with_cookies))
print("GDPR URLs with No Cookie Block: " + str(gdpr_with_no_cookie))
print("GDPR URLS with cookie Block: " + str(gdpr_with_cookies))
