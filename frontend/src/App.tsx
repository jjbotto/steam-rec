import { useState } from 'react'
import GameCard from './components/GameCard';

export default function App() {
  const [steamID, setSteamID] = useState("");
  const [recommendations, setRecommendations] = useState([]);
  
  return (
    <div style={{ padding: "1rem" }}>
      <h1>The Steam Recommender</h1>
      <input
        type="text"
        placeholder="Enter your Steam User ID"
        value={steamID}
        onChange={(e) => setSteamID(e.target.value)}
      />
      <button onClick={() => {}}>Get Recommendations</button>
    </div>
  );
}

