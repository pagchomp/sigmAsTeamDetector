# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 11:30:35 2017

@author: Brett Burk
"""
#TODO: Fix thead

import os
import time
import json
import webbrowser
import urllib.request

stratzAPI = "https://apibeta.stratz.com/api/v1/"
#playerID = "84195549"

colorsDota = ["Blue", "Teal", "Purple", "Yellow", "Orange",
              "Pink", "Grey", "LightBlue", "Green", "Brown"]
lanes = ["Roaming", "Safe Lane", "Mid", "Offlane", "Jungle"]
activity = ["None", "Very Low", "Low", "Medium", "High", "Very High", "Intense"]
rowOrder = ['color', 'playerName', 'avatar', 'recentWinPct', 'recentMMRAvg', 'partyMMR', 
            'soloMMR', 'matches', 'rankedPct', 'activity', 'impact', 'partyPct', 'supports', 
            'cores', 'uniqueHeroes', 'heroes', 'lanesL']
#table {
#    border-collapse: collapse;
#    width: 100%;
#}
#
#th, td {
#    text-align: left;
#    padding: 8px;
#}
css = """<style type="text/css">
table, th, td {
    border: 1px solid black;
    line-height: 14px;
}
.zui-table-zebra tbody tr:nth-child(odd) {
    background-color: #fff;
}
.zui-table-zebra tbody tr:nth-child(even) {
    background-color: #EEF7EE;
}
.zui-table {
    border: solid 1px #DDEEEE;
    border-collapse: collapse;
    border-spacing: 0;
    font: normal 13px Arial, sans-serif;
}
.zui-table thead th {
    background-color: #DDEFEF;
    border: solid 1px #DDEEEE;
    color: #336B6B;
    padding: 10px;
    text-align: center;
    text-shadow: 1px 1px 1px #fff;
}
.zui-table tbody td {
    border: solid 1px #DDEEEE;
    color: #333;
    padding: 10px;
    text-shadow: 1px 1px 1px #fff;
}
.zui-table-zebra tbody tr:nth-child(odd) {
    background-color: #fff;
}
.zui-table-zebra tbody tr:nth-child(even) {
    background-color: #EEF7EE;
}
.zui-table-horizontal tbody td {
    border-left: none;
    border-right: none;
}
.Blue{
    background-color: #2E6AE6 !important;
}
.Teal{
    background-color: #5DE6AD !important;
}
.Purple{
    background-color: #AD00AD !important;
}
.Yellow{
    background-color: #DCD90A !important;
}
.Orange{
    background-color: #E66200 !important;
}
.Pink{
    background-color: #E67AB0 !important;
}
.Grey{
    background-color: #92A440 !important;
}
.LightBlue{
    background-color: #5CC5E0 !important;
}
.Green{
    background-color: #00771F !important;
}
.Brown{
    background-color: #956000 !important;
}

table {
    border-collapse: collapse;
}


