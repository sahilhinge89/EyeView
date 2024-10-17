import React from 'react';
import { BrowserRouter as Router, Route, Switch, Redirect } from 'react-router-dom';
import './App.css';
import Login from './components/Login';
import SignUp from './components/SignUp';
import NavBar from './components/NavBar';
import HeroSection from './components/HeroSection';
import MainContent from './components/MainContent';

function App() {
  const isAuthenticated = !!localStorage.getItem('token');

  return (
    <Router>
      <div className="app">
        <NavBar />
        <Switch>
          <Route path="/login" component={Login} />
          <Route path="/signup" component={SignUp} />
          <Route path="/video_feed">
            {isAuthenticated ? <HeroSection /> : <Redirect to="/login" />}
          </Route>
          <Route path="/" exact component={MainContent} />
          <Redirect to="/" />
        </Switch>
      </div>
    </Router>
  );
}

export default App;