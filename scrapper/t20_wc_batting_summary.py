import requests
from bs4 import BeautifulSoup
import re
import json


def scrape_and_save(match_info):
    link = match_info["Scorecard URL"]
    response = requests.get(link)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        team_innings_elements = soup.find_all(class_='ds-text-title-xs ds-font-bold ds-text-typo')
        
        if len(team_innings_elements) >= 2:
            page_title = soup.find('title').text
            match_title = re.search(r'(\w+)\s+vs\s+(\w+)', page_title)
            
            if match_title:
                team1, team2 = match_title.groups()
            else:
                print("Team names not found in the title.")
                return None
            
            batting_tables = soup.find_all('table',
                                           class_='ds-w-full ds-table ds-table-md ds-table-auto ci-scorecard-table')
            
            if len(batting_tables) >= 2:
                batting_data = []
                
                for inning_index, batting_table in enumerate(batting_tables):
                    batting_pos = 1
                    
                    team_innings = team_innings_elements[inning_index].text.split('(')[0].strip()
                    
                    for row in batting_table.find_all('tr')[1:]:
                        cols = row.find_all('td')
                        
                        if len(cols) >= 7 and any(col.text.strip() for col in cols):
                            batting_info = {
                                "match_id": match_info["Scorecard"],
                                "match": f"{match_info['Team 1']} Vs {match_info['Team 2']}",
                                "teamInnings": team_innings,
                                "battingPos": batting_pos,
                                "batsmanName": cols[0].text.strip(),
                                "dismissal": cols[1].text.strip(),
                                "runs": cols[2].text.strip(),
                                "balls": cols[3].text.strip(),
                                "4s": cols[5].text.strip(),
                                "6s": cols[6].text.strip(),
                                "SR": cols[7].text.strip(),
                            }
                            batting_data.append(batting_info)
                            
                            batting_pos += 1
                
                return batting_data
            else:
                print("Batting tables for both innings not found on the page.")
                return None
        else:
            print("Team innings information not found on the page.")
            return None
    else:
        print(f"Failed to retrieve data from {link}.")
        return None


with open('../datasets/t20_wc_match_results.json', 'r', encoding='utf-8') as json_file:
    match_info_list = json.load(json_file)

all_batting_data = []

for index, match_info in enumerate(match_info_list, start=1):
    print(f"Scraping data for match {index}...")
    batting_data = scrape_and_save(match_info)
    
    if batting_data:
        all_batting_data.extend(batting_data)
    else:
        print(f"Skipping match {index} due to missing data.")

output_filename = '../datasets/t20_wc_batting_summary.json'
with open(output_filename, 'w', encoding='utf-8') as output_file:
    json.dump(all_batting_data, output_file, indent=4)

print(f"All data saved as {output_filename}.")
