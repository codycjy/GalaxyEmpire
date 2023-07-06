import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import Layout from './views/home.jsx'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import router from './router/index.jsx';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
