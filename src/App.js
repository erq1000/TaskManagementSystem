import React from 'react';
import ReactDOM from 'react-dom';
import AppHeader from './components/AppHeader';
import MainContent from './components/MainContent';
import Footer from './components/Footer';

function App() {
    return (
        <div className="app-container">
            <AppHeader />
            <MainContent />
            <Footer />
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));