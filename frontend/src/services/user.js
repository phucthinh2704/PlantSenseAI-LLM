import axios from "@configs/axios";

// (Admin) Lấy tất cả user
export const apiGetAllUsers = async () =>
	axios({
		method: "GET",
		url: `/users/`,
	});

// (Admin) Cập nhật vai trò
export const apiUpdateUserRole = async (userId, role) =>
	axios({
		method: "PUT",
		url: `/users/${userId}/role`,
		data: { role }, // { "role": "admin" }
	});

// (Admin) Cập nhật trạng thái
export const apiUpdateUserStatus = async (userId, status) =>
	axios({
		method: "PUT",
		url: `/users/${userId}/status`,
		data: { status }, // { "status": "banned" }
	});

// (Admin) Xóa user
export const apiDeleteUser = async (userId) =>
	axios({
		method: "DELETE",
		url: `/users/${userId}`,
	});