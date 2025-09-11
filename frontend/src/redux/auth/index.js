import authReducer, { loginSuccess, logout, setUser } from "./authSlice";
import { logoutUser } from "./authThunks";

export { loginSuccess, logout, setUser, logoutUser };
export default authReducer;
