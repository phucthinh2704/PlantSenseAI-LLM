import axios from "../config/axios";

export const apiLogin = async (data) =>
	axios({
		method: "POST",
		url: `/auth/google`,
		data,
	});