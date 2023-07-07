import { createBrowserRouter } from "react-router-dom";

import Home from '../views/home'
import Query from '../views/query'
import ErrorPage from '../views/error'
const router = createBrowserRouter([
    {
      path: "/",
      element: <Home/>,
      errorElement: <ErrorPage />,
      children:[
        {
            path:"/query",
            element:<Query/>,
        }
      ],
    },
  ]);

export default router