
import GameCard from './GameCard';
import { Game } from '../types';

type GameGridProps = {
    games: Game[];
}

// Add styles
const styles = {
  gameGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))',
    gap: '2rem',
    padding: '1rem',
    maxWidth: '1200px',
    margin: '0 auto',
  }
};

export default function GameGrid({ games }: GameGridProps) {
    return (
        <div className="grid grid-cols-2 gap-10 p-10">
            {games.map((game) => (
                <GameCard
                    key={game.id}
                    name={game.name}
                    rating={game.rating}
                    price={game.price}
                    image_url={game.image_url}
                />
            ))}
        </div>
    );
}