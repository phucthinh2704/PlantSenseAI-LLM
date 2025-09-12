import axios from "@configs/axios";

export const apiLogin = async (data) =>
	axios({
		method: "POST",
		url: `/auth/login`,
		data,
	});
export const apiGoogleLogin = async (data) =>
	axios({
		method: "POST",
		url: `/auth/google`,
		data,
	});
export const apiLogout = async (data) =>
	axios({
		method: "POST",
		url: `/auth/logout`,
		data,
	});
