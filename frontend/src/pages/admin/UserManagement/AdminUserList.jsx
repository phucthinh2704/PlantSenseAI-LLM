import React, { useEffect, useState, useCallback } from "react";
import {
	apiGetAllUsers,
	apiDeleteUser,
	apiUpdateUserRole,
	apiUpdateUserStatus,
} from "@services/user";
import useAlert from "@hooks/useAlert";
import {
	Trash2,
	UserCheck,
	UserX,
	Shield,
	User as UserIcon,
} from "lucide-react";
import { useSelector } from "react-redux";
import AvatarDefault from "@components/AvatarDefault"; // Import component Avatar
import { formatDistanceToNow, parseISO } from "date-fns";
import { vi } from "date-fns/locale";

const AdminUserList = () => {
	const [users, setUsers] = useState([]);
	const [loading, setLoading] = useState(true);
	const { showConfirm, showSuccess, showError } = useAlert();
	const currentUser = useSelector((state) => state.auth.user); // Lấy admin hiện tại từ Redux

	const fetchUsers = useCallback(async () => {
		setLoading(true);
		try {
			const res = await apiGetAllUsers();
			if (res.success) {
				setUsers(res.data);
			} else {
				showError("Không thể tải danh sách người dùng.");
			}
		} catch (err) {
			console.error(err);
			showError("Lỗi máy chủ khi tải danh sách người dùng.");
		} finally {
			setLoading(false);
		}
	}, [showError]);

	useEffect(() => {
		fetchUsers();
	}, [fetchUsers]); // Sử dụng fetchUsers làm dependency

	const formatTimestamp = (isoString) => {
		try {
			const dateUTC = parseISO(isoString);
			return formatDistanceToNow(dateUTC, { addSuffix: true, locale: vi });
		} catch (e) {
      console.error("Lỗi parse ngày:", isoString, e);
			return "Không rõ";
		}
	};

	const handleDelete = (userId, userName) => {
		if (userId === currentUser?.id) {
			showError("Bạn không thể tự xóa chính mình!");
			return;
		}
		showConfirm(
			`Xác nhận xóa "${userName}"?`,
			"Hành động này sẽ xóa vĩnh viễn người dùng và tất cả các cuộc hội thoại của họ."
		).then(async (result) => {
			if (result.isConfirmed) {
				try {
					await apiDeleteUser(userId);
					showSuccess("Đã xóa người dùng thành công.");
					fetchUsers(); // Tải lại danh sách
				} catch (err) {
					console.error(err);
					showError("Xóa thất bại. Vui lòng thử lại.");
				}
			}
		});
	};

	const handleRoleChange = (userId, userName, newRole) => {
		showConfirm(
			`Thay đổi vai trò?`,
			`Bạn có chắc muốn đổi "${userName}" thành ${
				newRole === "admin" ? "Quản trị viên" : "Người dùng"
			}?`
		).then(async (result) => {
			if (result.isConfirmed) {
				try {
					await apiUpdateUserRole(userId, newRole);
					showSuccess("Cập nhật vai trò thành công.");
					fetchUsers();
				} catch (err) {
          console.error(err);
					showError("Cập nhật vai trò thất bại.");
				}
			}
		});
	};

	const handleStatusChange = (userId, userName, newStatus) => {
		const statusText =
			newStatus === "active"
				? "Kích hoạt"
				: newStatus === "banned"
				? "Cấm"
				: "Vô hiệu hóa";
		showConfirm(
			`Thay đổi trạng thái?`,
			`Bạn có chắc muốn "${statusText}" tài khoản "${userName}"?`
		).then(async (result) => {
			if (result.isConfirmed) {
				try {
					await apiUpdateUserStatus(userId, newStatus);
					showSuccess("Cập nhật trạng thái thành công.");
					fetchUsers();
				} catch (err) {
          console.error(err);
					showError("Cập nhật trạng thái thất bại.");
				}
			}
		});
	};

	if (loading) {
		return <div>Đang tải dữ liệu người dùng...</div>;
	}

	return (
		<div>
			<h1 className="text-3xl font-bold text-gray-800 mb-6">
				Quản lý Người dùng ({users.length})
			</h1>

			<div className="bg-white shadow-md rounded-lg overflow-hidden">
				<table className="min-w-full divide-y divide-gray-200">
					<thead className="bg-gray-50">
						<tr>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Người dùng
							</th>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Vai trò
							</th>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Trạng thái
							</th>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Ngày tham gia
							</th>
							<th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
								Hành động
							</th>
						</tr>
					</thead>
					<tbody className="bg-white divide-y divide-gray-200">
						{users.map((user) => (
							<tr key={user.id}>
								<td className="px-6 py-4 whitespace-nowrap">
									<div className="flex items-center">
										<div className="flex-shrink-0 h-10 w-10">
											{user.avatar ? (
												<img
													className="h-10 w-10 rounded-full object-cover"
													src={user.avatar}
													alt={user.name}
												/>
											) : (
												<AvatarDefault name={user.name} />
											)}
										</div>
										<div className="ml-4">
											<div className="text-sm font-medium text-gray-900">
												{user.name}
											</div>
											<div className="text-sm text-gray-500">
												{user.email}
											</div>
										</div>
									</div>
								</td>
								<td className="px-6 py-4 whitespace-nowrap">
									{user.role === "admin" ? (
										<span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
											Admin
										</span>
									) : (
										<span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
											User
										</span>
									)}
								</td>
								<td className="px-6 py-4 whitespace-nowrap">
									{user.status === "active" && (
										<span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
											Active
										</span>
									)}
									{user.status === "inactive" && (
										<span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
											Inactive
										</span>
									)}
									{user.status === "banned" && (
										<span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
											Banned
										</span>
									)}
								</td>
								<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{formatTimestamp(user.created_at)}
								</td>
								<td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
									{/* Nút Role */}
									{user.role === "user" ? (
										<button
											onClick={() =>
												handleRoleChange(
													user.id,
													user.name,
													"admin"
												)
											}
											className="text-gray-500 hover:text-red-600"
											title="Nâng lên Admin">
											<Shield size={18} className="inline-block" />
										</button>
									) : (
										<button
											onClick={() =>
												handleRoleChange(
													user.id,
													user.name,
													"user"
												)
											}
											className="text-red-600 hover:text-gray-500"
											title="Hạ xuống User">
											<UserIcon size={18} className="inline-block" />
										</button>
									)}

									{/* Nút Status */}
									{user.status === "active" ? (
										<button
											onClick={() =>
												handleStatusChange(
													user.id,
													user.name,
													"banned"
												)
											}
											className="text-gray-500 hover:text-red-600"
											title="Cấm (Ban) tài khoản">
											<UserX size={18} className="inline-block" />
										</button>
									) : (
										<button
											onClick={() =>
												handleStatusChange(
													user.id,
													user.name,
													"active"
												)
											}
											className="text-gray-500 hover:text-green-600"
											title="Kích hoạt tài khoản">
											<UserCheck size={18} className="inline-block" />
										</button>
									)}

									{/* Nút Xóa */}
									<button
										onClick={() => handleDelete(user.id, user.name)}
										className="text-red-600 hover:text-red-900"
										title="Xóa vĩnh viễn"
										disabled={user.id === currentUser?.id} // Không cho tự xóa
									>
										<Trash2 size={18} className="inline-block" />
									</button>
								</td>
							</tr>
						))}
					</tbody>
				</table>
			</div>
		</div>
	);
};

export default AdminUserList;