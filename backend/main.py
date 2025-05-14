from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from steam_web_api import Steam
from bs4 import BeautifulSoup
from collections import defaultdict
import requests
import re

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class SteamAPIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        #self.steam = Steam(api_key)
        self.api_url = "https://api.steampowered.com"
        self.game_url = "https://store.steampowered.com/app/"
    
    # scrapes the top sellers page and returns a list of game names
    def retrieve_top_sellers(self):
        print("Retrieving top sellers...")
        top_sellers = []
        games_per_page = 50

        # loop through 7 pages of top sellers to get roughly 200 games
        for i in range(0, 7):
            url = f"https://store.steampowered.com/search/?filter=topsellers&page={i}"
            response = requests.get(url)
            
            if (response.status_code == 200):
                soup = BeautifulSoup(response.text, 'html.parser')
                games = soup.find_all("a", class_="search_result_row")
                
                for game in games[:games_per_page]:  # Get top 50 games per page
                    game_id = game.get('data-ds-appid')
                    name = game.find("span", class_="title").text.strip()
                    img_tag = game.find("img")
                    image_url = img_tag.get('src') if img_tag else ""
                    if name == 'Steam Deck' or name == 'Valve Index® Headset': # Skip non-games
                        continue
                    top_sellers.append({"name": name, "id": game_id, "image_url": image_url})
                print(len(top_sellers))
            else:
                print(f"Failed to retrieve top sellers: {response.status_code}")
                return []
        
        return top_sellers

    # retrieves info for top sellers
    def retrieve_game_info(self, top_seller):
        url = f"{self.game_url}{top_seller['id']}"
        response = requests.get(url)
        
        if (response.status_code == 200):
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # get game rating info
            rating_element = soup.find("span", class_="nonresponsive_hidden responsive_reviewdesc")
            if rating_element:
                rating_match = re.search(r'\d+', rating_element.text.strip())
                rating = int(rating_match.group()) if rating_match else 0
            else:
                rating = 0
            top_seller['rating'] = rating


            # get game tags
            game_tags = [tag.text.strip() for tag in soup.find_all("a", class_="app_tag")]
            top_seller['tags'] = game_tags

            # get game price
            price_element = soup.find("div", class_="game_purchase_price")
            if price_element:
                price = price_element.text.strip()
                game_price = re.search(r'\d+(\.\d+)?', price)
                if game_price:
                    top_seller['price'] = float(game_price.group())
                else:
                    top_seller['price'] = 0
            else:
                top_seller['price'] = 0

            
            return top_seller
            





    


# TEST
@app.get("/")
def read_root():
    return "Hello World!"

# get top sellers from Steam
@app.get("/top-sellers")
def get_top_sellers():
    steam_api_client = SteamAPIClient("YOUR_STEAM_API_KEY_HERE")  # Replace with your actual Steam API key
    top_sellers = steam_api_client.retrieve_top_sellers()
    return {"top_sellers": top_sellers}
    
@app.get("/top-seller-info")
def get_top_seller_info():
    steam_api_client = SteamAPIClient("YOUR_STEAM_API_KEY_HERE")  # Replace with your actual Steam API key
    top_sellers = steam_api_client.retrieve_top_sellers()
    ts_info = []
    for game in top_sellers:
        ts_info.append(steam_api_client.retrieve_game_info(game))
    return {"top_sellers": ts_info}
    