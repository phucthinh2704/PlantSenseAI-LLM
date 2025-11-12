import axios from "@configs/axios";

export const apiGetConversationHistory = async (userId) =>
	axios({
		method: "GET",
		url: `/conversations/user/${userId}`,
	});
export const apiGetConversationDetails = async (conversationId) =>
	axios({
		method: "GET",
		url: `/conversations/${conversationId}`,
	});
export const apiDeleteConversation = async (conversationId) =>
	axios({
		method: "DELETE",
		url: `/conversations/${conversationId}`,
	});
export const apiUpdateConversationTitle = async (conversationId, title) =>
	axios({
		method: "PUT",
		url: `/conversations/${conversationId}/title`,
		data: { title },
	});

export const apiGetAllConversations = async () =>
	axios({
		method: "GET",
		url: `/conversations/all`,
	});
