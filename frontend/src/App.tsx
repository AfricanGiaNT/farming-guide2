import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Home from './pages/Home';
import Weather from './pages/Weather';
import Crops from './pages/Crops';
import Varieties from './pages/Varieties';
import Search from './pages/Search';
import AdminVarieties from './pages/AdminVarieties';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/weather" element={<Weather />} />
          <Route path="/crops" element={<Crops />} />
          <Route path="/varieties" element={<Varieties />} />
          <Route path="/search" element={<Search />} />
          <Route path="/admin/varieties" element={<AdminVarieties />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
