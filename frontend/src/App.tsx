import { useState } from 'react'
import SearchBar from './components/SearchBar';
import GameGrid from './components/GameGrid';
import { Game } from './types';

export default function App() {
  const [steamID, setSteamID] = useState("");
  const [recommendations, setRecommendations] = useState<Game[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isNewSearch, setIsNewSearch] = useState(true);
  
  const getRecommendations = async (steamID: string) => {
    setIsLoading(true);
    setIsNewSearch(false);
    try {
      const response = await fetch(`http://127.0.0.1:8000/recommendations?steam_id=${steamID}`);
      if (!response.ok) {
        throw new Error('Failed to retrieve recommendations');
      }
      const data = await response.json();
      setRecommendations(data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations: ', error);
    }
    setIsLoading(false);
  };
  
  return (
    <div className="flex flex-col min-h-screen min-w-screen">
      <div className={`bg-black flex flex-col items-center transition-all duration-500 min-w-screen
                      ${isNewSearch ? "justify-center flex-1" : "justify-start mt-0"}`}>
        <SearchBar
          steamID={steamID}
          onSteamIDChange={setSteamID}
          onGetRecommendations={() => getRecommendations(steamID)}
        />
      </div>
      {recommendations.length > 0 && (
      <div>
        <GameGrid games={recommendations} />
      </div>
      )}
    </div>
  );
}

