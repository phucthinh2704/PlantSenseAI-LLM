import PrivateRoute from "./PrivateRoute";
import PublicRoute from "./PublicRoute";
import LoginPage from "@pages/Login";
import HomePage from "@pages/Home";
import React from 'react';

const ROUTE_TYPE = {
    PUBLIC: PublicRoute,
    PRIVATE: PrivateRoute
}

const routes = [
    {
        path: "/",
        Page: HomePage,
        // Layout: ,
        type: ROUTE_TYPE.PUBLIC,
        title: "CTU ArgiChatbot"
    },
    {
        path: "/login",
        Page: LoginPage,
        type: ROUTE_TYPE.PUBLIC,
        title: "Đăng nhập"
    },
]

function createRoute(route) {
    const { Page, Layout, title, path, type } = route;
    const WrappedLayout = Layout || React.Fragment;

    return {
        path,
        type,
        title,
        element: (
            <WrappedLayout>
                <Page />
            </WrappedLayout>
        )
    };
}

const appRoutes = routes.map(createRoute);
export default appRoutes;