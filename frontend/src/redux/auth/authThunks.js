import { createAsyncThunk } from "@reduxjs/toolkit";
import { apiLogout } from "@services/auth";
import { logout } from "./authSlice";

export const logoutUser = createAsyncThunk(
	"auth/logoutUser",
	async (_, { getState, dispatch }) => {
		try {
			const { refreshToken } = getState().auth;
			if (refreshToken) {
				await apiLogout({ refreshToken });
			}
		} catch (err) {
			console.error("Logout API failed:", err);
		} finally {
			dispatch(logout());
		}
	}
);
