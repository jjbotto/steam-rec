from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
from collections import defaultdict
import requests
import re
from dotenv import load_dotenv
import os
import time

load_dotenv()
steam_api_key = os.getenv("STEAM_API_KEY")

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
        self.api_url = "https://api.steampowered.com"
        self.game_url = "https://store.steampowered.com/app/"
        self.total_user_genre_count = 0
        self.total_user_playtime = 0
        self.playtime_per_genre = defaultdict(int)
        self.single_genre_count = defaultdict(int)
        self.user_game_library = []
        self.unowned_game_library = []
    
    # scrapes the top sellers page and returns a list of games
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
                    new_game = {"name": name, "id": game_id, "image_url": image_url}
                    new_game = self.retrieve_ts_info(new_game)
                    self.unowned_game_library.append(new_game)

                print(len(self.unowned_game_library))
                time.sleep(0.5)
            else:
                print(f"Failed to retrieve top sellers: {response.status_code}")
                return []
        
        return self.unowned_game_library

    # returns list of genre tags for a game
    def retrieve_game_tags(self, game_id):
        url = f"{self.game_url}{game_id}"
        response = requests.get(url)
        
        tags = []
        if (response.status_code == 200):
            soup = BeautifulSoup(response.text, 'html.parser')
            tags = [tag.text.strip() for tag in soup.find_all("a", class_="app_tag")]
            time.sleep(0.1)
            return tags
        else:
            return []

    # returns ratings, tags, and price info for a single top seller
    def retrieve_ts_info(self, top_seller):
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
                rating = 70
            top_seller['rating'] = rating

            # get game genre tags
            game_tags = self.retrieve_game_tags(top_seller['id'])
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

            time.sleep(0.5)
            return top_seller

    # returns a list of user owned games
    def retrieve_user_info(self, user_id):
        url = f"{self.api_url}/IPlayerService/GetOwnedGames/v0001/"
        params = {
            "key": self.api_key,
            "steamid": user_id,
            "include_played_free_games": 1,
            "include_appinfo": 1,
        }
        response = requests.get(url, params=params)
       
        user_owned_games = []
        if response.status_code == 200:
            data = response.json().get("response", {})
            games = data.get("games", [])
            for game in games:
                self.total_user_playtime += game["playtime_forever"] / 60
                user_owned_games.append({"name": game["name"], "id": game["appid"], "playtime": game["playtime_forever"] / 60, "tags": self.retrieve_game_tags(game["appid"])}) if game["playtime_forever"] > 0 else None
            
            self.user_game_library = user_owned_games
            return user_owned_games
        else:
            return None

    # counts user genres and genre playtime
    def count_user_genres(self):
        for game in self.user_game_library:
            for tag in game['tags']:
                self.total_user_genre_count += 1
                self.playtime_per_genre[tag] += game['playtime']
                self.single_genre_count[tag] += 1

    # ranks unowned games in order of recommendation
    def rank_unowned_games(self):
        for game in self.unowned_game_library:
            if game['id'] in self.user_game_library:
                continue
            game_rank = 0
            for tag in game['tags']:
                if tag in self.playtime_per_genre:
                    game_rank += ((self.playtime_per_genre[tag] / self.total_user_playtime) * (self.single_genre_count[tag] / self.total_user_genre_count))
                else:
                    continue

            game_rank += (game['rating'] / 1000)
            game['rank'] = game_rank
        
        self.unowned_game_library.sort(key=lambda x: x['rank'], reverse=True)
        return self.unowned_game_library

           
                



    


# TEST
@app.get("/")
def read_root():
    return "Hello World!"

# get top sellers from Steam
@app.get("/top-sellers")
def get_top_sellers():
    steam_api_client = SteamAPIClient(steam_api_key)
    top_sellers = steam_api_client.retrieve_top_sellers()
    return {"top_sellers": top_sellers}
    
@app.get("/user-owned-games")
def get_user_info():
    steam_api_client = SteamAPIClient(steam_api_key)
    user_info = steam_api_client.retrieve_user_info("76561198059049117")
    return {"user_info": user_info}
    

@app.get("/recommendations")
def get_recommendations():
    steam_api_client = SteamAPIClient(steam_api_key)
    steam_api_client.retrieve_top_sellers()
    steam_api_client.retrieve_user_info("76561198059049117")
    recommendations = steam_api_client.rank_unowned_games()
    return {"recommendations": recommendations}
