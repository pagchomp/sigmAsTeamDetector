# -*- coding: utf-8 -*-
"""
This script downloads data from the stratz api and uses it to create a dashboard for teammates/enemies in a game of Dota 2
Created on Fri Aug  4 11:30:35 2017

@author: Brett Burk
"""

"""
TODO:
Cleanup of display of paired players
"""

import os
import time
import json
import webbrowser
import urllib.request

TEST = True

# My player id (kept for testing)
# player_id = "84195549"
# player_id = "115392625"

TOOL_TITLE = "sigmA's Team Detector BETA v.7"

RECENT_GAMES = 100

STRATZ_API = "https://api.stratz.com/api/v1/"
COLORS_DOTA = ["Blue", "Teal", "Purple", "Yellow", "Orange",
               "Pink", "Grey", "LightBlue", "Green", "Brown"]
LANES = ["Roaming", "Safe Lane", "Mid", "Offlane", "Jungle"]
ACTIVITY = ["None", "Very Low", "Low", "Medium", "High", "Very High", "Intense"]
ROW_ORDER = ['player_name', 'avatar', 'recent_win_pct', 'recent_mmr_avg', 'party_mmr',
             'solo_mmr', 'matches', 'ranked_pct', 'activity', 'impact', 'party_pct', 'supports',
             'cores', 'unique_heroes', 'heroes', 'lanes_played']
COLUMN_WIDTHS = [10, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 19, 19]
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
                     'party_pct' : "Party Percent",
                     'p_id' : "Player ID"
                    }

CSS = """<style type="text/css">
h1 {
    text-align: center;
}
a.title{
        text-decoration: none;
        color: #111; 
        font-family: 'Open Sans Condensed', sans-serif; 
        font-size: 64px; 
        font-weight: 700; 
        line-height: 64px; 
        margin: 0 0 0;
        padding: 20px 30px; 
        text-align: center;
}
h2 {
    text-align: center;
    text-decoration: none;
    color: #111; 
    font-family: 'Open Sans Condensed', sans-serif; 
    font-size: 18px; 
    font-weight: 700; 
    line-height: 18px; 
    margin: 0 0 0;
    padding: 5px 5px; 
    text-align: left;
}
table {
    table-layout: fixed;
    width: 100%;
    border: solid 1px #DDEEEE;
    border-collapse: collapse;
    border-spacing: 0;
    font: normal 11px Arial, sans-serif;
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
table:first-child {
  font: normal 10px Arial, sans-serif;
  text-align:center;
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

.button {
  font: bold 12px Arial;
  text-decoration: none;
  background-color: #EEEEEE;
  color: #333333;
  padding: 2px 6px 2px 6px;
  border-top: 1px solid #CCCCCC;
  border-right: 1px solid #333333;
  border-bottom: 1px solid #333333;
  border-left: 1px solid #CCCCCC;
}

</style>
"""

javascript = """<script>
function setClipboard(value) {
    var tempInput = document.createElement("input");
    tempInput.style = "position: absolute; left: -1000px; top: -1000px";
    tempInput.value = value;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand("copy");
    document.body.removeChild(tempInput);
}
</script>
"""

