import React from "react";
import { Navigate } from "react-router-dom";

const PublicRoute = ({ children }) => {
	const user = localStorage.getItem("access_token");

	if (user) {
		return (
			<Navigate
				to="/"
				replace
			/>
		);
	}

	return children;
};

export default PublicRoute;
