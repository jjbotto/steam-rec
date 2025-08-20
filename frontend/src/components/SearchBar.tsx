

type SearchBarProps = {
    steamID: string;
    onSteamIDChange: (steamID: string) => void;
    onGetRecommendations: () => void;
};

export default function SearchBar({ steamID, onSteamIDChange, onGetRecommendations }: SearchBarProps) {

    return (
        <div style={{ padding: "1rem" }} className="flex flex-col items-center min-w-screen gap-5 font-mono">
            <h1 className="text-4xl font-bold text-white">The Steam Recommender</h1>
            <input
                className="min-w-1/2 min-h-10 rounded-xl border-white border-2 p-2 text-white"
                type="text"
                placeholder="Enter your Steam User ID"
                value={steamID}
                onChange={(e) => onSteamIDChange(e.target.value)}
            />
            <button className="bg-gray-800 hover:bg-blue-900 rounded-xl border-white border-2 p-2 text-white shadow-md shadow-gray-500" onClick={onGetRecommendations}>Get Recommendations</button>
        </div>
    );
}