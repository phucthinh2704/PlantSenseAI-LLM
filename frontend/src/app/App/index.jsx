import Router from "@app/Router";
import React, { Fragment } from "react";
import { HelmetProvider } from "react-helmet-async";
import { ToastContainer } from "react-toastify";
import "./index.css";
function App() {
	window.global = window;
	return (
		<Fragment>
			<HelmetProvider>
				<Router />
			</HelmetProvider>
			<ToastContainer />
		</Fragment>
	);
}
export default App;