def find_file(target, folder):
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        try:
            if os.path.isdir(path):
                result = find_file(target, path)
                if result is not None:
                    return result
                continue
            if f == target and "dota" in path:
                return path
        except:
            pass
        
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
                   'p_id' : "",
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
                   'match_count' : 0,
                   'recent_match_ids' : []
                  }
    try:
        player_dict['p_id'] = str(player_id)
        player = json.loads(urllib.request.urlopen(player_web +
                                               player_id).read().decode('utf-8'))
        behavior = json.loads(urllib.request.urlopen(player_web +
                                                 player_id +
                                                 "/behaviorChart?take=" +
                                                 str(RECENT_GAMES)).read().decode('utf-8'))
        matches = json.loads(urllib.request.urlopen(STRATZ_API +
                                                    "match/?steamid=" +
                                                    str(player_id) +
                                                    "&take=" +
                                                    str(RECENT_GAMES)).read().decode('utf-8'))
        try:

            player_dict['player_name'] = player['name']
            player_dict['match_count'] = behavior['matchCount']
            player_dict['supports'] = int(round((behavior['supportCount']/(behavior['supportCount'] +
                                                                           behavior['coreCount'])) * 100, 0))
            player_dict['cores'] = 100 - player_dict['supports']
            ranks_mean = []
            for k in behavior['matches']:
                if 'rank' in k:
                    ranks_mean.append(k['rank'])
            player_dict['recent_mmr_avg'] = int(round(get_mean(ranks_mean)))
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
                if curr_hero['matchCount'] >= RECENT_GAMES//12:
                    hero_name = HERO_DICT[str(curr_hero['heroId'])]
                    hero_matches = curr_hero['matchCount']
                    hero_win_pct = int(round((curr_hero['winCount']/hero_matches) * 100))
                    player_dict['heroes'].append([hero_name, hero_matches, hero_win_pct])
                curr_lane = curr_hero['lanes']
                for la in curr_lane:
                    player_dict['lanes_played'][la['lane']] += la['matchCount']
                    player_dict['lanesWin'][la['lane']] += la['winCount']
            player_dict['lanesWin'] = get_division(player_dict['lanesWin'], player_dict['lanes_played'])
            for match in matches['results']:
                player_dict['recent_match_ids'].append(match['id'])
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

