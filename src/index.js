import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
const API_ENDPOINT = process.env.REACT_APP_API_ENDPOINT;
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <App apiEndpoint={API_ENDPOINT} />
    </React.StrictMode>
);