</style>
"""
#    word-break: break-all;
#    word-wrap:break-word;
colNamesDict = {'playerName': "Player Name",
        'supports' : "Support",
        'cores' : "Core",
        'recentMMRAvg' : "Recent MMR",
        'heroes' : "Heroes",
        'lanesL' : "Lanes",
        'uniqueHeroes' : "Unique Heroes",
        'recentWinPct' : "Recent Win %",
        'partyMMR' : "Party MMR",
        'soloMMR' : "Solo MMR",
        'matches' : "Total Matches",
        'avatar' : "Picture",
        'color' : "Color",
        'rankedPct' : "Ranked",
        'activity' : "Activity Level",
        'impact' : "Impact",
        'partyPct' : "Party Percent"
}

def getMean(nums):
    summation = 0
    for i in nums:
        summation += i
    return summation/len(nums)

def getDivision(first, second):
    results = [0] * len(first)
    for i in range(len(first)):
        if second[i] > 0:
            results[i] = int(round((first[i] / second[i]) * 100, 0))
        else:
            results[i] = 0
    return results
                   

def loadHeroes():
    print('Loading Dota Games. . .')
    heroDict = {}
    heroLoad = json.loads(urllib.request.urlopen(stratzAPI +
                                          "hero").read().decode('utf-8'))
    for i in heroLoad:
        heroDict[i] = heroLoad[i]['displayName']
    return heroDict
    
def idNewGame():
    with open(currFile) as myfile:
        currLine = -1
        searchingGame = True
        temp = list(myfile)
        while searchingGame:
            currGame = temp[currLine]
            currGame = currGame[currGame.find("(")+1:currGame.find(")")].split()
            if "DOTA_GAMEMODE" in currGame[2] and len(currGame) >= 13:
                return currGame
            else:
                currLine -= 1

def pullData(playerID):
    playerWeb = stratzAPI + "player/"
    behavior = json.loads(urllib.request.urlopen(playerWeb +
                                                 playerID +
                                                 "/behaviorChart").read().decode('utf-8'))
    player = json.loads(urllib.request.urlopen(playerWeb +
                                               playerID).read().decode('utf-8'))
    playerDict = {'playerName': player['name'],
        'supports' : 0,
        'cores' : 0,
        'recentMMRAvg' : 0,
        'heroes' : [],
        'lanesL' : [0, 0, 0, 0, 0],
        'lanesWin' : [0, 0, 0, 0, 0],
        'uniqueHeroes' : 0,
        'recentWinPct' : 0,
        'partyMMR' : 0,
        'soloMMR' : 0,
        'matches' : 0,
        'avatar' : "",
        'color' : "",
        'rankedPct' : 0,
        'activity' : "",
        'impact' : "",
        'partyPct' : 0
            }
    try:
        playerDict['supports'] = int(round((behavior['supportCount']/(behavior['supportCount'] +
                                                        behavior['coreCount'])) * 100, 0))
        playerDict['cores'] = 100 - playerDict['supports']
        playerDict['recentMMRAvg'] = int(round(getMean([k['rank'] for k in behavior['matches']]), 0))
        playerDict['recentWinPct'] = int(round(100 * behavior['winCount']/behavior['matchCount'], 0))
        heroes = behavior['heroes']
        playerDict['uniqueHeroes'] = len(heroes)
        playerDict['rankedPct'] = int(round(behavior['rankedCount']/.25, 0))
        playerDict['partyPct'] = int(round(behavior['partyCount']/.25, 0))
        playerDict['activity'] = activity[behavior['activity']]
        imp = behavior['avgImp']
        if imp >= 109:
            playerDict['impact'] = 'High'
        elif imp <= 91:
            playerDict['impact'] = 'Low'
        else:
            playerDict['impact'] = 'Medium'
        for hero in range(len(heroes)):
            currHero = heroes[hero]
            if currHero['matchCount'] > 2:
                heroName = heroDict[str(currHero['heroId'])]
                heroMatches = currHero['matchCount']
                heroWinPct = int(round((currHero['winCount']/heroMatches) * 100))
                playerDict['heroes'].append([heroName, heroMatches, heroWinPct])
            currLane = currHero['lanes']
            for l in currLane:
                playerDict['lanesL'][l['lane']] += l['matchCount']
                playerDict['lanesWin'][l['lane']] += l['winCount']
        playerDict['lanesWin'] = getDivision(playerDict['lanesWin'], playerDict['lanesL'])
    except:
        print("No recent behavior data for " + str(player['name']))
    try:
        playerDict['partyMMR'] = player['mmrDetail']['partyValue']
        playerDict['soloMMR'] = player['mmrDetail']['soloValue']
        playerDict['avatar'] = player['avatar']
    except:
        print("No MMR data for " + str(player['name']))
    try:
        playerDict['matches'] = json.loads(urllib.request.urlopen(stratzAPI +
                                                    "match/?steamId=" +
                                                    playerID).read().decode('utf-8'))['total']
    except:
        print("no matches data for " + str(player['name']))
    return(playerDict)

def outHeroesLanes(playerDict):
    out = ""
    for row in rowOrder:
        if row == "heroes":
            heroL = "<td><table>"
            for hero in playerDict['heroes']:
                heroL += "<tr><td>"
                heroL += hero[0]
                heroL += "</td><td>" + str(hero[1]) + "</td><td>" + str(hero[2]) + "%" + "</td><tr>"
            out += heroL + "</table></td>"
        elif row == "lanesL":
            laneL = "<td><table>"
            for lane in range(5):
                if playerDict['lanesL'][lane] > 0:
                    laneL += "<tr><td>%s</td><td>%s%%</td><td>%s%%</td><tr>" % (lanes[lane], str(int(round((playerDict['lanesL'][lane]/25)* 100))),  str(playerDict['lanesWin'][lane]))
            out += laneL + "</table></td>"
        elif row == "avatar":
            out+= "<td><img src = '%s'></td>" % str(playerDict[row])
        elif row == "color":
            out += "<td class = %s></td>" % playerDict['color']
        else:
            currStr = str(playerDict[row])
            if row in ['recentWinPct', 'supports', 'cores', 'rankedPct', 'partyPct']:
                currStr += "%"
            out += "<td>%s</td>" % currStr
    return out

def genHTML(output):
    print('Generating Website...')
    Html_file = open("teamChecker.html", "w", encoding = "utf-8")
    Html_file.write(output)
    Html_file.close()
    webbrowser.open("teamChecker.html")

class Checker(object):
    def __init__(self):
        self._cached_stamp = 0
        self.filename = currFile

    def check(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            print('New Game Found!')
            currGame = idNewGame()
            del currGame[:3]
            output = css
            output += "<html><body><h1>sigmA's Team Detective v2</h1>"
            factions = ['RADIANT', 'DIRE']
            output += "<table>"
            print('Gathering Player Data. . .')
            #DataFrame(dict([ (k,Series(v)) for k,v in d.items() ]))
            #playerID = "84195549"
            for i in range(10):
                 #<td bgcolor="#FF0000">
                playerID = currGame[i][3:-1].split(":")[2]
                outData = pullData(playerID)
                outData['color'] = colorsDota[i]
                if i == 0 or i == 5:
                    output += "</table><br><h2>%s</h2><table class=\"zui-table zui-table-zebra zui-table-horizontal\">" % factions[i == 5]
                    output += "<tr>"
                    for currCol in rowOrder:
                        output += "<td>%s</td>" % str(colNamesDict[currCol]) 
                    output += "</tr>"
                output += "<tr>%s</tr>" % outHeroesLanes(outData)
            output += "</table>"
            output += "</body></html>"
            genHTML(output)
            print('Finished!')
            print('Searching for new games...')
        
def trier():
    pub = Checker()
    while True:
        try:
            time.sleep(5)
            pub.check()
        except:
            print('failed')
            time.sleep(2)
            trier()

dotaFolder = "C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/"
currFile = os.path.join(dotaFolder, "server_log.txt")
heroDict = loadHeroes()

trier()