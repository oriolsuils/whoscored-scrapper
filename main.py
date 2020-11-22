#!/usr/bin/env python
from selenium import webdriver 
import time
import os
import sys
from Team import Team
from webdriver_manager.chrome import ChromeDriverManager

def initDriver():
  driver = webdriver.Chrome(ChromeDriverManager().install())
  return driver

def getAllLinksTeam(baseURL):
  driver = initDriver()
  driver.get(baseURL)
  i = 0
  links = []
  time.sleep(2)
  matchesList = driver.find_elements_by_xpath("//*[@class='horiz-match-link result-1']")
  while i < len(matchesList):
    anchor = matchesList[i]
    links.append(anchor.get_attribute("href"))
    i += 1
  driver.close()
  return links

def getDataByLinks(links):
  driver = initDriver()
  for link in links:
    json = getJSON(driver, link)
    if(len(json) > 0):
      matchCentreData = json[0]
      formationIdNameMappings = json[1]
      name = getFileName(link)
      f = open(name+'.json', 'w')
      try:
        f.write("[")
        f.write(matchCentreData)
        f.write(",")
        f.write(formationIdNameMappings)
        f.write("]")
      finally:
        f.close()
        os.chdir("..")
  driver.close()

def getFileName(link):
  link = link[link.find("/Live/")+6:]
  indexLastNumber = findLastNumberPosition(link)
  folderName = link[:indexLastNumber+1]
  dir = os.path.join((os.path.dirname(os.path.realpath(__file__))),folderName)
  if not os.path.exists(dir):
    os.mkdir(dir)
  os.chdir(dir)
  
  matchName = link[indexLastNumber+2:]
  return matchName

def findLastNumberPosition(text):
  i=0
  lastIndex = 0
  while i < len(text):
    if text[i].isnumeric():
      lastIndex = i
    i+=1
  return lastIndex

def getJSON(driver, link):
  data = []
  driver.get(link)
  time.sleep(10)
  raw_result = driver.find_elements_by_xpath(("//*[@id='layout-wrapper']/script[1]"))[0]
  raw_result = raw_result.get_attribute("innerHTML")
  if "matchCentreData" not in raw_result:
    return data
  matchCentreData = raw_result[raw_result.find("{"):raw_result.find(";")]
  data.append(matchCentreData)
  formationIdNameMappings = raw_result[raw_result.find("formationIdNameMappings"):]
  formationIdNameMappings = formationIdNameMappings[formationIdNameMappings.find("{"):formationIdNameMappings.find(";")]
  data.append(formationIdNameMappings)
  return data

def getAllTeamsLaLiga():
  teams = []
  driver = initDriver()
  driver.get("https://www.whoscored.com/Regions/206/Tournaments/4/Espa%C3%B1a-LaLiga")
  time.sleep(2) 
  teamsList = driver.find_elements_by_xpath("//*[@id='standings-18851-content']/tr[*]/td[*]/a[@class='team-link ']")
  i = 0
  while i < len(teamsList):
    anchor = teamsList[i]
    teamURL = anchor.get_attribute("href")
    teamName = anchor.get_attribute("innerHTML")
    teamURL = teamURL.replace("/Show/","/Fixtures/")
    teams.append(Team(teamName, teamURL))
    i += 1
  driver.close()
  return teams

def menu():
  toQuit = False
  option = 0
  while not toQuit:
    print ("1. Get JSON data from team URL (e.g. https://www.whoscored.com/Teams/819/Show/Spain-Getafe)")
    print ("2. Select team from LaLiga")
    print ("3. Exit")
    print ("Please, choose an option")
    option = askNumber()

    if option == 1:
      url = str(input("URL: "))
      links = getAllLinksTeam(url)
      getDataByLinks(links)
      print("Job finished")
    elif option == 2:
      teams = getAllTeamsLaLiga()
      team = subMenuTeams(teams)
      links = getAllLinksTeam(team.getWebURL())
      getDataByLinks(links)
      print("Job finished")
    elif option == 3:
      toQuit = True
    else:
      print ("Enter a number between 1 and 3")
  print ("Bye")
  sys.exit()

def subMenuTeams(teamsList):
  toQuit = False
  option = 0
  while not toQuit:
    print("Select a team:")
    i=0
    while i<len(teamsList):
      print(str(i+1) + ". " + teamsList[i].getName())
      i+=1
    print(str(i+1) + ". Exit")
    option = askNumber()
    if option > 0 and option < len(teamsList):
      return teamsList[option-1]
    elif option == (len(teamsList)+1):
      toQuit = True
    else:
      print ("Enter a number between 1 and " + str(len(teamsList)+1))

def askNumber():
  right=False
  num=0
  while(not right):
    try:
      num = int(input("Enter a number: "))
      right=True
    except ValueError:
      print('Error, please enter a valid number')
  return num

menu()