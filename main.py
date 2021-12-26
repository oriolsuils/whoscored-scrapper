#!/usr/bin/env python
from selenium import webdriver 
import time
import os
import sys
from Team import Team
from webdriver_manager.chrome import ChromeDriverManager
import threading

LA_LIGA_ENDPOINT = "https://www.whoscored.com/Regions/206/Tournaments/4/Espa%C3%B1a-LaLiga"
PREMIER_LEAGUE_ENDPOINT = "https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League"
SERIE_A_ENDPOINT = "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A"
BUNDESLIGA_ENDPOINT = "https://www.whoscored.com/Regions/81/Tournaments/3/Germany-Bundesliga"
LIGUE_1_ENDPOINT = "https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1"
UCL_ENDPOINT = "https://www.whoscored.com/Regions/250/Tournaments/12/Seasons/8177/Stages/19009/Show/Europe-Champions-League-2020-2021"
UEL_ENDPOINT = "https://www.whoscored.com/Regions/250/Tournaments/30/Seasons/8178/Stages/19010/Show/Europe-Europa-League-2020-2021"
LIVE_MATCHES_ENDPOINT = "https://www.whoscored.com/LiveScores#live"

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

def getDataByLinks(links, team=""):
  driver = initDriver()
  for link in links:
    json = getJSON(driver, link)
    if(len(json) > 0):
      matchCentreData = json[0]
      formationIdNameMappings = json[1]
      name = getFileName(link, team)
      f = open(name+'.json', 'w', encoding='utf-8')
      try:
        f.write("[")
        f.write(matchCentreData)
        f.write(",")
        f.write(formationIdNameMappings)
        f.write("]")
      finally:
        f.close()
        os.chdir("../..")
  driver.close()

def getFileName(link, team=""):
  link = link[link.find("/Live/")+6:]
  indexLastNumber = findLastNumberPosition(link)
  folderName = link[:indexLastNumber]
  dir = os.path.join((os.path.dirname(os.path.realpath(__file__))),folderName)
  if not os.path.exists(dir):
    os.mkdir(dir)
  os.chdir(dir)

  if team != "":
    dir = os.path.join(dir,team.getName())
    if not os.path.exists(dir):
      os.mkdir(dir)
    os.chdir(dir)
  
  matchName = link[indexLastNumber+1:]
  return matchName

def findLastNumberPosition(text):
  idx = text.find("2021-2022")
  if(idx < 0):
    idx = text.find("2020-2021")
  if(idx < 0):
    idx = text.find("2019-2020")
  return idx+9

def getJSON(driver, link):
  data = []
  driver.get(link)
  time.sleep(10)
  raw_result = driver.find_elements_by_xpath(("//*[@id='layout-wrapper']/script[1]"))[0]
  raw_result = raw_result.get_attribute("innerHTML")
  if "matchCentreData" not in raw_result:
    return data
  matchCentreData = raw_result[raw_result.find("matchCentreData"):raw_result.find("matchCentreEventTypeJson")]
  matchCentreData = matchCentreData[matchCentreData.find("{"):matchCentreData.find(",\n")]
  data.append(matchCentreData)
  formationIdNameMappings = raw_result[raw_result.find("formationIdNameMappings"):]
  formationIdNameMappings = formationIdNameMappings[formationIdNameMappings.find("{"):formationIdNameMappings.find("\n        };")]
  data.append(formationIdNameMappings)
  return data

def getAllTeamsByLeague(path):
  teams = []
  driver = initDriver()
  driver.get(path)
  time.sleep(2)
  teamsList = driver.find_elements_by_xpath("//*[starts-with(@id, 'standings-')]/tr[*]/td[*]/a[@class='team-link ']")
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

def saveDataSingleMatch(link):
  driver = initDriver()
  json = getJSON(driver, link)
  if(len(json) > 0):
    matchCentreData = json[0]
    formationIdNameMappings = json[1]
    name = getFileName(link)
    f = open(name+'.json', 'w', encoding='utf-8')
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

