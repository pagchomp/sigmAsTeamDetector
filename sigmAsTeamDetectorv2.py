# -*- coding: utf-8 -*-
"""
This script downloads data from the stratz api and uses it to create a dashboard for teammates/enemies in a game of Dota 2
Created on Fri Aug  4 11:30:35 2017

@author: Brett Burk
"""

import os
import time
import json
import webbrowser
import urllib.request

STRATZ_API = "https://api.stratz.com/api/v1/"
# My player id (kept for testing)
# player_id = "84195549"

COLORS_DOTA = ["Blue", "Teal", "Purple", "Yellow", "Orange",
               "Pink", "Grey", "LightBlue", "Green", "Brown"]
LANES = ["Roaming", "Safe Lane", "Mid", "Offlane", "Jungle"]
ACTIVITY = ["None", "Very Low", "Low", "Medium", "High", "Very High", "Intense"]
ROW_ORDER = ['color', 'player_name', 'avatar', 'recent_win_pct', 'recent_mmr_avg', 'party_mmr',
             'solo_mmr', 'matches', 'ranked_pct', 'activity', 'impact', 'party_pct', 'supports',
             'cores', 'unique_heroes', 'heroes', 'lanes_played']

PROPER_NAMES_DICT = {'player_name': "Player Name",
                     'supports' : "Support",
                     'cores' : "Core",
                     'recent_mmr_avg' : "Recent MMR",
                     'heroes' : "Heroes",
                     'lanes_played' : "Lanes",
                     'unique_heroes' : "Unique Heroes",
                     'recent_win_pct' : "Recent Win %",
                     'party_mmr' : "Party MMR",
                     'solo_mmr' : "Solo MMR",
                     'matches' : "Total Matches",
                     'avatar' : "Picture",
                     'color' : "Color",
                     'ranked_pct' : "Ranked",
                     'activity' : "Activity Level",
                     'impact' : "Impact",
                     'party_pct' : "Party Percent"
                    }
TOOL_TITLE = "sigmA's Team Detector BETA v.4"

CSS = """<style type="text/css">
h1 {
    text-align: center;
}
h2 {
    text-align: center;
}
table {
    border: solid 1px #DDEEEE;
    border-collapse: collapse;
    border-spacing: 0;
    font: normal 13px Arial, sans-serif;
    border-left: none;
    border-right: none;
}
td {
    border-top: solid 1px #DDEEEE;
    color: #333;
    padding: 10px;
    text-shadow: 1px 1px 1px #fff;
}
tr:nth-child(even){background-color: #EEF7EE;}
tr:nth-child(odd){background-color: #fff;}
th {
    border: solid 1px #DDEEEE;
    background-color: #DDEFEF;
    border: solid 1px #DDEEEE;
    color: #336B6B;
    padding: 10px;
    text-align: center;
    text-shadow: 1px 1px 1px #fff;
}
.Blue{background-color: #2E6AE6;}
.Teal{background-color: #5DE6AD;}
.Purple{background-color: #AD00AD;}
.Yellow{background-color: #DCD90A;}
.Orange{background-color: #E66200;}
.Pink{background-color: #E67AB0;}
.Grey{background-color: #92A440;}
.LightBlue{background-color: #5CC5E0;}
.Green{background-color: #00771F;}
.Brown{background-color: #956000;}
</style>
"""

javascript = """<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script><script>
function copyToClipboard(element) {
  var $temp = $('<input>');
  $('body').append($temp);
  $temp.val($(element).text()).select();
  document.execCommand('copy');
  $temp.remove();
}
</script>
"""

def get_mean(nums):
    """Simple calculation of mean"""
    summation = 0
    for i in nums:
        summation += i
    return summation/len(nums)

def get_division(first, second):
    """Simple division calculation"""
    results = [0] * len(first)
    for i, item in enumerate(second):
        if item > 0:
            results[i] = int(round((first[i] / second[i]) * 100, 0))
        else:
            results[i] = 0
    return results

def load_heroes():
    """Loads in hero data to match hero number to name"""
    print('Loading Dota Games. . .')
    hero_dict = {}
    hero_load = json.loads(urllib.request.urlopen(STRATZ_API +
                                                  "hero").read().decode('utf-8'))
    for i in hero_load:
        hero_dict[i] = hero_load[i]['displayName']
    return hero_dict

