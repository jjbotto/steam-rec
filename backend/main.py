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
        max_pages = 5
        self.unowned_game_library = []
        seen_games = set()

        # loop through max pages of top sellers to get roughly 200 games
        for i in range(1, max_pages):
            url = f"https://store.steampowered.com/search/?filter=topsellers&page={i}"
            response = requests.get(url)
            
            if (response.status_code == 200):
                soup = BeautifulSoup(response.text, 'html.parser')
                games = soup.find_all("a", class_="search_result_row")
                
                for game in games:  
                    game_id = game.get('data-ds-appid')
                    if game_id in seen_games:
                        continue
                    name = game.find("span", class_="title").text.strip()
                    img_tag = game.find("img")
                    image_url = img_tag.get('src') if img_tag else ""
                    if name == 'Steam Deck' or name == 'Valve Index® Headset': # Skip non-games
                        continue
                    new_game = {"name": name, "id": game_id, "image_url": image_url}
                    new_game_info = self.retrieve_ts_info(new_game)
                    self.unowned_game_library.append(new_game_info)
                    seen_games.add(game_id)

                print(len(self.unowned_game_library))
                time.sleep(0.2)
            else:
                print(f"Failed to retrieve top sellers: {response.status_code}")
                return []
        
        print("Finished retrieving top sellers.")
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

            time.sleep(0.3)
            return top_seller

    # returns a list of user owned games
    def retrieve_user_info(self, user_id):
        print("Retrieving user info...")
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
        print("Total user playtime: ", self.total_user_playtime)
        print("Total user genre count: ", self.total_user_genre_count)
        user_owned_ids = {str(game['id']) for game in self.user_game_library}
        print("User owned game count: ", len(user_owned_ids))
        print("Unowned game count: ", len(self.unowned_game_library))
        recommendations = []

        for game in self.unowned_game_library:
            if str(game['id']) in user_owned_ids:
                print("Skipping owned game: ", game['name'])
                continue
            game_rank = 0

            for tag in game['tags']:
                if tag in self.playtime_per_genre:
                    game_rank += ((float(self.playtime_per_genre[tag]) / self.total_user_playtime) * (float(self.single_genre_count[tag]) / self.total_user_genre_count))
            game['rank'] = game_rank
            recommendations.append(game)
            print(game)
        
        recommendations.sort(key=lambda x: x['rank'], reverse=True)
        return recommendations


@app.get("/recommendations")
def get_recommendations(steam_id: str):
    steam_api_client = SteamAPIClient(steam_api_key)
    steam_api_client.retrieve_top_sellers()
    steam_api_client.retrieve_user_info(steam_id)
    steam_api_client.count_user_genres()
    raw_recommendations = steam_api_client.rank_unowned_games()
    recommendations = []
    for game in raw_recommendations:
        recommendations.append({
            "id": game['id'],
            "name": game['name'],
            "rating": game['rating'],
            "price": game['price'],
            "image_url": game['image_url'],
            "genres": game['tags'],
        })
    return {"recommendations": recommendations}
