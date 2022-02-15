from selenium import webdriver
from time import sleep
import time
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
import csv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import selenium
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
import numpy as np
import pandas as pd


def collect_search_page(search_url_dict, pages_per_category):
    driver = webdriver.Chrome(executable_path='chromedriver')

    #driver = webdriver.Chrome('chromedriver')
    #driver = webdriver.Chrome(ChromeDriverManager().install())
    list_link = []
    # for category, search_url in search_url_dict.items():
    for i in range(pages_per_category):
        driver.get(search_url_dict)
        time.sleep(1)
        total_height = int(driver.execute_script("return document.body.scrollHeight"))

        for i in range(1, total_height, 100):
            driver.execute_script("window.scrollTo(0, {});".format(i))

        items = driver.find_elements_by_class_name("shopee-search-item-result__item")

        for it in (items):
            # try:
            # Get interest attributes
            # name = it.find_element_by_css_selector('._1NoI8_').text
            # n_sold = it.find_element_by_css_selector('._18SLBt').text
            # price = it.find_element_by_css_selector('._1w9jLI._37ge-4._2ZYSiu > span._341bF0').text
            # shop_address = it.find_element_by_css_selector('._3amru2').text
            # image_url = it.find_element_by_css_selector('img._1T9dHf.V1Fpl5').get_attribute("src")
            url = it.find_element_by_css_selector('a').get_attribute("href")

            # #reformat some fields
            # print("-".join([name,n_sold,price,shop_address]))
            # n_sold = n_sold.split(" ")[-1] #convert n_sold to numeric
            # if n_sold[-1] == 'k':
            #     n_sold = float(n_sold.replace(",",".").strip("k")) * 1000
            # else:
            #     n_sold = float(n_sold)
            # price = float(price.replace(".","")) #convert price to numeric

            # csv_writer.writerow([url])
            list_link.append(url)
            print(url)
    return list_link
    # except:
    #     print('Missing ', i)

search=input("NHẬP TỪ KHÓA CẦN TÌM TẠI ĐÂY: ")
search=search.strip()
search=search.lower()
search=search.replace(" ", "%20")
#for i in len(search):
search_url_dict= 'https://shopee.vn/search?keyword='+ str(search)
print (search_url_dict)

list_link= collect_search_page(search_url_dict, pages_per_category=1)


def load_url_selenium_shopee(url):
    # Selenium
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # driver=webdriver.Chrome('E:/chromedriver_win32/chromedriver_win32/chromedriver.exe')
    print("Loading url=", url)
    driver.get(url)
    # list_review = []
    # list_time=[]

    list_sum = []
    # lấy 10 page cmt đầu tiên
    x = 0
    try:
        while x < 10:
            try:
                time.sleep(1)
                total_height = int(driver.execute_script("return document.body.scrollHeight"))

                for i in range(0, total_height, 100):
                    driver.execute_script("window.scrollTo(0, {});".format(i))

                WebDriverWait(driver, 5).until(
                    EC.visibility_of_all_elements_located((By.CSS_SELECTOR, "div.shopee-product-rating")))

            except:
                print('No has comment')
                break

            product_reviews = driver.find_elements_by_css_selector("[class='shopee-product-rating']")
            # Get product review
            for product in product_reviews:
                list_per_comment = []
                # review = product.find_element_by_css_selector("[class='shopee-product-rating__content']").text
                review = product.find_element_by_css_selector("[class='_3NrdYc']").text
                day = product.find_element_by_css_selector("[class='shopee-product-rating__time']").text
                if (review != "" or review.strip()):
                    print(review, "/n")
                    # list_review.append(review)
                    # list_time.append(day)
                    list_per_comment.append(day)
                    list_per_comment.append(review)
                    list_per_comment.append('shopee')
                    list_sum.append(list_per_comment)
            # Check for button next-pagination-item have disable attribute then jump from loop else click on the next button

            if len(driver.find_elements_by_css_selector(
                    "button.shopee-icon-button.shopee-icon-button--right[disabled]")) > 0:
                break;
            else:
                button_next = WebDriverWait(driver, 5).until(EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "button.shopee-icon-button.shopee-icon-button--right")))
                # driver.execute_script("arguments[0].click();", button_next)
                button_next.click()
                print("next page")
                time.sleep(2)
                x += 1

    except NoSuchElementException:
        driver.close()

    # list_sum=list(zip(list_time,list_review))
    # list_sum.append(list_per_comment)
    return list_sum

data_shopee=[]
#temp=[]
for i in range(len(list_link)):
    data_shopee.append(load_url_selenium_shopee(url=list_link[i]))
print (data_shopee)