def id_new_game():
    """Attempts to identify the most recent actual game of dota"""
    with open(CURR_FILE) as my_file:
        curr_line = -1
        searching_game = True
        temp = list(my_file)
        while searching_game:
            curr_game = temp[curr_line]
            curr_game = curr_game[curr_game.find("(")+1:curr_game.find(")")].split()
            if "DOTA_GAMEMODE" in curr_game[2] and len(curr_game) >= 13:
                return curr_game
            else:
                curr_line -= 1

def pull_data(player_id):
    """Pulls and creates all data"""
    player_web = STRATZ_API + "player/"
    player_dict = {'player_name': "",
                   'supports' : 0,
                   'cores' : 0,
                   'recent_mmr_avg' : 0,
                   'heroes' : [],
                   'lanes_played' : [0, 0, 0, 0, 0],
                   'lanesWin' : [0, 0, 0, 0, 0],
                   'unique_heroes' : 0,
                   'recent_win_pct' : 0,
                   'party_mmr' : 0,
                   'solo_mmr' : 0,
                   'matches' : 0,
                   'avatar' : "",
                   'color' : "",
                   'ranked_pct' : 0,
                   'activity' : "",
                   'impact' : "",
                   'party_pct' : 0,
                   'match_count' : 0
                  }
    try:
        player = json.loads(urllib.request.urlopen(player_web +
                                               player_id).read().decode('utf-8'))
        behavior = json.loads(urllib.request.urlopen(player_web +
                                                 player_id +
                                                 "/behaviorChart?take=250").read().decode('utf-8'))
        try:
            player_dict['player_name'] = player['name']
            player_dict['match_count'] = behavior['matchCount']
            player_dict['supports'] = int(round((behavior['supportCount']/(behavior['supportCount'] +
                                                                           behavior['coreCount'])) * 100, 0))
            player_dict['cores'] = 100 - player_dict['supports']
            player_dict['recent_mmr_avg'] = int(round(get_mean([k['rank'] for k in behavior['matches']]), 0))
            player_dict['recent_win_pct'] = int(round(100 * behavior['winCount']/player_dict['match_count'], 0))
            heroes = behavior['heroes']
            player_dict['unique_heroes'] = len(heroes)
            player_dict['ranked_pct'] = int(round((behavior['rankedCount']/player_dict['match_count']) * 100, 0))
            player_dict['party_pct'] = int(round((behavior['partyCount']/player_dict['match_count']) * 100, 0))
            player_dict['activity'] = ACTIVITY[behavior['activity']]
            if behavior['avgImp'] >= 109:
                player_dict['impact'] = 'High'
            elif behavior['avgImp'] <= 91:
                player_dict['impact'] = 'Low'
            else:
                player_dict['impact'] = 'Medium'
            for curr_hero in heroes:
                if curr_hero['matchCount'] >= player_dict['match_count']/5:
                    hero_name = HERO_DICT[str(curr_hero['heroId'])]
                    hero_matches = curr_hero['matchCount']
                    hero_win_pct = int(round((curr_hero['winCount']/hero_matches) * 100))
                    player_dict['heroes'].append([hero_name, hero_matches, hero_win_pct])
                curr_lane = curr_hero['lanes']
                for la in curr_lane:
                    player_dict['lanes_played'][la['lane']] += la['matchCount']
                    player_dict['lanesWin'][la['lane']] += la['winCount']
            player_dict['lanesWin'] = get_division(player_dict['lanesWin'], player_dict['lanes_played'])
        except Exception as e:
            print("No %s data for %s." % (str(e), str(player['name'])))
    except:
        print("No player information found for player #" + player_id)
        return player_dict
    try:
        player_dict['party_mmr'] = player['mmrDetail']['partyValue']
        player_dict['solo_mmr'] = player['mmrDetail']['soloValue']
        player_dict['avatar'] = player['avatar']
    except Exception as e:
        print("No %s data for %s." % (str(e), str(player['name'])))
    try:
        player_dict['matches'] = json.loads(urllib.request.urlopen(STRATZ_API +
                                                                   "match/?steamId=" +
                                                                   player_id).read().decode('utf-8'))['total']
    except Exception as e:
        print("No %s data for %s." % (str(e), str(player['name'])))
    return player_dict

