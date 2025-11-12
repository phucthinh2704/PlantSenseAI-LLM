import React from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import appRoutes from "./routes";

const router = createBrowserRouter(appRoutes);
function Router() {
	return (
		<RouterProvider
			future={{
				v7_startTransition: true,
			}}
			router={router}
		/>
	);
	// return (
	// 	<BrowserRouter
	// 		future={{
	// 			v7_startTransition: true,
	// 			v7_relativeSlatPath: true,
	// 			v7_relativeSplatPath: true,
	// 		}}>
	// 		<Routes>
	// 			{routes.map(({ path, element }) => (
	// 				<Route
	// 					key={path}
	// 					path={path}
	// 					element={element}
	// 				/>
	// 			))}
	// 		</Routes>
	// 	</BrowserRouter>
	// );
}

export default Router;
