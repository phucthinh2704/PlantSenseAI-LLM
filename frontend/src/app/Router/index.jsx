import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import routes from "./routes";
function Router() {
	return (
		<BrowserRouter
			future={{
				v7_startTransition: true,
				v7_relativeSlatPath: true,
				v7_relativeSplatPath: true,
			}}>
			<Routes>
				{routes.map(({ path, element }) => (
					<Route
						key={path}
						path={path}
						element={element}
					/>
				))}
			</Routes>
		</BrowserRouter>
	);
}

export default Router;
