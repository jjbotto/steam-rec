import React from 'react';
import GameCard from './GameCard';

export interface Game {
    id: number;
    name: string;
    rating: number;
    price: number;
    image_url: string;
    genres: string[];
}

type GameGridProps = {
    games: Game[];
}

export default function GameGrid({ games }: GameGridProps) {
    return (
        <div className="game-grid">
            {games.map((game) => (
                <GameCard
                    key={game.id}
                    name={game.name}
                    rating={game.rating}
                    price={game.price}
                    image_url={game.image_url}
                    genres={game.genres}
                />
            ))}
        </div>
    );
}