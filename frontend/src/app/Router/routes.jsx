import PrivateRoute from "./PrivateRoute";
import PublicRoute from "./PublicRoute";
import LoginPage from "@pages/Login";
import AdminRoute from "./AdminRoute";
import HomePage from "@pages/Home";
import React from "react";
import Title from "@components/Title";
import AdminLayout from "@pages/admin/AdminLayout";
import AdminDashboard from "@pages/admin/AdminDashboard";
import AdminPlantList from "@pages/admin/PlantManagement/AdminPlantList";
import AdminPlantForm from "@pages/admin/PlantManagement/AdminPlantForm";
import AdminDiseaseList from "@pages/admin/DiseaseManagement/AdminDiseaseList";
import AdminCultivationList from "@pages/admin/CultivationManagement/AdminCultivationList";
import AdminConversationList from "@pages/admin/ConversationManagement/AdminConversationList";
import AdminIndexing from "@pages/admin/Indexing/AdminIndexing";
import AdminUserList from "@pages/admin/UserManagement/AdminUserList";


const ROUTE_TYPE = {
	PUBLIC: PublicRoute,
	PRIVATE: PrivateRoute,
	ADMIN: AdminRoute,
};
function createRoute(route) {
	const { Page, Layout, path, type: RouteType, title } = route;
	const WrappedLayout = Layout || React.Fragment;

	return {
		path,
		element: (
			<RouteType>
				<Title>{title}</Title>
				<WrappedLayout>
					<Page />
				</WrappedLayout>
			</RouteType>
		),
	};
}

// --- ĐỊNH NGHĨA ROUTE ---
const routes = [
	// Route Người dùng
	{
		path: "/",
		Page: HomePage,
		type: ROUTE_TYPE.PRIVATE,
		title: "CTU ArgiChatbot",
	},
	{
		path: "/login",
		Page: LoginPage,
		type: ROUTE_TYPE.PUBLIC,
		title: "Đăng nhập",
	},

	// === BẮT ĐẦU ROUTE ADMIN (Định nghĩa kiểu lồng nhau) ===
	{
		path: "/admin",
		element: (
			<ROUTE_TYPE.ADMIN>
				<AdminLayout />
			</ROUTE_TYPE.ADMIN>
		),
		children: [
			{
				index: true, // Trang /admin
				element: (
					<>
						<Title>Dashboard</Title>
						<AdminDashboard />
					</>
				),
			},
			{
				path: "plants", // /admin/plants
				element: (
					<>
						<Title>Quản lý Giống cây</Title>
						<AdminPlantList />
					</>
				),
			},
			{
				path: "plants/new", // /admin/plants/new
				element: (
					<>
						<Title>Thêm Giống cây</Title>
						<AdminPlantForm />
					</>
				),
			},
			{
				path: "plants/edit/:plantId", // /admin/plants/edit/123
				element: (
					<>
						<Title>Sửa Giống cây</Title>
						<AdminPlantForm />
					</>
				),
			},
			{
				path: "diseases", // /admin/diseases
				element: (
					<>
						<Title>Quản lý Bệnh hại</Title>
						<AdminDiseaseList />
					</>
				),
			},
			{
				path: "cultivation", // /admin/cultivation
				element: (
					<>
						<Title>Quản lý Kỹ thuật Canh tác</Title>
						<AdminCultivationList />
					</>
				),
			},
			{
				path: "conversations", // /admin/conversations
				element: (
					<>
						<Title>Lịch sử Hội thoại</Title>
						<AdminConversationList />
					</>
				),
			},
			{
				path: "indexing", // /admin/indexing
				element: (
					<>
						<Title>Đồng bộ hóa (Index)</Title>
						<AdminIndexing />
					</>
				),
			},
			{
				path: "users", // Sẽ khớp với /admin/users
				element: (
					<>
						<Title>Quản lý Người dùng</Title>
						<AdminUserList />
					</>
				),
			},
		],
	},
];

// --- TÁI CẤU TRÚC LOGIC XUẤT ---
const adminRoutes = routes
	.filter((r) => r.path.startsWith("/admin"))
	.map((r) => ({
		path: r.path,
		element: r.element,
		children: r.children,
	}));

const simpleRoutes = routes
	.filter((r) => !r.path.startsWith("/admin"))
	.map(createRoute);

const appRoutes = [...simpleRoutes, ...adminRoutes];

export default appRoutes;
