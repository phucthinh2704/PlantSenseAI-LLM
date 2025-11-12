import React, { useState } from "react";
import { apiRunIncrementalIndex, apiRunFullReindex } from "@services/admin";
import useAlert from "@hooks/useAlert";
import { Database, RefreshCcw, AlertTriangle } from "lucide-react";

const AdminIndexing = () => {
	const [isLoading, setIsLoading] = useState(false);
	const [isFullLoading, setIsFullLoading] = useState(false);
	const { showConfirm, showSuccess, showError } = useAlert();

	const handleIncrementalIndex = async () => {
		showConfirm(
			"Chạy đồng bộ hóa tăng cường?",
			"Hệ thống sẽ quét các tài liệu mới hoặc được cập nhật từ MongoDB và thư mục /documents. Quá trình này có thể mất vài phút."
		).then(async (result) => {
			if(result.isConfirmed) {
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
			}
		});
	};

	const handleFullReindex = () => {
		showConfirm(
			"XÂY DỰNG LẠI TOÀN BỘ?",
			"HÀNH ĐỘNG NGUY HIỂM: Thao tác này sẽ XÓA SẠCH collection vector và chunk lại TOÀN BỘ dữ liệu. Sẽ mất rất nhiều thời gian. Bạn có chắc chắn?"
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
			<h1 className="text-3xl font-bold text-gray-800 mb-4">
				Đồng bộ hóa Dữ liệu (Indexing)
			</h1>
			<p className="text-lg text-gray-600 mb-8">
				Quản lý "bộ não" của Chatbot. Chạy đồng bộ hóa khi bạn cập nhật kiến thức.
			</p>

			<div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
				<h2 className="text-xl font-semibold mb-4 flex items-center">
					<Database className="mr-2 text-blue-600" />
					Cập nhật Vector Database (Qdrant)
				</h2>
				<p className="text-gray-600 mb-6">
					Chạy "Đồng bộ hóa Tăng cường" sau khi bạn thêm hoặc sửa cây, bệnh, v.v. để cập nhật kiến thức cho bot.
					Chỉ chạy "Xây dựng lại Toàn bộ" khi bạn xóa dữ liệu hoặc khi có lỗi nghiêm trọng.
				</p>
				
				<div className="space-y-4">
					<button
						onClick={handleIncrementalIndex}
						disabled={isLoading || isFullLoading}
						className="w-full bg-blue-600 text-white font-medium py-3 px-5 rounded-lg flex items-center justify-center space-x-2 hover:bg-blue-700 transition-colors disabled:bg-gray-400">
						<RefreshCcw size={18} className={isLoading ? "animate-spin" : ""} />
						<span>
							{isLoading ? "Đang đồng bộ..." : "Đồng bộ hóa Tăng cường (Chế độ mặc định)"}
						</span>
					</button>

					<button
						onClick={handleFullReindex}
						disabled={isLoading || isFullLoading}
						className="w-full bg-red-600 text-white font-medium py-3 px-5 rounded-lg flex items-center justify-center space-x-2 hover:bg-red-700 transition-colors disabled:bg-gray-400">
						<AlertTriangle size={18} />
						<span>
							{isFullLoading ? "Đang xây dựng lại..." : "Xây dựng lại Toàn bộ (Full Re-index)"}
						</span>
					</button>
				</div>
			</div>
		</div>
	);
};

export default AdminIndexing;