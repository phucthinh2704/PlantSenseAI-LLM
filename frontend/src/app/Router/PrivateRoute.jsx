import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const PrivateRoute = ({ children }) => {
	const user = localStorage.getItem("access_token");
	const navigate = useNavigate();

	useEffect(() => {
		if (!user) {
			toast.info("Bạn cần đăng nhập để vào hệ thống!", {
				autoClose: 2000,
			});
			navigate("/login", { replace: true });
		}
	}, [user, navigate]);

	if (!user) return null; // Không render gì khi chưa đăng nhập

	return children;
};

export default PrivateRoute;
