import { Game } from '../types';

type GameCardProps = Omit<Game, 'id' | 'genres'>;

export default function GameCard({ name, rating, price, image_url }: GameCardProps) {
    return (
        <div className="flex flex-col items-center gap-2 bg-blue-950/80 rounded-xl pt-5 pb-5 border-white border-2 font-mono hover:scale-110 transition-all duration-500 ease-in-out">
            <img 
                className="rounded-xl w-3/4"
                src={image_url} 
                alt={name} 
            />
            <h2 className="text-white text-2xl font-bold">{name}</h2>
            <p className="text-blue-800">Price: ${price}</p>
            <p className="text-gray-500">Rating: {rating}</p>
        </div>
    );
}
