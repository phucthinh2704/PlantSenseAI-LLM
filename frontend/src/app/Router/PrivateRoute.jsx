import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";

const PrivateRoute = ({ children }) => {
	const { accessToken } = useSelector((state) => state.auth);
	const navigate = useNavigate();

	useEffect(() => {
		if (!accessToken) {
			toast.info("Bạn cần đăng nhập để vào hệ thống!", {
				autoClose: 2000,
			});
			navigate("/login", { replace: true });
		}
	}, [accessToken, navigate]);

	if (!accessToken) return null; // Không render gì khi chưa đăng nhập

	return children;
};

export default PrivateRoute;
