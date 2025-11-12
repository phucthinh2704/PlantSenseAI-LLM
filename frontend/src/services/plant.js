import axios from "@configs/axios";

// Dựa trên app/router/plant_router.py
export const apiGetPlants = async () =>
	axios({
		method: "GET",
		url: `/plants/`,
	});

export const apiGetPlantById = async (plantId) =>
	axios({
		method: "GET",
		url: `/plants/${plantId}`,
	});

export const apiCreatePlant = async (data) =>
	axios({
		method: "POST",
		url: `/plants/`,
		data,
	});

export const apiUpdatePlant = async (plantId, data) =>
	axios({
		method: "PUT",
		url: `/plants/${plantId}`,
		data,
	});

export const apiDeletePlant = async (plantId) =>
	axios({
		method: "DELETE",
		url: `/plants/${plantId}`,
	});