import React, { useState } from "react";
import { apiRunIncrementalIndex, apiRunFullReindex } from "@services/admin";
import useAlert from "@hooks/useAlert";
import { Database, RefreshCcw, AlertTriangle } from "lucide-react";

const AdminDashboard = () => {
	const [isLoading, setIsLoading] = useState(false);
	const [isFullLoading, setIsFullLoading] = useState(false);
	const { showConfirm, showSuccess, showError } = useAlert();

	const handleIncrementalIndex = async () => {
		setIsLoading(true);
		try {
			await apiRunIncrementalIndex();
			showSuccess("Đồng bộ hóa tăng cường hoàn tất!");
		} catch (err) {
			console.error("Lỗi khi index tăng cường:", err);
			showError("Đồng bộ hóa thất bại. Vui lòng kiểm tra log server.");
		} finally {
			setIsLoading(false);
		}
	};

	const handleFullReindex = () => {
		showConfirm(
			"Xây dựng lại toàn bộ?",
			"Hành động này sẽ XÓA SẠCH và chunk lại toàn bộ dữ liệu. Sẽ mất rất nhiều thời gian. Bạn có chắc chắn?"
		).then(async (result) => {
			if (result.isConfirmed) {
				setIsFullLoading(true);
				try {
					await apiRunFullReindex();
					showSuccess(
						"Xây dựng lại toàn bộ hoàn tất!"
					);
				} catch (err) {
					console.error("Lỗi khi full re-index:", err);
					showError("Xây dựng lại thất bại. Vui lòng kiểm tra log server.");
				} finally {
					setIsFullLoading(false);
				}
			}
		});
	};

	return (
		<div>
			<h1 className="text-3xl font-bold text-gray-800 mb-6">
				Dashboard Quản trị
			</h1>

			<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
				{/* Thống kê (Bạn có thể thêm sau) */}
				<div className="bg-white p-6 rounded-lg shadow">
					<h2 className="text-xl font-semibold mb-4">Thống kê...</h2>
					{/* ... Thêm biểu đồ ... */}
				</div>
				
				{/* Quản lý Index */}
				<div className="bg-white p-6 rounded-lg shadow">
					<h2 className="text-xl font-semibold mb-4 flex items-center">
						<Database className="mr-2 text-blue-600" />
						Quản lý Dữ liệu Vector (Index)
					</h2>
					<p className="text-gray-600 mb-4">
						Chạy đồng bộ hóa sau khi bạn thêm/sửa/xóa dữ liệu trong MongoDB hoặc thư mục `documents`.
					</p>
					
					<button
						onClick={handleIncrementalIndex}
						disabled={isLoading || isFullLoading}
						className="w-full bg-blue-600 text-white font-medium py-3 px-5 rounded-lg flex items-center justify-center space-x-2 hover:bg-blue-700 transition-colors disabled:bg-gray-400">
						<RefreshCcw size={18} className={isLoading ? "animate-spin" : ""} />
						<span>
							{isLoading ? "Đang đồng bộ..." : "Đồng bộ hóa Tăng cường (Chạy ngay)"}
						</span>
					</button>

					<button
						onClick={handleFullReindex}
						disabled={isLoading || isFullLoading}
						className="w-full bg-red-600 text-white font-medium py-3 px-5 rounded-lg flex items-center justify-center space-x-2 hover:bg-red-700 transition-colors disabled:bg-gray-400 mt-4">
						<AlertTriangle size={18} />
						<span>
							{isFullLoading ? "Đang xây dựng lại..." : "Xây dựng lại Toàn bộ (Chạy lại từ đầu)"}
						</span>
					</button>
				</div>
			</div>
		</div>
	);
};

export default AdminDashboard;