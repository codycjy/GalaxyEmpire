import { createBrowserRouter } from "react-router-dom";

import Home from '../views/home'
import Query from '../views/query'
const router = createBrowserRouter([
    {
      path: "/",
      element: <Home/>,
      children:[
        {
            path:"/query",
            element:<Query/>
        }
      ],
    },
  ]);

export default router