def out_heroes_lanes(player_dict):
    """Outputs the data in HTML"""
    out = ""
    for row in ROW_ORDER:
        if row == "heroes":
            # Heroes
            hero_out = "<td><table>"
            if len(player_dict['heroes']) >= 1:
                hero_out += "<thead><th>Hero</th><th>#</th><th>Win</th></thead>"
                for hero in player_dict['heroes']:
                    highlight_color = ""
                    if hero[2] >= 60:
                        highlight_color = 'style="color:green"'
                    elif hero[2] <= 40:
                        highlight_color = 'style="color:red"'
                    hero_out += "<tr><td>"
                    hero_out += hero[0]
                    hero_out += "</td><td>" + str(hero[1])
                    hero_out += "</td><td %s>%s%%" % (highlight_color, str(hero[2]))
                    hero_out += "</td><tr>"
            out += hero_out + "</table></td>"
        elif row == "lanes_played":
            # Lanes
            lane_out = "<td><table>"
            if len(player_dict['heroes']) >= 1:
                lane_out += "<thead><th>Lane</th><th>Play</th><th>Win</th></thead>"
                for lane in range(5):

#                    if player_dict['lanes_played'][lane] > 5:
                    highlight_color = ""
                    if player_dict['lanesWin'][lane] >= 60:
                        highlight_color = 'style="color:green"'
                    elif player_dict['lanesWin'][lane] <= 40:
                        highlight_color = 'style="color:red"'
                    lane_out += "<tr><td>%s</td><td>%s%%</td><td %s>%s%%</td><tr>" % (LANES[lane],
                                                                                      str(int(round((player_dict['lanes_played'][lane]/player_dict['match_count'])* 100))),
                                                                                      highlight_color,
                                                                                      str(player_dict['lanesWin'][lane]))
            out += lane_out + "</table></td>"
        elif row == "avatar":
            # Draw pictures
            out += "<td><img src = '%s'></td>" % str(player_dict[row])
        elif row == "color":
            # Colors
            out += "<td class = \"%s\"></td>" % player_dict['color']
        else:
            str_out = player_dict[row]
            # Rows with percents in them
            highlight_color = ""
            if row in ['recent_win_pct', 'supports', 'cores', 'ranked_pct', 'party_pct']:
                if str_out > 60:
                    highlight_color = 'style="color:green"'
                elif str_out < 40:
                    highlight_color = 'style="color:red"'
                str_out = str(str_out) + "%"
            out += "<td %s>%s</td>" % (highlight_color, str(str_out))
    return out

def gen_html(output):
    """Creates the html document"""
    print('Generating Website...')
    html_file = open("teamChecker.html", "w", encoding="utf-8")
    html_file.write(output)
    html_file.close()
    webbrowser.open("teamChecker.html")

class Checker(object):
    """Checker class"""
    def __init__(self):
        """Initializes with filename"""
        self._cached_stamp = 0
        self.filename = CURR_FILE
    def check(self):
        """Checks for updated file, and if so queries most recent game"""
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            print('New Game Found!')
            curr_game = id_new_game()
            del curr_game[:3]
            output = "<!DOCTYPE html><html>"
            output += CSS
            output += "<body><title>%s</title><h1>%s</h1>" % (TOOL_TITLE, TOOL_TITLE)
            output += javascript
            output += "<button onclick=\"copyToClipboard('#p1')\">Copy TEXT 1</button>"
            factions = ['RADIANT', 'DIRE']
            output += "<table>"
            print('Gathering Player Data. . .')
            for i in range(10):
                player_id = curr_game[i][3:-1].split(":")[2]
                out_data = pull_data(player_id)
                out_data['color'] = COLORS_DOTA[i]
                if i == 0 or i == 5:
                    output += "</table><br><h2>%s</h2><table>" % factions[i == 5]
                    output += "<tr>"
                    for curr_col in ROW_ORDER:
                        output += "<td>%s</td>" % str(PROPER_NAMES_DICT[curr_col])
                    output += "</tr>"
                output += "<tr id = 'p%s'>%s</tr>" % (i, out_heroes_lanes(out_data))
            output += "</table>"
            output += "</body></html>"
            gen_html(output)
            print('Finished!')
            print('Searching for new games...')

def main():
    global DOTA_FOLDER, CURR_FILE, HERO_DICT
    DOTA_FOLDER = "C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/"
    CURR_FILE = os.path.join(DOTA_FOLDER, "server_log.txt")
    while not os.path.isfile(CURR_FILE):
        CURR_FILE = input("Please enter the dota 2 beta directory e.g. 'C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/':\n")
        CURR_FILE = os.path.join(CURR_FILE,  "game/dota/server_log.txt")
    HERO_DICT = load_heroes()
    pub = Checker()
    while True:
        try:
            time.sleep(5)
            pub.check()
        except Exception as e:
            print('Error Parsing Game: %s' % str(e))
            time.sleep(2)
            main()
    # my code here

if __name__ == "__main__":
    main()
