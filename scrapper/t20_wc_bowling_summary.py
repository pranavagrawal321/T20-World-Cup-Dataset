import pandas as pd
import requests
from bs4 import BeautifulSoup
import json


def process_link(link, match_info):
    try:
        tables = pd.read_html(link)
        concatenated_df = pd.concat([tables[1], tables[3]])
        filtered_rows = concatenated_df[concatenated_df["M"].str.isnumeric() & concatenated_df["R"].str.isnumeric()]
        bowling_team = match_info['Team 2'] if match_info['Winner'] == match_info['Team 1'] else match_info['Team 1']
        data_list = []
        for index, row in filtered_rows.iterrows():
            data_dict = {
                "match_id": match_info["Scorecard"],
                "match": f"{match_info['Team 1']} Vs {match_info['Team 2']}",
                "bowlingTeam": bowling_team,
                "bowlerName": row["BOWLING"],
                "overs": row["O"],
                "maiden": row["M"],
                "runs": row["R"],
                "wickets": row["W"],
                "economy": row["ECON"],
                "0s": row["0s"],
                "4s": row["4s"],
                "6s": row["6s"],
                "wides": row["WD"],
                "noBalls": row["NB"]
            }
            data_list.append(data_dict)
        
        return data_list
    except Exception as e:
        print(f"Error processing link: {link}")
        print(e)
        return None


match_info_file = "../datasets/t20_wc_match_results.json"
with open(match_info_file, "r") as json_file:
    match_info_list = json.load(json_file)

all_bowling_data = []

for match_info in match_info_list:
    scorecard_url = match_info["Scorecard URL"]
    print(f"Processing match: {match_info['Team 1']} vs {match_info['Team 2']}")
    
    response = requests.get(scorecard_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        bowling_data = process_link(scorecard_url, match_info)
        
        if bowling_data:
            all_bowling_data.extend(bowling_data)
    else:
        print(f"Error accessing link: {scorecard_url}")

bowling_df = pd.DataFrame(all_bowling_data)
bowling_df.to_json("t20_wc_bowling_summary.json", orient="records")

print("Bowling data saved to t20_wc_bowling_summary.json")
