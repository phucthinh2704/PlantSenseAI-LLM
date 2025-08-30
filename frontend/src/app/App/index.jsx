import React, { Fragment } from "react";
import Router from "@app/Router";
import { ToastContainer } from "react-toastify";
import "./index.css"
function App() {
    window.global = window;
    return (
        <Fragment>
            <Router></Router>
            <ToastContainer></ToastContainer>
        </Fragment>
    )

}
export default App