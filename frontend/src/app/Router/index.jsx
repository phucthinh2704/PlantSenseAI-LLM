import React from "react";
import { Route, BrowserRouter, Routes } from "react-router-dom";
import routes from "./routes";
import Title from "@components/Title";
function Router() {
	return (
		<BrowserRouter
			future={{
				v7_startTransition: true,
				v7_relativeSlatPath: true,
				v7_relativeSplatPath: true,
			}}>
			<Routes>
				{routes.map((route) => {
					const { path, element, title } = route;
					const RouteType = route.type;

					return (
						<Route
							key={path}
							path={path}
							element={
								<RouteType>
									<Title>{title}</Title>
									{element}
								</RouteType>
							}></Route>
					);
				})}
			</Routes>
		</BrowserRouter>
	);
}

export default Router;
