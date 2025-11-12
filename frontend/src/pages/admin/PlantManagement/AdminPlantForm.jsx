import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
	apiGetPlantById,
	apiCreatePlant,
	apiUpdatePlant,
} from "@services/plant";
import useAlert from "@hooks/useAlert";
import { Save, ArrowLeft, Plus, Trash2 } from "lucide-react";

// Dữ liệu trống ban đầu
const initialState = {
	name: "",
	origin: "",
	plant_type: "",
	category: "",
	growth_duration: "",
	morphology: "",
	yields: "",
	description: "",
	image_url: "",
	sources: [{ name: "", url: "" }],
};

const AdminPlantForm = () => {
	const { plantId } = useParams();
	const navigate = useNavigate();
	const isEditMode = Boolean(plantId);
	const [plant, setPlant] = useState(initialState);
	const [loading, setLoading] = useState(false);
	const { showSuccess, showError } = useAlert();

	useEffect(() => {
		if (isEditMode) {
			setLoading(true);
			apiGetPlantById(plantId)
				.then((res) => {
					if (res.success) {
						// Đảm bảo sources không bao giờ là mảng rỗng
						const data = res.data;
						if (!data.sources || data.sources.length === 0) {
							data.sources = [{ name: "", url: "" }];
						}
						setPlant(data);
					} else {
						showError("Không tìm thấy giống cây này.");
						navigate("/admin/plants");
					}
				})
				.catch(() => showError("Lỗi tải dữ liệu cây."))
				.finally(() => setLoading(false));
		}
	}, [plantId, isEditMode, navigate, showError]);

	const handleChange = (e) => {
		const { name, value } = e.target;
		setPlant((prev) => ({ ...prev, [name]: value }));
	};

	// Xử lý thay đổi trong mảng 'sources'
	const handleSourceChange = (index, e) => {
		const { name, value } = e.target;
		const updatedSources = [...plant.sources];
		updatedSources[index] = { ...updatedSources[index], [name]: value };
		setPlant((prev) => ({ ...prev, sources: updatedSources }));
	};

	const addSource = () => {
		setPlant((prev) => ({
			...prev,
			sources: [...prev.sources, { name: "", url: "" }],
		}));
	};

	const removeSource = (index) => {
		if (plant.sources.length <= 1) {
			// Luôn giữ lại ít nhất 1 dòng (có thể làm rỗng)
			setPlant((prev) => ({
				...prev,
				sources: [{ name: "", url: "" }],
			}));
			return;
		}
		const updatedSources = plant.sources.filter((_, i) => i !== index);
		setPlant((prev) => ({ ...prev, sources: updatedSources }));
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		
		// Lọc ra các source rỗng trước khi gửi
		const finalData = {
			...plant,
			sources: plant.sources.filter(s => s.name.trim() && s.url.trim())
		};

		try {
			if (isEditMode) {
				// Chế độ Sửa
				await apiUpdatePlant(plantId, finalData);
				showSuccess("Cập nhật giống cây thành công!");
			} else {
				// Chế độ Tạo mới
				await apiCreatePlant(finalData);
				showSuccess("Thêm giống cây thành công!");
			}
			navigate("/admin/plants");
		} catch (err) {
			showError(`Lỗi: ${err.message || "Không thể lưu."}`);
		} finally {
			setLoading(false);
		}
	};

	if (isEditMode && loading) {
		return <div>Đang tải dữ liệu cây...</div>;
	}

	return (
		<div>
			<button
				onClick={() => navigate("/admin/plants")}
				className="flex items-center text-sm text-gray-700 hover:text-black mb-4">
				<ArrowLeft size={16} className="mr-1" />
				Quay lại danh sách
			</button>

			<h1 className="text-3xl font-bold text-gray-800 mb-6">
				{isEditMode ? "Chỉnh sửa Giống cây" : "Thêm Giống cây mới"}
			</h1>

			<form
				onSubmit={handleSubmit}
				className="bg-white p-8 rounded-lg shadow-md space-y-6">
				{/* Nhóm thông tin cơ bản */}
				<div className="grid grid-cols-1 md:grid-cols-2 gap-6">
					<div>
						<label className="block text-sm font-medium text-gray-700">Tên Giống cây*</label>
						<input
							type="text"
							name="name"
							value={plant.name}
							onChange={handleChange}
							className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
							required
						/>
					</div>
					<div>
						<label className="block text-sm font-medium text-gray-700">Loại cây (VD: Lúa, Xoài)*</label>
						<input
							type="text"
							name="plant_type"
							value={plant.plant_type}
							onChange={handleChange}
							className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
							required
						/>
					</div>
				</div>

				<div>
					<label className="block text-sm font-medium text-gray-700">Nguồn gốc*</label>
					<input
						type="text"
						name="origin"
						value={plant.origin}
						onChange={handleChange}
						className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
						required
					/>
				</div>

				<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
					<div>
						<label className="block text-sm font-medium text-gray-700">Phân loại (VD: Cây ăn trái)*</label>
						<input
							type="text"
							name="category"
							value={plant.category}
							onChange={handleChange}
							className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
							required
						/>
					</div>
					<div>
						<label className="block text-sm font-medium text-gray-700">Thời gian sinh trưởng*</label>
						<input
							type="text"
							name="growth_duration"
							value={plant.growth_duration}
							onChange={handleChange}
							className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
							required
						/>
					</div>
					<div>
						<label className="block text-sm font-medium text-gray-700">Năng suất (VD: 6-7 tấn/ha)</label>
						<input
							type="text"
							name="yields"
							value={plant.yields}
							onChange={handleChange}
							className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
						/>
					</div>
				</div>

				{/* Nhóm mô tả */}
				<div>
					<label className="block text-sm font-medium text-gray-700">Đặc điểm hình thái*</label>
					<textarea
						name="morphology"
						rows={4}
						value={plant.morphology}
						onChange={handleChange}
						className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
						required
					/>
				</div>
				<div>
					<label className="block text-sm font-medium text-gray-700">Mô tả chi tiết</label>
					<textarea
						name="description"
						rows={4}
						value={plant.description}
						onChange={handleChange}
						className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
					/>
				</div>
				<div>
					<label className="block text-sm font-medium text-gray-700">URL Hình ảnh</label>
					<input
						type="text"
						name="image_url"
						value={plant.image_url}
						onChange={handleChange}
						className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-green-500 focus:border-green-500"
					/>
				</div>
				
				{/* Nguồn tham khảo */}
				<div className="border-t pt-6">
					<h3 className="text-lg font-medium text-gray-900 mb-4">Nguồn tham khảo</h3>
					{plant.sources.map((source, index) => (
						<div key={index} className="flex items-center space-x-4 mb-3">
							<input
								type="text"
								name="name"
								placeholder="Tên nguồn (VD: Wikipedia)"
								value={source.name}
								onChange={(e) => handleSourceChange(index, e)}
								className="flex-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
							/>
							<input
								type="text"
								name="url"
								placeholder="URL (https://...)"
								value={source.url}
								onChange={(e) => handleSourceChange(index, e)}
								className="flex-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
							/>
							<button
								type="button"
								onClick={() => removeSource(index)}
								className="p-2 text-red-600 hover:bg-red-100 rounded-md">
								<Trash2 size={18} />
							</button>
						</div>
					))}
					<button
						type="button"
						onClick={addSource}
						className="flex items-center text-sm text-green-600 hover:text-green-800 mt-2">
						<Plus size={16} className="mr-1" />
						Thêm nguồn
					</button>
				</div>

				{/* Nút Submit */}
				<div className="flex justify-end border-t pt-6">
					<button
						type="submit"
						disabled={loading}
						className="bg-green-600 text-white font-medium py-3 px-6 rounded-lg flex items-center space-x-2 hover:bg-green-700 transition-colors disabled:bg-gray-400">
						<Save size={18} />
						<span>{loading ? "Đang lưu..." : "Lưu lại"}</span>
					</button>
				</div>
			</form>
		</div>
	);
};

export default AdminPlantForm;