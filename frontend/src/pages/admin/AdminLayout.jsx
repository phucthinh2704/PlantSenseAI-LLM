import React from "react";
import { useSelector } from "react-redux";
import { NavLink, Outlet } from "react-router-dom";
import {
	BarChart,
	Bot,
	Bug,
	ChevronRight,
	Database,
	Home,
	Leaf,
	MessageSquare,
	Sprout,
	Users,
} from "lucide-react";

// eslint-disable-next-line no-unused-vars
const AdminNavLink = ({ to, icon: Icon, children }) => (
	<NavLink
		to={to}
		end
		className={({ isActive }) =>
			`flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium transition-colors ${
				isActive
					? "bg-gray-900 text-white"
					: "text-gray-300 hover:bg-gray-700 hover:text-white"
			}`
		}>
		<div className="flex items-center space-x-3">
			<Icon size={18} />
			<span>{children}</span>
		</div>
		<ChevronRight size={16} />
	</NavLink>
);

const AdminLayout = () => {
	const { user } = useSelector((state) => state.auth);

	return (
		<div className="flex h-screen bg-gray-100">
			{/* Admin Sidebar */}
			<aside className="w-64 flex-shrink-0 bg-gray-800 text-white flex flex-col">
				<div className="h-16 flex-shrink-0 px-4 flex items-center justify-between border-b border-gray-700">
					<div className="flex items-center space-x-2">
						<Bot className="text-green-400" />
						<span className="font-semibold text-lg">
							AgriBot Admin
						</span>
					</div>
				</div>
				<div className="flex-1 overflow-y-auto p-4 space-y-2">
					<AdminNavLink
						to="/admin"
						icon={Home}>
						Dashboard
					</AdminNavLink>

					<p className="text-xs text-gray-400 uppercase pt-4 pb-1 px-3">
						Quản lý Tri thức
					</p>
					<AdminNavLink
						to="/admin/plants"
						icon={Sprout}>
						Giống cây
					</AdminNavLink>
					<AdminNavLink
						to="/admin/diseases"
						icon={Bug}>
						Bệnh hại
					</AdminNavLink>
					<AdminNavLink
						to="/admin/cultivation"
						icon={Leaf}>
						Kỹ thuật Canh tác
					</AdminNavLink>

					<p className="text-xs text-gray-400 uppercase pt-4 pb-1 px-3">
						Hệ thống
					</p>
					<AdminNavLink
						to="/admin/conversations"
						icon={MessageSquare}>
						Lịch sử Hội thoại
					</AdminNavLink>
					<AdminNavLink
						to="/admin/users"
						icon={Users}>
						Người dùng
					</AdminNavLink>
					<AdminNavLink
						to="/admin/indexing"
						icon={Database}>
						Đồng bộ hóa (Index)
					</AdminNavLink>
				</div>
				<div className="p-4 border-t border-gray-700">
					<p className="text-sm text-gray-300">Đã đăng nhập với</p>
					<p className="font-medium truncate">{user?.email}</p>
				</div>
			</aside>

			{/* Main Content */}
			<main className="flex-1 overflow-y-auto">
				<div className="p-8">
					{/* Outlet sẽ render trang con (Dashboard, PlantList, v.v.) */}
					<Outlet />
				</div>
			</main>
		</div>
	);
};

export default AdminLayout;
