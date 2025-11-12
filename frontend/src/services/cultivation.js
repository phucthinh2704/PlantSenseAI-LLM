import axios from "@configs/axios";

export const apiGetCultivations = async () =>
	axios({
		method: "GET",
		url: `/cultivation/`,
	});

export const apiGetCultivationsByPlant = async (plantId) =>
	axios({
		method: "GET",
		url: `/cultivation/by_plant/${plantId}`,
	});

export const apiDeleteCultivation = async (techniqueId) =>
	axios({
		method: "DELETE",
		url: `/cultivation/${techniqueId}`,
	});