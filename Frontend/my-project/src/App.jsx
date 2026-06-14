import {Routes, Route} from 'react-router-dom';
import {React, useEffect, useState} from 'react';
import Home from './pages/home.jsx';

function App(){

  const [user, setUser] = useState(null);

  useEffect(() => {
    fetch("http://localhost:5000/api/user")
      .then((res) => res.json())
      .then((data) => setUser(data));
  }, []);//fetching the backend api

  return (
    <Routes>
      <Route path="/" element={<Home />} />// Define other routes here
    </Routes>
  ); 
};

export default App;