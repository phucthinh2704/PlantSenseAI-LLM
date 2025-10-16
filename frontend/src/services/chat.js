import axios from "@configs/axios";

export const apiChatWithLLM = async (data) =>
	axios({
		method: "POST",
		url: `/chat/ask`,
		data,
	});
