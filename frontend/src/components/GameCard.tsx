import { Properties } from 'csstype';
import { Game } from '../types';

type GameCardProps = Omit<Game, 'id'>;

const styles: Record<string, Properties> = {
  gameCard: {
    backgroundColor: '#fff',
    borderRadius: '8px',
    padding: '1rem',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    textAlign: 'center',
    transition: 'transform 0.2s',
    cursor: 'pointer',
  },
  gameImage: {
    width: '100%',
    height: '200px',
    objectFit: 'cover',
    borderRadius: '4px',
    marginBottom: '1rem',
  },
  gameTitle: {
    fontSize: '1.2rem',
    fontWeight: 'bold',
    margin: '0.5rem 0',
  },
  gameRating: {
    color: '#666',
    margin: '0.5rem 0',
  },
  gamePrice: {
    color: '#2ecc71',
    fontWeight: 'bold',
    margin: '0.5rem 0',
  },
  gameGenres: {
    color: '#3498db',
    margin: '0.5rem 0',
  },
};

export default function GameCard({ name, rating, price, image_url, genres }: GameCardProps) {
    return (
        <div style={styles.gameCard}>
            <img 
                src={image_url} 
                alt={name} 
                style={styles.gameImage}
            />
            <h2 style={styles.gameTitle}>{name}</h2>
            <p style={styles.gameRating}>Rating: {rating}</p>
            <p style={styles.gamePrice}>Price: ${price}</p>
            <p style={styles.gameGenres}>Genres: {genres.join(', ')}</p>
        </div>
    );
}
