import React, { useCallback, useEffect, useRef, useState } from "react";
import {
	apiGetCultivations,
	apiDeleteCultivation,
} from "@services/cultivation";
import useAlert from "@hooks/useAlert";
import { Link } from "react-router-dom";
import { Plus, Edit, Trash2 } from "lucide-react";

const AdminCultivationList = () => {
	const [techniques, setTechniques] = useState([]);
  const [loading, setLoading] = useState(true);

  const { showConfirm, showSuccess, showError } = useAlert();
  const showErrorRef = useRef(showError);
  const showSuccessRef = useRef(showSuccess);

  // cập nhật ref nếu hook trả về hàm mới
  useEffect(() => {
    showErrorRef.current = showError;
    showSuccessRef.current = showSuccess;
  }, [showError, showSuccess]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiGetCultivations();
      if (res.success) setTechniques(res.data);
      else showErrorRef.current("Không thể tải danh sách kỹ thuật.");
    } catch (e) {
      console.error(e);
      showErrorRef.current("Lỗi máy chủ khi tải kỹ thuật canh tác.");
    } finally {
      setLoading(false);
    }
  }, []); // <-- không còn phụ thuộc vào hàm không ổn định

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleDelete = (id, name) => {
    showConfirm(
      `Xác nhận xóa "${name}"?`,
      "Bạn sẽ cần chạy 'Full Re-index' để xóa hoàn toàn dữ liệu."
    ).then(async (r) => {
      if (r.isConfirmed) {
        try {
          await apiDeleteCultivation(id);
          showSuccessRef.current("Đã xóa kỹ thuật thành công.");
          fetchData(); // gọi lại an toàn
        } catch (e) {
          console.error(e);
          showErrorRef.current("Xóa thất bại. Vui lòng thử lại.");
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
					Kỹ thuật Canh tác ({techniques.length})
				</h1>
				<Link
					to="/admin/cultivation/new"
					className="bg-green-600 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2 hover:bg-green-700 transition-colors">
					<Plus size={18} />
					<span>Thêm mới</span>
				</Link>
			</div>

			<div className="bg-white shadow-md rounded-lg overflow-hidden">
				<table className="min-w-full divide-y divide-gray-200">
					<thead className="bg-gray-50">
						<tr>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Tên Kỹ thuật
							</th>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Loại cây
							</th>
							<th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
								Giai đoạn
							</th>
							<th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
								Hành động
							</th>
						</tr>
					</thead>
					<tbody className="bg-white divide-y divide-gray-200">
						{techniques.map((tech) => (
							<tr key={tech._id}>
								<td className="px-6 py-4 whitespace-nowrap">
									<div className="text-sm font-medium text-gray-900">
										{tech.name}
									</div>
								</td>
								<td className="px-6 py-4 whitespace-nowrap">
									<span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
										{tech.crop_type}
									</span>
								</td>
								<td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
									{tech.application_period}
								</td>
								<td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
									<Link
										to={`/admin/cultivation/edit/${tech._id}`}
										className="text-indigo-600 hover:text-indigo-900"
										title="Sửa">
										<Edit
											size={18}
											className="inline-block"
										/>
									</Link>
									<button
										onClick={() =>
											handleDelete(tech._id, tech.name)
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

export default AdminCultivationList;
