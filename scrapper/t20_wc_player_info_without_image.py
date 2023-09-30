import requests
from bs4 import BeautifulSoup
import json


def extract(url):
    response = requests.get(url)
    
    soup = BeautifulSoup(response.content, "html.parser")
    
    h1_element = soup.find("h1", class_="ds-text-title-l ds-font-bold")
    
    span_element = h1_element.find_next("span")
    div_element = soup.find("div")
    
    name = h1_element.text.strip()
    team = span_element.text.strip()
    
    batting_style_label = div_element.find(string="Batting Style")
    if batting_style_label:
        batting_style_span = batting_style_label.find_next("span")
        batting_style = batting_style_span.text.strip()
    else:
        batting_style = ""
    
    bowling_style_label = div_element.find(string="Bowling Style")
    
    description = soup.find("div", class_="ci-player-bio-content")
    
    if bowling_style_label:
        bowling_style_span = bowling_style_label.find_next("span")
        bowling_style = bowling_style_span.text.strip()
    else:
        bowling_style = ""
    
    playing_role_label = div_element.find(string="Playing Role")
    
    if playing_role_label:
        playing_role_span = playing_role_label.find_next("span")
        playing_role = playing_role_span.text.strip()
    else:
        playing_role = ""
    
    if description:
        description = description.text.strip()
    else:
        description = ""
    
    return {
        "name": name,
        "team": team,
        "battingStyle": batting_style.strip(),
        "bowlingStyle": bowling_style,
        "playingRole": playing_role,
        "description": description
    }


def get_players(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        class_name = "ds-min-w-max"
        
        elements = soup.find_all(class_=class_name)
        
        l = []
        
        for element in elements:
            links = element.find_all("a")
            for link in links:
                href = link.get('href')
                if href and "cricketers" in href:
                    l.append(href)
        return set(l)
    else:
        return f"Failed to fetch the webpage. Status code: {response.status_code}"


with open('../datasets/t20_wc_match_results.json', 'r') as file:
    match_data = json.load(file)

all_player_info = []

for match in match_data:
    scorecard_url = match.get("Scorecard URL")
    
    if scorecard_url:
        players_url = get_players(scorecard_url)
        for player_url in players_url:
            player_info = extract("https://www.espncricinfo.com" + player_url)
            all_player_info.append(player_info)

with open('../datasets/t20_wc_players_info.json', 'w') as file:
    json.dump(all_player_info, file, indent=4)
