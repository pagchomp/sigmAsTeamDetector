# -*- coding: utf-8 -*-
"""
This script downloads data from the stratz api and uses it to create a
dashboard for teammates/enemies in a game of Dota 2
Created on Fri Aug  4 11:30:35 2017

@author: Brett Burk
"""
import os
import time
import json
import webbrowser
import urllib.request

"""
TODO:
    Recent Averages
    Double check for division by 0 errors
    2 seperate buttons for copying mmr info?
    Java version?
    Check if most recent game processed
"""

"""
My player id (kept for testing)
player_id = "84195549"
player_id = "115392625"
match_id = "3418564446"
"""

TOOL_TITLE = "sigmA's Team Detector 1.0"
TEST = False

RECENT_GAMES = 100
STRATZ_API = "https://api.stratz.com/api/v1/"
COLORS_DOTA = ["Blue", "Teal", "Purple", "Yellow", "Orange",
               "Pink", "Grey", "LightBlue", "Green", "Brown"]
LANES = ["Roaming", "Safe Lane", "Mid", "Offlane", "Jungle"]
ACTIVITY = ["None", "Very Low", "Low", "Medium",
            "High", "Very High", "Intense"]
ROW_ORDER = ['player_name', 'avatar', 'recent_win_pct', 'solo_mmr',
             'party_mmr', 'recent_mmr_avg', 'matches', 'ranked_pct',
             'activity', 'impact', 'party_pct', 'supports', 'cores',
             'unique_heroes', 'heroes', 'lanes_played', 'played_together']
