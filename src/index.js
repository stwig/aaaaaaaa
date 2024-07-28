// src/index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import AppRoutes from './routes/Routes';
import App from './App';
import './index.css';

// Create a root element and render the AppRoutes
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <AppRoutes />
  </React.StrictMode>
);


// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
