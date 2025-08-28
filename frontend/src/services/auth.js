import axios from "@configs/axios";

export const apiLogin = async (data) =>
	axios({
		method: "POST",
		url: `/auth/google`,
		data,
	});