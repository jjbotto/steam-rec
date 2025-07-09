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
    try {
      const response = await fetch(`http://127.0.0.1:8000/recommendations?steam_id=${steamID}`);
      if (!response.ok) {
        throw new Error('Failed to retrieve recommendations');
      }
      const data = await response.json();
      setIsNewSearch(false);
      setRecommendations(data.recommendations);
    } catch (error) {
      console.error('Error fetching recommendations: ', error);
    }
    setIsLoading(false);
  };
  
  return (
    <div>
      <SearchBar
        steamID={steamID}
        onSteamIDChange={setSteamID}
        onGetRecommendations={() => getRecommendations(steamID)}
        isCentered={isNewSearch}
      />
      <GameGrid games={recommendations} />
    </div>
  );
}

