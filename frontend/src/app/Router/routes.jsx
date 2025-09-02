import PrivateRoute from "./PrivateRoute";
import PublicRoute from "./PublicRoute";
import LoginPage from "@pages/Login";
import HomePage from "@pages/Home";
import React from "react";
import Title from "@components/Title";

const ROUTE_TYPE = {
	PUBLIC: PublicRoute,
	PRIVATE: PrivateRoute,
};

const routes = [
	{
		path: "/",
		Page: HomePage,
		type: React.Fragment,
		title: "CTU ArgiChatbot",
	},
	{
		path: "/login",
		Page: LoginPage,
		type: ROUTE_TYPE.PUBLIC, // Login mới cần PublicRoute
		title: "Đăng nhập",
	},
];

function createRoute(route) {
  const { Page, Layout, path, type: RouteType, title } = route;
  const WrappedLayout = Layout || React.Fragment;

  return {
    path,
    element: (
      <RouteType>
        <Title>{title}</Title>
        <WrappedLayout>
          <Page />
        </WrappedLayout>
      </RouteType>
    ),
  };
}

const appRoutes = routes.map(createRoute);
export default appRoutes;
