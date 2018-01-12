# -*- coding: utf-8 -*-

"""
This script downloads data from the stratz api and uses it to create a
dashboard for teammates/enemies in a game of Dota 2
Created on Fri Aug  4 11:30:35 2017

@author: Brett Burk
"""
import os
import time
import webbrowser
import requests

"""
TODO:
    Copy button for summary stats
    Make a class for individual heroes/radiant/dire
    Java version?
"""

"""
My player id (kept for testing)
player_id = "84195549"
player_id = "115392625"
match_id = "3418564446"
"""

TOOL_TITLE = "sigmA's Team Detector 1.4"
TEST = False
#TEST = True

RECENT_GAMES = 100
STRATZ_API = "https://api.stratz.com/api/v1/"
COLORS_DOTA = ["Blue", "Teal", "Purple", "Yellow", "Orange",
               "Pink", "Grey", "LightBlue", "Green", "Brown"]
LANES = ["Roaming", "Safe Lane", "Mid", "Offlane", "Jungle"]
ACTIVITY = ["None", "Very Low", "Low", "Medium",
            "High", "Very High", "Intense"]
ROW_ORDER = ['player_name', 'avatar', 'recent_win_pct', 'solo_medal',
             'matches', 'ranked_pct', 'activity', 'impact', 'party_pct',
             'supports', 'unique_heroes', 'heroes', 'lanes_played',
             'played_together']
IMPACT_UPPER = 109
IMPACT_LOWER = 91
COLUMN_WIDTHS = [10, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 14, 14, 14]
FACTIONS = ['RADIANT', 'DIRE']
MEDALS = ['Herald', 'Guardian', 'Crusader', 'Archon', 'Legend', 'Ancient',
          'Divine']
PROPER_NAMES_DICT = {'player_name': "Player Name",
                     'supports': "Support",
                     'cores': "Core",
                     'heroes': "Heroes",
                     'lanes_played': "Lanes",
                     'unique_heroes': "Unique Heroes",
                     'recent_win_pct': "Recent Win %",
                     'solo_medal': "Solo Medal",
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
    font-size: 32px;
    font-weight: 700;
    line-height: 32px;
    margin: 0 0 0;
    padding: 20px 30px;
    text-align: center;
    text-shadow: 0 1px 0 #ccc,
             0 2px 0 #c9c9c9,
             0 3px 0 #bbb,
             0 4px 0 #b9b9b9,
             0 5px 0 #aaa,
             0 6px 1px rgba(0,0,0,.1),
             0 0 5px rgba(0,0,0,.1),
             0 1px 3px rgba(0,0,0,.3),
             0 3px 5px rgba(0,0,0,.2),
             0 5px 10px rgba(0,0,0,.25),
             0 10px 10px rgba(0,0,0,.2),
             0 20px 20px rgba(0,0,0,.15);
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
    vertical-align: middle;
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
    text-decoration: none;
    font: bold 12px Arial;
    white-space: normal;
    display: block;
    background-color: #EEEEEE;
    padding-left: .25rem;
    padding-right: .25rem;
    margin-right: .25rem;
    color: black;
    border-width: 0;
    max-width: 10rem;
    min-height: 1rem;
    vertical-align: top;
    font-weight: bold;
    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19);
}

.hide-scroll {
    overflow: hidden;
}

