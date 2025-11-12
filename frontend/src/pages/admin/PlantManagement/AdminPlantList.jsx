import useAlert from "@hooks/useAlert";
import { apiDeletePlant, apiGetPlants } from "@services/plant";
import { Edit, Plus, Trash2 } from "lucide-react";
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

const AdminPlantList = () => {
	const [plants, setPlants] = useState([]);
	const [loading, setLoading] = useState(true);
	const { showConfirm, showSuccess, showError } = useAlert();

	const fetchPlants = async () => {
		setLoading(true);
		try {
			const res = await apiGetPlants();
			if (res.success) {
				setPlants(res.data);
			} else {
				showError("Không thể tải danh sách giống cây.");
			}
		} catch (err) {
			console.error(err);
			showError("Lỗi máy chủ khi tải giống cây.");
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		fetchPlants();
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, []);

	const handleDelete = (plantId, plantName) => {
		showConfirm(
			`Xác nhận xóa "${plantName}"?`,
			"Hành động này sẽ xóa cây khỏi MongoDB. Bạn sẽ cần chạy lại 'Full Re-index' để xóa khỏi Qdrant."
		).then(async (result) => {
			if (result.isConfirmed) {
				try {
					await apiDeletePlant(plantId);
					showSuccess("Đã xóa giống cây thành công.");
					fetchPlants(); // Tải lại danh sách
				} catch (err) {
					console.error(err);
					showError("Xóa thất bại. Vui lòng thử lại.");
				}
			}
		});
	};

	if (loading) {
		return <div>Đang tải dữ liệu...</div>;
	}

	return (
		<div>
			<div className="flex justify-between items-center mb-6">
				<h1 className="text-3xl font-bold text-gray-800">
					Quản lý Giống cây ({plants.length})
				</h1>
				<Link
					to="/admin/plants/new"
					className="bg-green-600 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2 hover:bg-green-700 transition-colors">
					<Plus size={18} />
					<span>Thêm mới</span>
				</Link>
			</div>

			{/* Bảng dữ liệu */}
			<div className="bg-white shadow-md rounded-lg overflow-hidden">
				<table className="min-w-full divide-y divide-gray-200">
					<thead className="bg-gray-50">
						<tr>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Tên Giống
							</th>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Loại cây
							</th>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Nguồn gốc
							</th>
							<th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
								Hành động
							</th>
						</tr>
					</thead>
					<tbody className="bg-white divide-y divide-gray-200">
						{plants.map((plant) => (
							<tr key={plant._id}>
								<td className="px-6 py-4 whitespace-nowrap">
									<div className="text-sm font-medium text-gray-900">
										{plant.name}
									</div>
								</td>
								<td className="px-6 py-4 whitespace-nowrap">
									<span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
										{plant.category}
									</span>
								</td>
								<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 truncate max-w-xs">
									{plant.origin}
								</td>
								<td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
									<Link
										to={`/admin/plants/edit/${plant._id}`}
										className="text-indigo-600 hover:text-indigo-900"
										title="Sửa">
										<Edit
											size={18}
											className="inline-block"
										/>
									</Link>
									<button
										onClick={() =>
											handleDelete(plant._id, plant.name)
										}
										className="text-red-600 hover:text-red-900"
										title="Xóa">
										<Trash2
											size={18}
											className="inline-block"
										/>
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

export default AdminPlantList;
