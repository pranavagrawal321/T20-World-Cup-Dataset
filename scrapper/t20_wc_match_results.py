import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.espncricinfo.com/records/tournament/team-match-results/icc-men-s-t20-world-cup-2022-23-14450"

response = requests.get(url)

df = pd.read_html(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table',
                      class_="ds-w-full ds-table ds-table-xs ds-table-auto ds-w-full ds-overflow-scroll ds-scrollbar-hide")
    
    if table:
        l = []
        for cell in table.find_all('td', class_="ds-min-w-max ds-text-right"):
            link = cell.find('a')
            if link:
                link_text = link.get_text(strip=True)
                link_url = link.get('href')
                if "/series" in link_url:
                    l.append("https://www.espncricinfo.com/" + link_url)
        
        df = pd.DataFrame(df[0])
        ans = pd.concat([df, pd.DataFrame({"Scorecard URL": l})], axis=1)
        
        ans.to_json("t20_wc_match_results.json", orient="records")
        print("Data written to 't20_wc_match_results.json'")
    else:
        print("Table not found on the webpage.")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
