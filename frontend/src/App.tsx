import './App.css'
import React, { useEffect, useState } from 'react';

function App() {

  // useeffect for fetching data from the API

  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(import.meta.env.VITE_API_URL);
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    fetchData();
  }, []);


  return (
    <>
      <h1>Medic Agent</h1>
      <p>Welcome to the Medic Agent application!</p>
      {
        data ? (
          <div>
            <h2>Data from API:</h2>
            <pre>{JSON.stringify(data, null, 2)}</pre>
          </div>
        ) : (
          <p>Loading data...</p>
        )
      }
    </>
  )
}

export default App
