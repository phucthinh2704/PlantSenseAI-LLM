import React, { useCallback, useEffect, useRef, useState } from "react";
import { apiGetDiseases, apiDeleteDisease } from "@services/disease";
import useAlert from "@hooks/useAlert";
import { Link } from "react-router-dom";
import { Plus, Edit, Trash2 } from "lucide-react";

const AdminDiseaseList = () => {
  const [diseases, setDiseases] = useState([]);
  const [loading, setLoading] = useState(true);

  const { showConfirm, showSuccess, showError } = useAlert();
  // Giữ ổn định các hàm alert để không làm đổi deps
  const showErrorRef = useRef(showError);
  const showSuccessRef = useRef(showSuccess);

  useEffect(() => {
    showErrorRef.current = showError;
    showSuccessRef.current = showSuccess;
  }, [showError, showSuccess]);

  const fetchDiseases = useCallback(async () => {
    setLoading(true);
    try {
      const res = await apiGetDiseases();
      if (res?.success) {
        setDiseases(res.data || []);
      } else {
        showErrorRef.current("Không thể tải danh sách bệnh hại.");
      }
    } catch (err) {
      console.error(err);
      showErrorRef.current("Lỗi máy chủ khi tải bệnh hại.");
    } finally {
      setLoading(false);
    }
  }, []); // <-- không phụ thuộc vào showError nữa

  useEffect(() => {
    fetchDiseases();
  }, [fetchDiseases]);

  const handleDelete = (diseaseId, diseaseName) => {
    showConfirm(
      `Xác nhận xóa "${diseaseName}"?`,
      "Hành động này sẽ xóa bệnh khỏi MongoDB. Bạn sẽ cần chạy lại 'Full Re-index' để xóa khỏi Qdrant."
    ).then(async (result) => {
      if (result?.isConfirmed) {
        try {
          await apiDeleteDisease(diseaseId);
          showSuccessRef.current("Đã xóa bệnh hại thành công.");
          fetchDiseases();
        } catch (err) {
          console.error(err);
          showErrorRef.current("Xóa thất bại. Vui lòng thử lại.");
        }
      }
    });
  };

  if (loading) return <div>Đang tải dữ liệu...</div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">
          Quản lý Bệnh hại ({diseases.length})
        </h1>
        <Link
          to="/admin/diseases/new"
          className="bg-green-600 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2 hover:bg-green-700 transition-colors"
        >
          <Plus size={18} />
          <span>Thêm mới</span>
        </Link>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Tên Bệnh
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nguyên nhân
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Hành động
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {diseases.map((d) => (
              <tr key={d._id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {d.name}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 truncate max-w-md">
                  {d.cause}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <Link
                    to={`/admin/diseases/edit/${d._id}`}
                    className="text-indigo-600 hover:text-indigo-900"
                    title="Sửa"
                  >
                    <Edit size={18} className="inline-block" />
                  </Link>
                  <button
                    onClick={() => handleDelete(d._id, d.name)}
                    className="text-red-600 hover:text-red-900"
                    title="Xóa"
                  >
                    <Trash2 size={18} className="inline-block" />
                  </button>
                </td>
              </tr>
            ))}
            {diseases.length === 0 && (
              <tr>
                <td className="px-6 py-6 text-sm text-gray-500" colSpan={3}>
                  Chưa có bệnh hại nào.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminDiseaseList;
