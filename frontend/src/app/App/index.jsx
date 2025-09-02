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
			<ToastContainer
				position="top-right"
				autoClose={3000}
				hideProgressBar={false}
				newestOnTop={false}
				closeOnClick
				rtl={false}
				pauseOnFocusLoss
				draggable
				pauseOnHover
				theme="light"
			/>
		</Fragment>
	);
}
export default App;