def out_heroes_lanes(player_dict, p_num):
    """Outputs the data in HTML"""
    out = ""
    for row in ROW_ORDER:
        if row == "heroes":
            # Heroes            
            out += "<td>"
            if len(player_dict['heroes']) >= 1:
                hero_out = "<table>"
                hero_out += "<thead><th>Hero</th><th>#</th><th>Win</th></thead>"
                copy_data = COLORS_DOTA[p_num] + " in %s games: " % RECENT_GAMES
                for hero in player_dict['heroes']:
                    highlight_color = ""
                    if hero[2] >= 60:
                        highlight_color = 'style="color:green"'
                    elif hero[2] <= 40:
                        highlight_color = 'style="color:red"'
                    hero_out += "<tr><td>"
                    hero_out += hero[0]
                    copy_data += hero[0] + "-"
                    hero_out += "</td><td>" + str(hero[1])
                    copy_data += str(hero[1]) + "-"
                    hero_out += "</td><td %s>%s%%" % (highlight_color, str(hero[2]))
                    copy_data += str(hero[2]) + "% "
                    hero_out += "</td><tr>"
                hero_out += "</table><center><button onclick=\"setClipboard('%s')\">Copy</button></center></td>" % copy_data
                out += hero_out
            else:
                out += "</td>"
        elif row == "lanes_played":
            # Lanes data
            copy_data = COLORS_DOTA[p_num] + " in %s games: " % RECENT_GAMES
            lane_out = "<td><table>"
            lane_out += "<thead><th>Lane</th><th>Play</th><th>Win</th></thead>"
            for lane in range(5):
                lane_played = int(round((player_dict['lanes_played'][lane]/player_dict['match_count'])* 100))
                highlight_color_win = ""
                if player_dict['lanesWin'][lane] >= 60:
                    highlight_color_win = 'style="color:green"'
                elif player_dict['lanesWin'][lane] <= 40 and player_dict['lanes_played'][lane] != 0:
                    highlight_color_win = 'style="color:red"'
                if lane_played > 25:
                    row_style = " style='font-weight:800'"
                else:
                    row_style = ""
                if lane_played > 0:
                    copy_data += LANES[lane] + ": " + str(player_dict['lanes_played'][lane]) + "-" + str(player_dict['lanesWin'][lane]) + "% "
                lane_out += "<tr %s><td>%s</td><td>%s%%</td><td %s>%s%%</td></tr>" % (row_style,
                                                                                     LANES[lane],
                                                                                     str(lane_played),
                                                                                     highlight_color_win,
                                                                                     str(player_dict['lanesWin'][lane]))
            out += lane_out + "</table><center><button onclick=\"setClipboard('%s')\">Copy</button></center></td>" % copy_data
        elif row == "avatar":
            # Draw pictures
            out += "<td><img src = '%s'></td>" % str(player_dict[row])
        elif row == "player_name":
            # Colors
            out += "<td class = \"%s\" style = \"word-break: break-all;\"><a href = https://stratz.com/player/%s class = 'button' target='_blank'>%s</a></td>" % (player_dict['color'], player_dict['p_id'], player_dict['player_name'])
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
            output += "<body><title>%s</title><h1><a href = \"http://github.com/pagchomp\" class = \"title\">%s</a></h1>" % (TOOL_TITLE, TOOL_TITLE)
            output += javascript
            factions = ['RADIANT', 'DIRE']
            table_output = "<table>"
            print('Gathering Player Data. . .')
            mmr_data = ""
            matches = []
            for i in range(10):
                player_id = curr_game[i][3:-1].split(":")[2]
                out_data = pull_data(player_id)
                mmr_data += COLORS_DOTA[i] + ":" + str(out_data['solo_mmr']) + "/" + str(out_data['party_mmr']) + " "
                out_data['color'] = COLORS_DOTA[i]
                if i == 0 or i == 5:
                    table_output += "</table><br><h2>%s</h2><table>" % factions[i == 5]
                    table_output += "<tr>"
                    for curr_col in range(len(ROW_ORDER)):
                        table_output += "<td width = '%s%%'>%s</td>" % (str(COLUMN_WIDTHS[curr_col]), str(PROPER_NAMES_DICT[ROW_ORDER[curr_col]]))
                    table_output += "</tr>"
                table_output += "<tr>%s</tr>" % out_heroes_lanes(out_data, i)
                matches.append(out_data)
            table_output += "</table>"
            output += "<center><button onclick=\"setClipboard('%s')\">Copy MMRs</button></center><br>" % mmr_data
            output += table_output
            plays_together = ""
            # https://api.stratz.com/api/v1/match/?matchId=3416483753,3416451526
            for i in range(len(matches)):
                for j in range(i + 1, len(matches)):
                    shared_matches = set(matches[i]['recent_match_ids']) & set(matches[j]['recent_match_ids'])
                    shared_matches = [str(x) for x in shared_matches]
                    if len(shared_matches) > 0:
                        plays_together += "<br><a href = %s> %s and %s have played %s games together in the past %s</a><br>" % ("https://api.stratz.com/api/v1/match/?matchId=" +
                                                                                                                                ','.join(shared_matches),
                                                                                                                                matches[i]['player_name'], 
                                                                                                                                matches[j]['player_name'],
                                                                                                                                str(len(shared_matches)),
                                                                                                                                str(RECENT_GAMES))
            output += plays_together
            output += "<center>Powered by<br><a href = 'http://stratz.com'><img src = \"https://stratz.com/assets/img/stratz/Stratz_Icon_Full.53650306.png\"></a></center>"

            output += "</body></html>"
            gen_html(output)
            print('Finished!')
            print('Searching for new games...')

def main():
    global DOTA_FOLDER, CURR_FILE, HERO_DICT
    DOTA_FOLDER = "C:/Program Files (x86)/Steam/steamapps/common/dota 2 beta/game/dota/"
#    DOTA_FOLDER = "C:/Users/bmburk/Dropbox/sigmAsTeamDetector/"
    CURR_FILE = os.path.join(DOTA_FOLDER, "server_log.txt")
    while not os.path.isfile(CURR_FILE):
        print('Default folder does not contain Dota 2, please wait while the Dota 2 folder is found. . .')
        drives = [letter + ':\\' for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ']
        target = "server_log.txt"
        for drive in drives:
            if os.path.isdir(drive):
                filepath = find_file(target, drive)
                if filepath is not None:
                    break    
        CURR_FILE = os.path.join(filepath)
        print('Folder found!')
    HERO_DICT = load_heroes()
    pub = Checker()
    if TEST == True:
        pub.check()
    else:
        while True:
            try:
                time.sleep(5)
                pub.check()
            except Exception as e:
                print('Error Parsing Game: %s' % str(e))
                time.sleep(2)
                main()

if __name__ == "__main__":
    main()