def getAllLiveMatches():
  driver = initDriver()
  data = []
  driver.get(LIVE_MATCHES_ENDPOINT)
  competitions = driver.find_elements_by_xpath("//div[contains(@class, 'divtable-row group')]")
  i = 0
  while i < len(competitions):
    competition_json = {}
    competition_json["matches"] = []
    div = competitions[i]
    competition_id = div.get_attribute("id")
    competition_label = driver.find_elements_by_xpath("//*[@id='"+competition_id+"']/div[2]/div/a/span")
    competition_label = competition_label[0].get_attribute("innerHTML")
    competition_label = competition_label[competition_label.find("</span>")+7:]
    competition_json["id"] = competition_id
    competition_json["label"] = competition_label
    matches_div = driver.find_elements_by_xpath("//*[@data-group-id='"+competition_id[1:]+"']")
    j = 0
    while j < len(matches_div):
      match_json = {}
      match_id = matches_div[j].get_attribute("id")
      div_match = driver.find_elements_by_xpath("//*[@id='"+match_id+"']")
      if(len(div_match) > 0):
        anchor_match = div_match[0].find_elements_by_css_selector("a.horiz-match-link.result-2.rc")
        if(len(anchor_match) > 0):
          home_team = div_match[0].find_elements_by_xpath("//*[@id='"+match_id+"']/div[6]/a/span")
          away_team = div_match[0].find_elements_by_xpath("//*[@id='"+match_id+"']/div[8]/a/span")
          time_elapsed = div_match[0].find_elements_by_xpath("//*[@id='"+match_id+"']/div[3]/span[3]/span")
          match_json["id"] = match_id
          match_json["url"] = anchor_match[0].get_attribute("href")
          match_json["result"] = anchor_match[0].get_attribute("innerHTML")
          match_json["homeTeam"] = home_team[0].get_attribute("innerHTML")
          match_json["awayTeam"] = away_team[0].get_attribute("innerHTML")
          match_json["timeElapsed"] = time_elapsed[0].get_attribute("innerHTML")
          competition_json["matches"].append(match_json)
      j += 1
    if len(competition_json["matches"]) > 0:
      data.append(competition_json)
    i += 1
  return data

def menu():
  toQuit = False
  option = 0
  while not toQuit:
    print ("1. Get JSON data entering team URL")
    print ("2. Select team from LaLiga")
    print ("3. Get JSON data entering single match")
    print ("4. Get JSON data from La Liga (Spain), Premier League (England), Serie A (Italy), Bundesliga (Germany), Ligue 1 (France), UCL and UEL")
    print ("5. Live match")
    print ("6. Get list of live matches")
    print ("7. Exit")
    print ("Please, choose an option")
    option = askNumber()

    if option == 1:
      url = str(input("(e.g. https://www.whoscored.com/Teams/819/Show/Spain-Getafe)\nURL: "))
      links = getAllLinksTeam(url)
      getDataByLinks(links)
      print("Job finished")
    elif option == 2:
      teams = getAllTeamsByLeague(LA_LIGA_ENDPOINT)
      team = subMenuTeams(teams)
      links = getAllLinksTeam(team.getWebURL())
      getDataByLinks(links)
      print("Job finished")
    elif option == 3:
      url = str(input("(e.g. https://www.whoscored.com/Matches/1492131/Live/Spain-LaLiga-2020-2021-Athletic-Bilbao-Getafe)\nURL:"))
      saveDataSingleMatch(url)
      print("Job finished")
    elif option == 4:
      getJsonFromAllTeams()
      print("Job finished")
    elif option == 5:
      url = str(input("(e.g. https://www.whoscored.com/Matches/1492131/Live/Spain-LaLiga-2020-2021-Athletic-Bilbao-Getafe)\nURL: "))
      ticker = threading.Event()
      while not ticker.wait(60.0):
        saveDataSingleMatch(url)
        if checkIfMatchEnded(url):
          break
      print("Job finished")
    elif option == 6:
      print(getAllLiveMatches())
    elif option == 7:
      toQuit = True
    else:
      print ("Enter a number between 1 and 4")
  print ("Bye")
  sys.exit()

def checkIfMatchEnded(url):
  ended = False
  driver = initDriver()
  driver.get(url)
  time.sleep(10)
  raw_result = driver.find_elements_by_xpath(("//*[@id='match-header']/table/tbody/tr[2]/td[2]/div[1]/dl/dd/span"))[0]
  raw_result = raw_result.get_attribute("innerHTML")
  if raw_result == "FT":
    ended = True
  return ended

def getJsonFromAllTeams():
  teams = getAllTeamsByLeague(LA_LIGA_ENDPOINT)
  teams += getAllTeamsByLeague(PREMIER_LEAGUE_ENDPOINT)
  teams += getAllTeamsByLeague(SERIE_A_ENDPOINT)
  teams += getAllTeamsByLeague(BUNDESLIGA_ENDPOINT)
  teams += getAllTeamsByLeague(LIGUE_1_ENDPOINT)
  teams += getAllTeamsByLeague(UCL_ENDPOINT)
  teams += getAllTeamsByLeague(UEL_ENDPOINT)
  teams = setUniqueTeams(teams)
  for team in teams:
    links = getAllLinksTeam(team.getWebURL())
    print("INI " + team.getName() + " - " + str(len(links)))
    getDataByLinks(links, team)
    print("FIN " + team.getName())

def setUniqueTeams(teams):
  unique_teams = []
  addTeam = True
  for team in teams:
    for ut in unique_teams:
      if team.getName() == ut.getName():
        addTeam = False
        break
    if addTeam:
      unique_teams.append(team)
    addTeam = True
  return unique_teams

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