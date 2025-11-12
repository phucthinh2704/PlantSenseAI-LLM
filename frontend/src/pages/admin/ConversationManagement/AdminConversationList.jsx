import React, { useEffect, useRef, useState } from "react";
import { apiGetAllConversations } from "@services/conversation";
import useAlert from "@hooks/useAlert";
import { Link } from "react-router-dom";
import { Eye, Trash2 } from "lucide-react";
import { formatDistanceToNow, parseISO } from "date-fns";
import { vi } from "date-fns/locale";

const AdminConversationList = () => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  const { showError } = useAlert();
  const showErrorRef = useRef(showError);

  // nếu hook trả về hàm mới, cập nhật ref nhưng không gây re-run effect
  useEffect(() => {
    showErrorRef.current = showError;
  }, [showError]);

  useEffect(() => {
    const ac = new AbortController();
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await apiGetAllConversations({ signal: ac.signal });
        if (ac.signal.aborted) return;

        if (res?.success) {
          setConversations(res.data || []);
        } else {
          showErrorRef.current("Không thể tải lịch sử hội thoại.");
        }
      } catch (err) {
        if (ac.signal.aborted) return;
        console.error(err);
        showErrorRef.current("Lỗi máy chủ khi tải hội thoại.");
      } finally {
        if (!ac.signal.aborted) setLoading(false);
      }
    };
    fetchData();
    return () => ac.abort();
  }, []); // <-- không còn phụ thuộc vào showError

  const formatTimestamp = (isoString) => {
    try {
      const dateUTC = parseISO(isoString);
      return formatDistanceToNow(dateUTC, { addSuffix: true, locale: vi });
    } catch (e) {
      console.error("Lỗi parse ngày:", isoString, e);
      return "Không rõ";
    }
  };

  if (loading) return <div>Đang tải dữ liệu...</div>;

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        Lịch sử Hội thoại ({conversations.length})
      </h1>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tiêu đề</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cập nhật lần cuối</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Hành động</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {conversations.map((conv) => (
              <tr key={conv._id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {conv.title || "Chưa có tiêu đề"}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                  {conv.user_id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {formatTimestamp(conv.updated_at)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <Link
                    to={`/admin/conversations/view/${conv._id}`}
                    className="text-blue-600 hover:text-blue-900"
                    title="Xem chi tiết"
                  >
                    <Eye size={18} className="inline-block" />
                  </Link>
                  <button
                    // onClick={() => handleDelete(conv._id)}
                    className="text-red-600 hover:text-red-900"
                    title="Xóa"
                  >
                    <Trash2 size={18} className="inline-block" />
                  </button>
                </td>
              </tr>
            ))}
            {conversations.length === 0 && (
              <tr>
                <td className="px-6 py-6 text-sm text-gray-500" colSpan={4}>
                  Chưa có hội thoại nào.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AdminConversationList;
