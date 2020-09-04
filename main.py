from selenium import webdriver 
import time 
from bs4 import BeautifulSoup
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import time

options = Options()
options.add_argument('headless')
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
driver = webdriver.Chrome(executable_path ="C:\Program Files (x86)\Google\Chrome\chromedriver.exe") 
website_URL ="https://www.whoscored.com/Teams/65/Fixtures/Spain-Barcelona"
driver.get(website_URL)
laligaButton = driver.find_elements_by_xpath("//dl[@id='team-fixture-tournaments']//dd//a[@data-value='4']")[0]
driver.execute_script("arguments[0].click();", laligaButton)
i = 1
links = []
#time.sleep(2)
driver.implicitly_wait(2)
while i < 39:
  xpath = "//*[@id='team-fixtures']/div/div["+str(i)+"]/div[9]/a"
  anchor = driver.find_elements_by_xpath(xpath)[0]
  links.append(anchor.get_attribute("href"))
  i += 1

print(links)

for link in links:
  driver.implicitly_wait(10)
  driver.get(link)
  time.sleep(10)
  matchCentreData = driver.find_elements_by_xpath(("//*[@id='layout-wrapper']/script[1]"))[0]
  name = link[link.find("Spain-LaLiga-2019-2020-")+23:]

  f = open(name+'.txt', 'w')
  try:
    f.write(matchCentreData.get_attribute("innerHTML"))
  finally:
    f.close()