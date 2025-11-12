import { useCallback, useMemo } from "react";
import Swal from "sweetalert2";

export default function useAlert() {
	const showSuccess = useCallback((message, opts = {}) => {
		return Swal.fire({
			title: "Thành công!",
			text: message,
			icon: "success",
			timer: 2000,
			timerProgressBar: true,
			showConfirmButton: false,
			...opts,
		});
	}, []); // <-- không phụ thuộc gì, reference cố định

	const showError = useCallback((message, opts = {}) => {
		return Swal.fire({
			title: "Lỗi!",
			text: message,
			icon: "error",
			...opts,
		});
	}, []);

	const showConfirm = useCallback((message, opts = {}) => {
		// Trả về Promise của SweetAlert2
		return Swal.fire({
			title: "Xác nhận",
			text: message,
			icon: "warning",
			showCancelButton: true,
			confirmButtonText: "Đồng ý",
			cancelButtonText: "Hủy",
			confirmButtonColor: "#d33",
			cancelButtonColor: "#3085d6",
			...opts,
		});
	}, []);

	// Tránh tạo object mới mỗi lần render hook
	return useMemo(
		() => ({ showSuccess, showError, showConfirm }),
		[showSuccess, showError, showConfirm]
	);
}