.viewport {
    overflow: auto;
    height: 500px;
    margin-right: -16px;
}
</style>"""

JAVASCRIPT = """<script>
function setClipboard(value) {
    var tempInput = document.createElement("input");
    tempInput.style = "position: absolute; left: -1000px; top: -1000px";
    tempInput.value = value;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand("copy");
    document.body.removeChild(tempInput);
};
</script>"""

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
        except Exception as e:
            pass


def load_json(url):
    return requests.get(url, headers={'Connection': 'close'}).json()


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
    if TEST:
        print('Processing player ID #' + str(player_id))
    player_dict = {'player_name': "",
                   'player_id': "",
                   'supports': 0,
                   'cores': 0,
                   'heroes': [],
                   'lanes_played': [0, 0, 0, 0, 0],
                   'lanes_win': [0, 0, 0, 0, 0],
                   'unique_heroes': 0,
                   'recent_win_pct': 0,
                   'solo_medal': 0,
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
        matches = load_json(STRATZ_API + "player/" + player_dict['player_id'] +
                            "/matches?take=" + str(RECENT_GAMES))
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
            player_dict['matches'] = matches['total']
            for match in matches['results']:
                player_dict['recent_match_ids'].append(str(match['id']))
        except:
            pass
    except:
        pass
    try:
        player_dict['solo_medal'] = player['rankDetail']['rank']
    except Exception as e:
        pass
    return player_dict


def game_processor():
    """ Processes game """
    global player_df, last_game
    curr_game = id_new_game()
    if curr_game[1] == last_game:
        print('Game already processed')
        return 0
    else:
        last_game = str(curr_game[1])
        del curr_game[:3]
        # Stored as strings
        player_df = [{}for x in range(10)]
        curr_game = [x[3:-1].split(":")[2] for x in curr_game]
        if TEST:
            start = time.time()
        for i in range(10):
            player_df[i] = player_processor(curr_game[i])
            player_df[i]['color'] = COLORS_DOTA[i]
        end = time.time()
        if TEST:
            print('API Call Time ' + str(end - start))
            start = time.time()
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
        if TEST:
            end = time.time()
            print('Check if Previous Teammates ' + str(end - start))
        html_output(player_df)

def output_player(player, p_num):
    out = "<tr>"
    for row in ROW_ORDER:
        if row == "avatar":
            # Draw pictures
            out += "<td width = '{}%'><img src = '{}'></td>".format(str([COLUMN_WIDTHS[i] for i, x in enumerate(ROW_ORDER) if x == "avatar"][0]),
                                 str(player[row]))
        elif row == "player_name":
            # Colors
            out += "<td width = '{}%' class = \"{}\" style = \"word-break: break-all;\">" \
            "<a href = https://stratz.com/player/{} class = 'button' target='_blank'>{}</a></td>".format(str([COLUMN_WIDTHS[i] for i, x in enumerate(ROW_ORDER) if x == "player_name"][0]),
                                                 player['color'], 
                                                 player['player_id'], 
                                                 player['player_name'])
        elif row == "heroes":
            # Heroes
            out += "<td width = '{}%'>".format(str([COLUMN_WIDTHS[i] for i, x in enumerate(ROW_ORDER) if x == "heroes"][0]))
            if len(player['heroes']) >= 1:
                hero_out = "<table>"
                hero_out += "<thead><th>Hero</th><th>#</th><th>Win</th></thead>"
                copy_data = COLORS_DOTA[p_num] + " in {} games: ".format(RECENT_GAMES)
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
                    hero_out += "</td><td {}>{}%".format(highlight_color, str(hero[2]))
                    copy_data += str(hero[2]) + "% "
                    hero_out += "</td><tr>"
                hero_out += "</table><center><button onclick=\"setClipboard('{}')\">Copy</button></center></td>".format(copy_data)
                out += hero_out
            else:
                out += "</td>"
        elif row == "lanes_played":
            # Lanes data
            copy_data = COLORS_DOTA[p_num] + " in {} games: ".format(RECENT_GAMES)
            lane_out = "<td width = '{}%'><table>".format(str([COLUMN_WIDTHS[i] for i, x in enumerate(ROW_ORDER) if x == "lanes_played"][0]))
            lane_out += "<thead><th>Lane</th><th>Play</th><th>Win</th></thead>"
            for lane in range(5):
                if player['match_count'] == 0:
                    lane_out += "<tr></tr>"
                else:
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
                    lane_out += "<tr {}><td>{}</td><td>{}%</td><td {}>{}%</td></tr>".format(row_style,
                                                                                         LANES[lane],
                                                                                         str(lane_played),
                                                                                         highlight_color_win,
                                                                                         str(player['lanes_win'][lane]))
            out += lane_out + "</table><center><button onclick=\"setClipboard('{}')\">Copy</button></center></td>".format(copy_data)
        elif row == "played_together":
            # Games played together
            out += "<td width = '{}%'><table>".format(str([COLUMN_WIDTHS[i] for i, x in enumerate(ROW_ORDER) if x == "played_together"][0]))
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
                    out += "<tr><td style = \"word-break: break-all;\">{}</td><td>{}</td><td>{}</td></tr>".format(result_match,
                                                                                                              p2_name,
                                                                                                              result_match_number)
            out += "</table></td>"
        elif row == "solo_medal":
            if player[row] >= 10:
                str_out = MEDALS[int(str(player[row])[0])-1] + ' {}'.format(str(player[row])[1])
                out += "<td width = '{}%'>{}</td>".format(str(COLUMN_WIDTHS[1]), str(str_out))
            else:
                out += "<td width = '{}%'></td>".format(str(COLUMN_WIDTHS[1]))
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
            out += "<td width = '{}%' {}>{}</td>".format(str(COLUMN_WIDTHS[1]), highlight_color, str(str_out))
    out += "</tr>"
    return out


def summarize_team(player_df):
    """ I should probably make a class and make radiant and dire as well as player just instances of that class """
    radiant = {"recent_win_avg" : 0,
        "solo_medal_avg" : 0,
        "total_matches_avg" : 0,
        "ranked_matches_avg" : 0,
        "activity_level_avg" : 0,
        "impact_level_avg" : 0,
        "party_percent_avg" : 0,
        "support_avg" : 0,
        "core_avg" : 0,
        "unique_heroes" : 0
    }
    dire = {"recent_win_avg" : 0,
        "solo_medal_avg" : 0,
        "total_matches_avg" : 0,
        "ranked_matches_avg" : 0,
        "activity_level_avg" : 0,
        "impact_level_avg" : 0,
        "party_percent_avg" : 0,
        "support_avg" : 0,
        "core_avg" : 0,
        "unique_heroes" : 0
    }
    for faction in [radiant, dire]:
        faction_success = 0
        if faction == radiant:
            c = 0
        else:
            c = 5
        for i in range(c + 0, c + 5):
            try:
                faction['recent_win_avg'] += player_df[i]['recent_win_pct']
#                faction['solo_medal_avg'] += player_df[i]['solo_medal']
                # Thank you python for having to do it this way btw its 10/5 = 2
                faction['solo_medal_avg'] += int(float(str(player_df[i]['solo_medal'])[0] + str(int(str(player_df[i]['solo_medal'])[1]) * 2)))
                faction['total_matches_avg'] += player_df[i]['matches']
                faction['ranked_matches_avg'] += player_df[i]['ranked_pct']
                faction['activity_level_avg'] += [j for j, k in enumerate(ACTIVITY) if k == player_df[i]['activity']][0]
                faction['impact_level_avg'] += [j for j, k in enumerate(['Low', 'Medium', 'High']) if k == player_df[i]['impact']][0]
                faction['party_percent_avg'] += player_df[i]['party_pct']
                faction['support_avg'] += player_df[i]['supports']
                faction['core_avg'] += player_df[i]['cores']
                faction['unique_heroes'] += player_df[i]['unique_heroes']
                faction_success += 1
            except:
                print('no value for ' + str(i))
        if faction_success > 0:
            for k, v in faction.items():
                faction[k] = round(v / faction_success, 2)
            faction['activity_level_avg'] = ACTIVITY[int(round(faction['activity_level_avg'], 0))]
            faction['impact_level_avg'] = ['Low', 'Medium', 'High'][int(round(faction['impact_level_avg'], 0))]
            # 5/10 = 1/2
            faction['solo_medal_avg'] = MEDALS[int(str(faction['solo_medal_avg'])[0])-1] + ' {}'.format(int(float(str(faction['solo_medal_avg'])[1:]) * 1/2))
    return [radiant, dire]


def html_output(player_df):
    """Outputs the data in HTML"""
    output = "<!DOCTYPE html><html><meta charset='UTF-8'> "
    output += CSS
    output += "<body><title>{}</title><h1><a href = \"http://github.com/pagchomp\" class = \"title\">{}</a></h1>".format(TOOL_TITLE, TOOL_TITLE)
    output += JAVASCRIPT
    table_output = ""
    radiant, dire = summarize_team(player_df)
    for i in range(10):
        if i == 0 or i == 5:
            if i == 0:
                table_output += "<h2>{}</h2><table>".format(FACTIONS[0])
                table_output += "<tr>"
            else:
                table_output += "</table><table></table><br><h2>{}</h2><table>".format(FACTIONS[1])
                table_output += "<tr>"
            for curr_col in range(len(ROW_ORDER)):
                table_output += "<th width = '{}%'>{}</th>".format(str(COLUMN_WIDTHS[curr_col]),
                                                                str(PROPER_NAMES_DICT[ROW_ORDER[curr_col]]))
            table_output += "</tr></table><div class = \"hide-scroll\">" + \
                            "<div class = \"viewport\"><table>"
        table_output += output_player(player_df[i], i)
        if i == 4 or i == 9:
            if i == 4:
                faction = radiant
            else:
                faction = dire
            faction_outputs = [str(faction["recent_win_avg"]) + "%",
                               faction["solo_medal_avg"],
                               faction["total_matches_avg"],
                               str(faction["ranked_matches_avg"]) + "%",
                               faction["activity_level_avg"],
                               faction["impact_level_avg"],
                               str(faction["party_percent_avg"]) + "%",
                               str(faction["support_avg"]) + "%",
                               faction["unique_heroes"]]
            table_output += "</table></div></div><table><tr><td width = '{}%' align='center'><b>TEAM AVERAGES:</b></td><td width = '{}%' align='center'></td>".format(COLUMN_WIDTHS[0],
                                                                         COLUMN_WIDTHS[1])
            for j, k in enumerate(faction_outputs):
                table_output += "<td width = '{}%' align='center'>{}</td>".format(str(COLUMN_WIDTHS[j + 2]), k)
            table_output += ("<td width =' {}%' align='center'></td>".format(str(COLUMN_WIDTHS[len(COLUMN_WIDTHS) - 1])) * 3)
            table_output += "</tr>"
    table_output += "</table>"
    mmr_data = ""
    for i in range(10):
        mmr_data += COLORS_DOTA[i] + ":" + str(player_df[i]['solo_medal']) + " "
    output += "<center><button onclick=\"setClipboard('{}')\">Copy MMRs</button></center>".format(mmr_data)
    output += table_output
    output += "</div></div><center>Powered by<br><a href = 'http://stratz.com'>" + \
              "<img src = \"https://stratz.com/assets/img/stratz/Stratz_Icon_Full.53650306.png\">" + \
              "</a></center>"
    output += "</body></html>"
    html_file = open("sigmAsTeamDetector.html", "w", encoding="utf8")
    html_file.write(output)
    html_file.close()
    webbrowser.open("sigmAsTeamDetector.html")
#    print(output)
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
                print('Error Parsing Game: {}'.format(str(e)))
                time.sleep(2)
                main()


if __name__ == "__main__":
    main()
