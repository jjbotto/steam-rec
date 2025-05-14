import React, { useEffect, useState } from 'react';

const App: React.FC = () => {
  const [message, setMessage] = useState<string>('Loading...');

  useEffect(() => {
    fetch('http://localhost:8000/')
      .then((res) => res.json())
      .then((data) => setMessage(data))
      .catch((err) => {
        console.error('Error fetching from backend:', err);
        setMessage('Error fetching message');
      });
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h1>Message from Backend:</h1>
      <p>{message}</p>
    </div>
  );
};

export default App;
