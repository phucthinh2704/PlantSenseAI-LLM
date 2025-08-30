import Swal from "sweetalert2";

export const useAlert = () => {
	const showSuccess = (message) =>
		Swal.fire("Thành công!", message, "success");

	const showError = (message) => Swal.fire("Lỗi!", message, "error");

	const showConfirm = async (message) => {
		return Swal.fire({
			title: "Xác nhận",
			text: message,
			icon: "warning",
			showCancelButton: true,
			confirmButtonText: "Đồng ý",
			cancelButtonText: "Hủy",
		});
	};

	return { showSuccess, showError, showConfirm };
};
