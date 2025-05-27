import React from 'react'

type GameCardProps = {
    name: string,
    rating: number, 
    price: number,
    image_url: string,
    genres: string[]
}

export default function GameCard({ name, rating, price, image_url, genres }: GameCardProps) {
    return (
        <div className="game-card">
            <h2 className="game-title">{name}</h2>
            <img src={image_url} alt={name} className="game-image" />
            <p className="game-rating">Rating: {rating}</p>
            <p className="game-price">Price: ${price}</p>
            <p className="game-genres">Genres: {genres.join(', ')}</p>
        </div>
    );
}
