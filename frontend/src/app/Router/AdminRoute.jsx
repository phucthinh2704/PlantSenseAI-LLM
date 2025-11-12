import React from "react";
import { useSelector } from "react-redux";
import { Navigate, useLocation } from "react-router-dom";
import LoadingPage from "@components/LoadingPage"; // Giả sử bạn có component này

const AdminRoute = ({ children }) => {
	const { user } = useSelector((state) => state.auth);
	const location = useLocation();

	// if (isLoading) {
	//   return <LoadingPage />;
	// }

	// Nếu đã login VÀ là admin, cho phép truy cập
	if (user && user.role === "admin") {
		return children;
	}

	// Nếu đã login nhưng KHÔNG PHẢI admin, đá về trang chủ
	if (user && user.role !== "admin") {
		return <Navigate to="/" state={{ from: location }} replace />;
	}

	// Nếu chưa login, đá về trang đăng nhập
	return <Navigate to="/login" state={{ from: location }} replace />;
};

export default AdminRoute;