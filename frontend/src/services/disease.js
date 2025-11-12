import axios from "@configs/axios";

export const apiGetDiseases = async (plant_id = null) =>
	axios({
		method: "GET",
		url: `/diseases/`,
		params: { plant_id }, // Gửi plant_id nếu có
	});

export const apiDeleteDisease = async (diseaseId) =>
	axios({
		method: "DELETE",
		url: `/diseases/${diseaseId}`,
	});

// (Thêm apiCreateDisease, apiUpdateDisease, v.v. nếu bạn cần form)