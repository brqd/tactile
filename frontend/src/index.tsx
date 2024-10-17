import * as React from "react";
import * as ReactDOM from "react-dom/client";
import "./index.css";
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import MiniDrawer from "./layouts/miniDrawer"
import ErrorPage from "./error-page";
import reportWebVitals from './reportWebVitals';
import LoremIpsum from "./pages/lorem-ipsum";
import { MenuStateProvider } from "./layouts/menuState"

const router = createBrowserRouter([
  {
    path: "/",
    element: <MiniDrawer />,
    errorElement: <ErrorPage />,
    children: [
      {
        path: "lorem",
        element: <LoremIpsum />,
      },
    ],    
  },
]);


ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <MenuStateProvider>
      <RouterProvider router={router} />
    </MenuStateProvider>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();


