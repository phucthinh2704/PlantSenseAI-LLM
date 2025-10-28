import Swal from "sweetalert2";

export default function useAlert() {
	const showSuccess = (message) =>
		Swal.fire({
			title: "Thành công!",
			text: message,
			icon: "success",
			timer: 2000,
			timerProgressBar: true,
			showConfirmButton: false,
		});

	const showError = (message) =>
		Swal.fire({
			title: "Lỗi!",
			text: message,
			icon: "error",
		});

	const showConfirm = async (message) => {
		return Swal.fire({
			title: "Xác nhận",
			text: message,
			icon: "warning",
			showCancelButton: true,
			confirmButtonText: "Đồng ý",
			cancelButtonText: "Hủy",
			confirmButtonColor: "#d33",
			cancelButtonColor: "#3085d6",
		});
	};

	return { showSuccess, showError, showConfirm };
}
