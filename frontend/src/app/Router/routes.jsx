import PrivateRoute from "./PrivateRoute";
import PublicRoute from "./PublicRoute";
import LoginPage from "@pages/Login";
import React from 'react';

const ROUTE_TYPE = {
    PUBLIC: PublicRoute,
    PRIVATE: PrivateRoute
}

const routes = [
    {
        path: "/login",
        Page: LoginPage,
        type: ROUTE_TYPE.PUBLIC,
        title: "Đăng nhập"
    },
    {
        path: "/login",
        Page: LoginPage,
        // Layout: ,
        type: ROUTE_TYPE.PUBLIC,
        title: "CTU ArgiChatbot"
    },
]

export default routes.map((route) => {
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
});