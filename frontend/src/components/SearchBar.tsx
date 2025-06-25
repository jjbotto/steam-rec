import React from 'react';

type SearchBarProps = {
    steamID: string;
    onSteamIDChange: (steamID: string) => void;
    onGetRecommendations: () => void;
    isCentered: boolean;
};

export default function SearchBar({ steamID, onSteamIDChange, onGetRecommendations, isCentered }: SearchBarProps) {
    const searchBarClass = isCentered ? "search-bar centered" : "search-bar moved-up";

    return (
        <div style={{ padding: "1rem" }} className={searchBarClass}>
            <h1>The Steam Recommender</h1>
            <input
                type="text"
                placeholder="Enter your Steam User ID"
                value={steamID}
                onChange={(e) => onSteamIDChange(e.target.value)}
            />
            <button onClick={onGetRecommendations}>Get Recommendations</button>
        </div>
    );
}