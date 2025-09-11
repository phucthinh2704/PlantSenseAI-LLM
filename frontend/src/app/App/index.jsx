import Router from "@app/Router";
import React, { Fragment } from "react";
import { HelmetProvider } from "react-helmet-async";
import { ToastContainer } from "react-toastify";
import { PersistGate } from "redux-persist/integration/react";
import { Provider } from "react-redux";
import "./index.css";
import { persistor, store } from "@redux/store";
function App() {
	window.global = window;
	return (
		<Fragment>
		<Provider store={store}>
			<PersistGate
				loading={null}
				persistor={persistor}>
			<HelmetProvider>
				<Router />
			</HelmetProvider>
			</PersistGate>
		</Provider>
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
