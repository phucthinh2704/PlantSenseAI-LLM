import axios from "@configs/axios";

export const apiChatWithLLM = async ({ question, user_id, conversation_id, images = [] }) => {
	const formData = new FormData();
	formData.append("user_id", user_id);
	formData.append("question", question ?? "");
	if (conversation_id) {
		formData.append("conversation_id", conversation_id);
	}
	// Đính kèm nhiều file ảnh (nếu có)
	images.forEach((fileObj) => {
		formData.append("images", fileObj.file);
	});

	return axios({
		method: "POST",
		url: `/chat/ask`,
		data: formData,
		headers: {
			"Content-Type": "multipart/form-data",
		},
	});
};