IMPACT_UPPER = 109
IMPACT_LOWER = 91
COLUMN_WIDTHS = [10, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 19, 19, 19]
FACTIONS = ['RADIANT', 'DIRE']
PROPER_NAMES_DICT = {'player_name': "Player Name",
                     'supports': "Support",
                     'cores': "Core",
                     'recent_mmr_avg': "Recent MMR",
                     'heroes': "Heroes",
                     'lanes_played': "Lanes",
                     'unique_heroes': "Unique Heroes",
                     'recent_win_pct': "Recent Win %",
                     'party_mmr': "Party MMR",
                     'solo_mmr': "Solo MMR",
                     'matches': "Total Matches",
                     'avatar': "Picture",
                     'color': "Color",
                     'ranked_pct': "Ranked",
                     'activity': "Activity Level",
                     'impact': "Impact",
                     'party_pct': "Party Percent",
                     'p_id': "Player ID",
                     'played_together': "Played Together"
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
last_game = ""


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
            game_processor()


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


def to_percent(number):
    return int(round((number) * 100, 0))


def find_file(folder):
    """ Searches directories for the file """
    target = "server_log.txt"
    for f in os.listdir(folder):
        path = os.path.join(folder, f)
        try:
            if os.path.isdir(path):
                result = find_file(path)
                if result is not None:
                    return result
                continue
            if f == target and "dota" in path:
                return path
        except:
            pass


def load_json(url):
    return json.loads(urllib.request.urlopen(url).read().decode('utf-8'))


def load_heroes():
    """Loads in hero data to match hero number to name"""
    print('Loading heroes')
    hero_dict = {}
    hero_load = load_json(STRATZ_API + "hero")
    for i in hero_load:
        hero_dict[i] = hero_load[i]['displayName']
    return hero_dict


def id_new_game():
    """Attempts to identify the most recent actual game of dota"""
    print('IDing new game')
    global last_game
    with open(CURR_FILE) as my_file:
        curr_line = -1
        searching_game = True
        temp = list(my_file)
        while searching_game:
            curr_game = temp[curr_line]
            curr_game = curr_game[curr_game.find("(") +
                                  1:curr_game.find(")")].split()
            if "DOTA_GAMEMODE" in curr_game[2] and len(curr_game) >= 13:
                return curr_game
            else:
                curr_line -= 1


def check_shared_match(match, player1, player2):
    """ Checks a shared match and determines who won """
    """
    player1 = "84195549"
    player2 = "115392625"
    match = "3418564446"
    match = "3420967958" -- lost together example
    """
    match = load_json(STRATZ_API +
                      "/match/?matchId=" +
                      str(match) +
                      "&include=player")['results'][0]
    for i in match['players']:
        if player1 == str(i['steamId']):
            player1_won = not (match['didRadiantWin'] ^ i['isRadiant'])
        if player2 == str(i['steamId']):
            player2_won = not (match['didRadiantWin'] ^ i['isRadiant'])
    if player1_won and player2_won:
        return 0
    elif player1_won:
        return 1
    elif player2_won:
        return 2
    else:
        return 3


def check_all_shared_matches(matches, player1, player2):
    vec = [['Won with', 0],
           ['Won versus', 0],
           ['Lost versus', 0],
           ['Lost with', 0]]
    for m in matches:
        vec[check_shared_match(m, player1, player2)][1] += 1
    vec = [x for x in vec if not x[1] == 0]
    return vec


def player_processor(player_id):
    """Pulls and creates all data"""
    print('Processing player ID #' + str(player_id))
    player_dict = {'player_name': "",
                   'player_id': "",
                   'supports': 0,
                   'cores': 0,
                   'recent_mmr_avg': 0,
                   'heroes': [],
                   'lanes_played': [0, 0, 0, 0, 0],
                   'lanes_win': [0, 0, 0, 0, 0],
                   'unique_heroes': 0,
                   'recent_win_pct': 0,
                   'party_mmr': 0,
                   'solo_mmr': 0,
                   'matches': 0,
                   'avatar': "",
                   'color': "",
                   'ranked_pct': 0,
                   'activity': "",
                   'impact': "",
                   'party_pct': 0,
                   'match_count': 0,
                   'recent_match_ids': [],
                   'played_together': []
                   }
    try:
        player_dict['player_id'] = player_id
        player = load_json(STRATZ_API + "player/" + player_dict['player_id'])
        behavior = load_json(STRATZ_API +
                             "player/" +
                             player_dict['player_id'] +
                             "/behaviorChart?take=" +
                             str(RECENT_GAMES))
        matches = load_json(STRATZ_API +
                            "match/?steamid=" +
                            player_dict['player_id'] +
                            "&take=" +
                            str(RECENT_GAMES))
        try:
            player_dict['player_name'] = player['name']
            player_dict['avatar'] = player['avatar']
            player_dict['match_count'] = behavior['matchCount']
            player_dict['supports'] = to_percent(behavior['supportCount'] /
                                                 (behavior['supportCount'] +
                                                  behavior['coreCount']))
            player_dict['cores'] = 100 - player_dict['supports']
            ranks_mean = []
            for k in behavior['matches']:
                if 'rank' in k:
                    ranks_mean.append(k['rank'])
            player_dict['recent_mmr_avg'] = int(round(get_mean(ranks_mean)))
            player_dict['recent_win_pct'] = to_percent(behavior['winCount'] /
                                                       player_dict['match_count'])
            player_dict['unique_heroes'] = len(behavior['heroes'])
            player_dict['ranked_pct'] = to_percent(behavior['rankedCount'] /
                                                   player_dict['match_count'])
            player_dict['party_pct'] = to_percent(behavior['partyCount'] /
                                                  player_dict['match_count'])
            player_dict['activity'] = ACTIVITY[behavior['activity']]
            if behavior['avgImp'] >= IMPACT_UPPER:
                player_dict['impact'] = 'High'
            elif behavior['avgImp'] <= IMPACT_LOWER:
                player_dict['impact'] = 'Low'
            else:
                player_dict['impact'] = 'Medium'
            for curr_hero in behavior['heroes']:
                if curr_hero['matchCount'] >= RECENT_GAMES//12:
                    hero_name = HERO_DICT[str(curr_hero['heroId'])]
                    hero_matches = curr_hero['matchCount']
                    hero_win_pct = to_percent(curr_hero['winCount'] /
                                              hero_matches)
                    player_dict['heroes'].append([hero_name,
                                                  hero_matches,
                                                  hero_win_pct])
                curr_lane = curr_hero['lanes']
                for la in curr_lane:
                    player_dict['lanes_played'][la['lane']] += la['matchCount']
                    player_dict['lanes_win'][la['lane']] += la['winCount']
            player_dict['lanes_win'] = get_division(player_dict['lanes_win'],
                                                    player_dict['lanes_played'])
            for match in matches['results']:
                player_dict['recent_match_ids'].append(str(match['id']))
        except:
            pass
    except:
        pass
    try:
        player_dict['party_mmr'] = player['mmrDetail']['partyValue']
    except Exception as e:
        pass
    try:
        player_dict['solo_mmr'] = player['mmrDetail']['soloValue']
    except Exception as e:
        pass
    return player_dict


def game_processor():
    """ Processes game """
    print('Processing Game')
    global player_df, last_game
    curr_game = id_new_game()
    if curr_game[1] == last_game:
        return 0
    else:
        last_game = str(curr_game[1])
        del curr_game[:3]
        # Stored as strings
        player_df = [{}for x in range(10)]
        for i in range(10):
            player_df[i] = player_processor(curr_game[i][3:-1].split(":")[2])
            player_df[i]['color'] = COLORS_DOTA[i]
        for i in range(10):
            # Check shared matches
            for j in range(i + 1, 10):
                shared_matches = set(player_df[i]['recent_match_ids']) & \
                                 set(player_df[j]['recent_match_ids'])
                if len(shared_matches) > 0:
                    shared_matches = check_all_shared_matches(shared_matches,
                                                              player_df[i]['player_id'],
                                                              player_df[j]['player_id'])
                    shared_output = []
                    for stat in shared_matches:
                        shared_output.append([player_df[i]['player_name'],
                                              player_df[j]['player_name'],
                                              stat[0],
                                              stat[1]])
                    player_df[i]['played_together'].append(shared_output)
                    player_df[j]['played_together'].append(shared_output)
        html_output(player_df)


def output_player(player, p_num):
    out = "<tr>"
    for row in ROW_ORDER:
        if row == "avatar":
            # Draw pictures
            out += "<td><img src = '%s'></td>" % str(player[row])
        elif row == "player_name":
            # Colors
            out += "<td class = \"%s\" style = \"word-break: break-all;\">" \
            "<a href = https://stratz.com/player/%s class = 'button' target='_blank'>%s</a></td>" % (player['color'], player['player_id'], player['player_name'])
        elif row == "heroes":
            # Heroes
            out += "<td>"
            if len(player['heroes']) >= 1:
                hero_out = "<table>"
                hero_out += "<thead><th>Hero</th><th>#</th><th>Win</th></thead>"
                copy_data = COLORS_DOTA[p_num] + " in %s games: " % RECENT_GAMES
                for hero in player['heroes']:
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
                lane_played = to_percent(player['lanes_played'][lane] /
                                         player['match_count'])
                highlight_color_win = ""
                if player['lanes_win'][lane] >= 60:
                    highlight_color_win = 'style="color:green"'
                elif player['lanes_win'][lane] <= 40 and player['lanes_played'][lane] != 0:
                    highlight_color_win = 'style="color:red"'
                if lane_played > 25:
                    row_style = " style='font-weight:800'"
                else:
                    row_style = ""
                if lane_played > 0:
                    copy_data += LANES[lane] + ": " + \
                                 str(player['lanes_played'][lane]) + \
                                 "-" + str(player['lanes_win'][lane]) + "% "
                lane_out += "<tr %s><td>%s</td><td>%s%%</td><td %s>%s%%</td></tr>" % (row_style,
                                                                                     LANES[lane],
                                                                                     str(lane_played),
                                                                                     highlight_color_win,
                                                                                     str(player['lanes_win'][lane]))
            out += lane_out + "</table><center><button onclick=\"setClipboard('%s')\">Copy</button></center></td>" % copy_data
        elif row == "played_together":
            # Games played together
            out += "<td><table>"
            out += "<thead><th>Status</th><th>Player 2</th><th>Count</th></thead>"
            for i in range(len(player['played_together'])):
                for j in range(len(player['played_together'][i])):
                    p1_name = player['played_together'][i][j][0]
                    p2_name = player['played_together'][i][j][1]
                    result_match = player['played_together'][i][j][2]
                    result_match_number = str(player['played_together'][i][j][3])
                    if p1_name != player['player_name']:
                        temp_name = p1_name
                        p1_name = p2_name
                        p2_name = temp_name
                        if result_match == "Lost versus":
                            result_match = "Won versus"
                        elif result_match == "Won versus":
                            result_match = "Lost versus"
                    out += "<tr><td style = \"word-break: break-all;\">%s</td><td>%s</td><td>%s</td></tr>" % (result_match,
                                                                                                              p2_name,
                                                                                                              result_match_number)
            out += "</table></td>"
        else:
            str_out = player[row]
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


def html_output(player_df):
    """Outputs the data in HTML"""
    output = "<!DOCTYPE html><html>"
    output += CSS
    output += "<body><title>%s</title><h1><a href = \"http://github.com/pagchomp\" class = \"title\">%s</a></h1>" % (TOOL_TITLE, TOOL_TITLE)
    output += javascript
    table_output = "<table>"
    for i in range(10):
#        print('html output' + str(i))
        if i == 0 or i == 5:
            table_output += "</table><br><h2>%s</h2><table>" % FACTIONS[i == 5]
            table_output += "<tr>"
            for curr_col in range(len(ROW_ORDER)):
                table_output += "<td width = '%s%%'>%s</td>" % (str(COLUMN_WIDTHS[curr_col]), 
                                                                str(PROPER_NAMES_DICT[ROW_ORDER[curr_col]]))
            table_output += "</tr>"
        table_output += output_player(player_df[i], i)
    table_output += "</table>"
    mmr_data = ""
    for i in range(10):
        mmr_data += COLORS_DOTA[i] + ":" + str(player_df[i]['solo_mmr']) + " "
    output += "<center><button onclick=\"setClipboard('%s')\">Copy MMRs</button></center><br>" % mmr_data
    output += table_output
    output += "<center>Powered by<br><a href = 'http://stratz.com'><img src = \"https://stratz.com/assets/img/stratz/Stratz_Icon_Full.53650306.png\"></a></center>"
    output += "</body></html>"
    html_file = open("sigmAsTeamDetector.html", "w", encoding="utf-8")
    html_file.write(output)
    html_file.close()
    webbrowser.open("sigmAsTeamDetector.html")
    print('File created')


def main():
    """ Main """
    global DOTA_FOLDER, CURR_FILE, HERO_DICT
    DOTA_FOLDER = "C:/Program Files (x86)/Steam/steamapps/" \
                  "common/dota 2 beta/game/dota/"
    CURR_FILE = os.path.join(DOTA_FOLDER, "server_log.txt")
    # Searches for dota directory if it's not the default
    while not os.path.isfile(CURR_FILE):
        print('Default foldernot found, searching for folder. . .')
        drives = [letter + ':\\' for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ']
        for drive in drives:
            if os.path.isdir(drive):
                filepath = find_file(drive)
                if filepath is not None:
                    break
        CURR_FILE = os.path.join(filepath)
    print('File found!')
    HERO_DICT = load_heroes()
    # Checks for new games
    pub = Checker()
    if TEST:
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
