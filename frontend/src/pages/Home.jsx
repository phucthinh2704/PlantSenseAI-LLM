import AvatarDefault from "@components/AvatarDefault";
import MarkdownFormatter from "@components/MarkdownFormatter";
import TypewriterMarkdown from "@components/TypewriterMarkdown";
import useAlert from "@hooks/useAlert";
import { logoutUser } from "@redux/auth";
import { apiChatWithLLM } from "@services/chat";
import {
	apiDeleteConversation,
	apiGetConversationDetails,
	apiGetConversationHistory,
	apiUpdateConversationTitle,
} from "@services/conversation";
import { formatDistanceToNow, parseISO } from "date-fns";
import { vi } from "date-fns/locale";
import {
	Bot,
	Bug,
	Check,
	ChevronDown,
	Droplets,
	Edit3,
	Image as ImageIcon,
	Leaf,
	LogOut,
	Menu,
	Plus,
	Send,
	Settings,
	Sprout,
	Sun,
	Trash2,
	User,
	X,
} from "lucide-react";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";

// Chat History Sidebar Component
const ChatSidebar = ({
	isOpen,
	toggleSidebar,
	onConversationSelect,
	currentConversationId,
}) => {
	const [conversations, setConversations] = useState([]);
	const [editingConvId, setEditingConvId] = useState(null);
	const [newTitle, setNewTitle] = useState("");

	const { showConfirm, showError } = useAlert();
	const { user } = useSelector((state) => state.auth);

	useEffect(() => {
		const getConversations = async (userId) => {
			try {
				const response = await apiGetConversationHistory(userId);
				if (response.success && Array.isArray(response.data)) {
					const formattedConversations = response.data
						.map((conv) => {
							const lastMessage =
								conv.messages && conv.messages.length > 0
									? conv.messages[conv.messages.length - 1]
									: null;

							let timestampStr = "Không rõ";
							if (conv.updated_at) {
								try {
									const dateUTC = parseISO(conv.updated_at); // Dùng parseISO để đọc đúng UTC
									timestampStr = formatDistanceToNow(
										dateUTC,
										{ addSuffix: true, locale: vi }
									);
								} catch (e) {
									console.error(
										"Lỗi parse ngày:",
										conv.updated_at,
										e
									);
									// Fallback nếu chuỗi ngày bị lỗi
									timestampStr =
										new Date(
											conv.updated_at
										).toLocaleTimeString("vi-VN") ||
										"Không rõ";
								}
							}

							return {
								id: conv._id,
								title:
									conv.title ||
									"Cuộc trò chuyện chưa có tiêu đề",
								lastMessage: lastMessage
									? lastMessage.content
									: "...",
								timestamp: timestampStr,
								updated_at_raw: conv.updated_at,
								active: conv._id === currentConversationId,
							};
						})
						.sort(
							(a, b) =>
								new Date(b.updated_at_raw || 0) -
								new Date(a.updated_at_raw || 0)
						);
					setConversations(formattedConversations);
				} else {
					console.error(
						"API response is not successful or data is not an array:",
						response
					);
					setConversations([]);
				}
			} catch (error) {
				console.error("Failed to fetch conversations:", error);
				setConversations([]);
			}
		};
		if (user?.id) {
			getConversations(user.id);
		}
	}, [user?.id, currentConversationId]);

	const handleSelectConversation = (convId) => {
		if (onConversationSelect) {
			onConversationSelect(convId);
		}
	};

	const handleNewConversation = () => {
		if (onConversationSelect) {
			onConversationSelect(null);
		}
	};

	const handleEditTitleConversation = (convId, currentTitle) => {
		setEditingConvId(convId);
		setNewTitle(currentTitle);
	};

	const handleSaveTitle = async (convId) => {
		if (!newTitle.trim()) {
			console.error("Tiêu đề không được để trống");
			showError("Tiêu đề không được để trống");
			return;
		}

		try {
			const response = await apiUpdateConversationTitle(convId, newTitle);
			if (response.success) {
				setConversations((prevConversations) =>
					prevConversations.map((conv) =>
						conv.id === convId ? { ...conv, title: newTitle } : conv
					)
				);
				setEditingConvId(null);
				setNewTitle("");
			} else {
				console.error("Cập nhật tiêu đề thất bại:", response);
			}
		} catch (error) {
			console.error("Lỗi khi cập nhật tiêu đề:", error);
		}
	};

	const handleCancelEdit = () => {
		setEditingConvId(null);
		setNewTitle("");
	};

	const handleDeleteConversation = (convId) => {
		showConfirm("Bạn có chắc chắn muốn xóa cuộc trò chuyện này?").then(
			async (result) => {
				if (result.isConfirmed) {
					const response = await apiDeleteConversation(convId);
					if (response.success) {
						setConversations((prevConversations) =>
							prevConversations.filter(
								(conv) => conv.id !== convId
							)
						);
						// Nếu xóa cuộc trò chuyện đang active, chọn tạo mới
						if (
							convId === currentConversationId &&
							onConversationSelect
						) {
							onConversationSelect(null);
						}
					} else {
						console.error(
							"Xóa cuộc trò chuyện thất bại:",
							response
						);
					}
				}
			}
		);
	};

	return (
		<>
			{/* Mobile Overlay */}
			{isOpen && (
				<div
					className="fixed inset-0 bg-black/30 z-40 lg:hidden"
					onClick={toggleSidebar}
				/>
			)}

			{/* Sidebar */}
			<aside
				className={`
        fixed left-0 top-0 h-full w-80 bg-gray-800 text-white z-50 transform transition-transform duration-300 ease-in-out flex flex-col
        ${isOpen ? "translate-x-0" : "-translate-x-full"}
        lg:translate-x-0 lg:relative lg:z-auto
      `}>
				{/* Header */}
				<div className="p-4 border-b border-gray-600">
					<div className="flex items-center justify-between mb-4">
						<div className="flex items-center space-x-3">
							<div className="p-2 bg-green-600 rounded-lg">
								<Leaf className="h-5 w-5 text-white" />
							</div>
							<span className="font-bold text-lg">AgriBot</span>
						</div>
						<button
							onClick={toggleSidebar}
							className="lg:hidden p-2 hover:bg-gray-700 rounded-lg transition-colors">
							<X size={20} />
						</button>
					</div>

					<button
						onClick={handleNewConversation}
						className="w-full flex items-center justify-center space-x-2 bg-gray-800 hover:bg-gray-700 text-white py-3 px-4 rounded-lg border border-gray-600 transition-colors">
						<Plus size={18} />
						<span>Cuộc trò chuyện mới</span>
					</button>
				</div>

				{/* Chat History */}
				<div className="flex-1 overflow-y-auto p-4 space-y-2">
					<h3 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">
						Lịch sử trò chuyện
					</h3>
					{conversations.map((conv) => (
						<div
							key={conv.id}
							onClick={() => {
								// Không cho chọn lại khi đang sửa title
								if (editingConvId !== conv.id) {
									handleSelectConversation(conv.id);
								}
							}}
							className={`group relative p-3 rounded-lg cursor-pointer transition-all duration-200 ${
								conv.active
									? "bg-green-700 text-white"
									: "hover:bg-gray-700 text-gray-200"
							}`}>
							<div className="flex items-start justify-between">
								<div className="flex-1 min-w-0">
									{/* Inline Editing */}
									{editingConvId === conv.id ? (
										<div className="flex items-center gap-2 mb-2">
											<input
												type="text"
												value={newTitle}
												onChange={(e) =>
													setNewTitle(e.target.value)
												}
												onClick={(e) =>
													e.stopPropagation()
												}
												className="flex-1 px-2 py-1 text-sm bg-gray-700 text-white rounded border border-green-500 focus:outline-none focus:ring-2 focus:ring-green-400"
												placeholder="Nhập tiêu đề mới..."
												autoFocus
												onKeyDown={(e) => {
													// Lưu bằng Enter
													if (e.key === "Enter") {
														handleSaveTitle(
															conv.id
														);
													} else if (
														e.key === "Escape"
													) {
														// Hủy bằng Esc
														handleCancelEdit();
													}
												}}
											/>
											<button
												onClick={(e) => {
													e.stopPropagation();
													handleSaveTitle(conv.id);
												}}
												className="p-1.5 bg-green-600 hover:bg-green-700 rounded transition-colors cursor-pointer"
												title="Lưu">
												<Check
													size={15}
													className="text-white"
												/>
											</button>
											<button
												onClick={(e) => {
													e.stopPropagation();
													handleCancelEdit();
												}}
												className="p-1.5 bg-red-600 hover:bg-red-500 rounded transition-colors cursor-pointer mt-0.5"
												title="Hủy">
												<X
													size={15}
													className="text-white"
												/>
											</button>
										</div>
									) : (
										<h4 className="font-medium text-sm truncate">
											{conv.title}
										</h4>
									)}
									{editingConvId !== conv.id && (
										<>
											<p
												className={`text-xs mt-1 truncate ${
													conv.active
														? "text-green-100"
														: "text-gray-300"
												}`}>
												{conv.lastMessage}
											</p>
											<span
												className={`text-xs mt-1 block ${
													conv.active
														? "text-green-200"
														: "text-gray-400"
												}`}>
												{" "}
												{/* Mờ hơn */}
												{conv.timestamp}
											</span>
										</>
									)}
								</div>
								<div
									className={`${
										// Ẩn khi đang edit item này
										editingConvId === conv.id
											? "hidden"
											: "flex"
									} space-x-1 opacity-0 group-hover:opacity-100 transition-opacity absolute top-2 right-2`} // Định vị tuyệt đối
								>
									<button
										className="p-1 hover:bg-blue-600 rounded text-white bg-gray-600" // Thêm màu nền
										onClick={(e) => {
											e.stopPropagation();
											handleEditTitleConversation(
												conv.id,
												conv.title
											);
										}}
										title="Sửa tiêu đề">
										<Edit3 size={12} />
									</button>
									<button
										className="p-1 hover:bg-red-600 rounded text-white bg-gray-600" // Thêm màu nền
										onClick={(e) => {
											e.stopPropagation();
											handleDeleteConversation(conv.id);
										}}
										title="Xóa cuộc trò chuyện">
										<Trash2 size={12} />
									</button>
								</div>
							</div>
						</div>
					))}
				</div>
			</aside>
		</>
	);
};
const Navbar = ({ user }) => {
	const [showUserMenu, setShowUserMenu] = useState(false);
	const dispatch = useDispatch();
	const { showConfirm } = useAlert();

	const getStatusColor = (status) => {
		return status === "active" ? "text-green-600" : "text-gray-500";
	};

	const getStatusText = (status) => {
		return status === "active" ? "Đang hoạt động" : "Không hoạt động";
	};

	const handleLogout = () => {
		showConfirm("Bạn có chắc chắn muốn đăng xuất?").then((result) => {
			if (result.isConfirmed) {
				dispatch(logoutUser());
			}
		});
	};

	return (
		<nav className="bg-white border-b border-green-200 shadow-sm">
			<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<div className="flex items-center justify-between h-16">
					{/* User Info */}
					<div className="flex items-center space-x-4">
						{/* Status */}
						<div className="hidden sm:flex items-center space-x-2">
							<div
								className={`w-2 h-2 rounded-full ${
									user.status === "active"
										? "bg-green-500 animate-pulse"
										: "bg-gray-400"
								}`}></div>
							<span
								className={`text-sm font-medium ${getStatusColor(
									user.status
								)}`}>
								{getStatusText(user.status)}
							</span>
						</div>

						{/* User Menu */}
						<div className="relative">
							<button
								onClick={() => setShowUserMenu(!showUserMenu)}
								className="flex items-center space-x-3 p-2 rounded-lg hover:bg-green-50 transition-colors duration-200 cursor-pointer">
								{user.avatar ? (
									<img
										src={`${user.avatar}`}
										alt="Avatar"
										className="w-8 h-8 rounded-full border-2 border-green-200 object-cover"
									/>
								) : (
									<AvatarDefault name={user.name} />
								)}

								<div className="text-left hidden sm:block">
									<p className="text-sm font-medium text-gray-800">
										{user.name}
									</p>
									<p className="text-xs text-green-600">
										{user.email}
									</p>
								</div>
								<ChevronDown
									className={`w-4 h-4 text-gray-500 transition-transform ${
										showUserMenu ? "rotate-180" : ""
									}`}
								/>
							</button>

							{/* Dropdown Menu */}
							{showUserMenu && (
								<>
									{/* Overlay */}
									<div
										className="fixed inset-0 z-40"
										onClick={() =>
											setShowUserMenu(false)
										}></div>

									<div className="absolute right-0 mt-2 w-72 bg-white border border-green-200 rounded-xl shadow-lg z-50">
										{/* User Info Header */}
										<div className="p-4 border-b border-gray-100">
											<div className="flex items-center space-x-3">
												{user.avatar ? (
													<img
														src={user.avatar}
														alt="Avatar"
														className="w-12 h-12 rounded-full border-2 border-green-200 object-cover"
													/>
												) : (
													<AvatarDefault
														name={user.name}
														size={48}
														textSize="text-lg"
													/>
												)}

												<div className="flex-1">
													<h5 className="font-semibold text-gray-800">
														{user.name}
													</h5>
													<p className="text-xs text-gray-600 line-clamp-1">
														{user.email}
													</p>
													<div className="flex items-center justify-between mt-2">
														<div className="flex items-center space-x-1">
															<div
																className={`w-2 h-2 rounded-full ${
																	user.status ===
																	"active"
																		? "bg-green-500"
																		: "bg-gray-400"
																}`}></div>
															<span
																className={`text-xs ${getStatusColor(
																	user.status
																)}`}>
																{getStatusText(
																	user.status
																)}
															</span>
														</div>
													</div>
												</div>
											</div>

											{/* User ID */}
											<div className="mt-3 p-2 bg-gray-50 rounded-lg">
												<p className="text-xs text-gray-500">
													ID người dùng
												</p>
												<p className="text-sm font-mono text-gray-800">
													{user.id}
												</p>
											</div>
										</div>

										{/* Menu Actions */}
										<div className="p-2">
											<button className="flex items-center space-x-3 w-full p-2 text-left text-gray-700 hover:bg-green-50 rounded-lg transition-colors">
												<User className="w-4 h-4" />
												<span>Thông tin cá nhân</span>
											</button>
											<button className="flex items-center space-x-3 w-full p-2 text-left text-gray-700 hover:bg-green-50 rounded-lg transition-colors">
												<Settings className="w-4 h-4" />
												<span>Cài đặt tài khoản</span>
											</button>
											<hr className="my-2 border-gray-200" />
											<button
												className="flex items-center space-x-3 w-full p-2 text-left text-red-600 hover:bg-red-50 rounded-lg transition-colors"
												onClick={handleLogout}>
												<LogOut className="w-4 h-4" />
												<span>Đăng xuất</span>
											</button>
										</div>
									</div>
								</>
							)}
						</div>
					</div>
				</div>
			</div>
		</nav>
	);
};
// Message Component
// const Message = ({ message, isBot = false, timestamp }) => {
// 	return (
// 		<div
// 			className={`flex w-full mb-6 ${
// 				isBot ? "justify-start" : "justify-end"
// 			}`}>
// 			<div className="flex max-w-4xl w-full">
// 				{/* Avatar */}
// 				<div
// 					className={`flex-shrink-0 flex items-start ${
// 						isBot ? "mr-4" : "ml-4 order-2"
// 					}`}>
// 					<div
// 						className={`w-8 h-8 rounded-full flex items-center justify-center ${
// 							isBot ? "bg-green-600" : "bg-blue-600"
// 						}`}>
// 						{isBot ? (
// 							<Bot
// 								size={16}
// 								className="text-white"
// 							/>
// 						) : (
// 							<User
// 								size={16}
// 								className="text-white"
// 							/>
// 						)}
// 					</div>
// 				</div>

// 				{/* Message Content */}
// 				<div
// 					className={`flex-1 min-w-0 flex flex-col ${
// 						isBot ? "" : "items-end"
// 					}`}>
// 					<div
// 						className={`${
// 							isBot ? "text-left" : "text-right"
// 						} mb-1`}>
// 						<span className="text-xs text-gray-500 font-medium">
// 							{isBot ? "AgriBot" : "Bạn"} • {timestamp}
// 						</span>
// 					</div>
// 					<div
// 						className={`inline-block px-4 py-3 rounded-2xl max-w-[80%] break-words ${
// 							isBot
// 								? "bg-white border border-gray-200 text-gray-800"
// 								: "bg-green-600 text-white"
// 						}`}>
// 						<div className="prose prose-sm max-w-none">
// 							<MarkdownFormatter value={message} />
// 						</div>
// 					</div>
// 				</div>
// 			</div>
// 		</div>
// 	);
// };
// Message Component
const Message = ({
	message,
	isBot = false,
	timestamp,
	streaming = false,
	onStreamEnd,
}) => {
	return (
		<div
			className={`flex w-full mb-6${
				isBot ? "justify-start" : "justify-end"
			}`}>
			<div className="flex max-w-4xl w-full">
				{/* Avatar */}
				<div
					className={`flex-shrink-0 flex items-start ${
						isBot ? "mr-4" : "ml-4 order-2"
					}`}>
					<div
						className={`w-10 h-10 rounded-full flex items-center justify-center ${
							isBot ? "bg-green-600" : "bg-blue-600"
						}`}>
						{isBot ? (
							<Bot
								size={16}
								className="text-white"
							/>
						) : (
							<User
								size={16}
								className="text-white"
							/>
						)}
					</div>
				</div>

				{/* Body */}
				<div
					className={`flex-1 min-w-0 flex flex-col ${
						isBot ? "" : "items-end"
					}`}>
					<div
						className={`${
							isBot ? "text-left" : "text-right"
						} mb-1`}>
						<span className="text-xs text-gray-500 font-medium">
							{isBot ? "AgriBot" : "Bạn"} • {timestamp}
						</span>
					</div>

					<div
						className={`inline-block px-4 py-3 rounded-2xl max-w-fit break-words ${
							isBot
								? "bg-white border border-gray-200 text-gray-800"
								: "bg-green-600 text-white"
						}`}>
						<div className="prose prose-sm max-w-none">
							{isBot && streaming ? (
								<TypewriterMarkdown
									text={message}
									onDone={onStreamEnd}
								/>
							) : (
								<MarkdownFormatter value={message} />
							)}
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};

// Quick Actions Component
const QuickActions = ({ onActionClick }) => {
	const actions = [
		{
			icon: Sprout,
			title: "Tư vấn giống cây",
			description: "Chọn giống phù hợp với điều kiện",
			color: "bg-green-50 text-green-600 border-green-200",
		},
		{
			icon: Sun,
			title: "Kỹ thuật canh tác",
			description: "Hướng dẫn trồng và chăm sóc",
			color: "bg-yellow-50 text-yellow-600 border-yellow-200",
		},
		{
			icon: Droplets,
			title: "Quản lý tưới tiêu",
			description: "Lịch tưới nước tối ưu",
			color: "bg-blue-50 text-blue-600 border-blue-200",
		},
		{
			icon: Bug,
			title: "Phòng trừ sâu bệnh",
			description: "Chẩn đoán và điều trị",
			color: "bg-red-50 text-red-600 border-red-200",
		},
	];

	return (
		<div className="mb-8">
			<div className="text-center mb-6">
				<h2 className="text-2xl font-bold text-gray-800 mb-2">
					Chào mừng bạn đến với AgriBot! 🌱
				</h2>
				<p className="text-gray-600">
					Tôi có thể giúp bạn tư vấn về nông nghiệp. Hãy chọn chủ đề
					hoặc đặt câu hỏi trực tiếp.
				</p>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
				{actions.map((action, index) => (
					<button
						key={index}
						onClick={() => onActionClick(action.title)}
						className={`
              p-4 rounded-xl border-2 transition-all duration-200 hover:shadow-md hover:-translate-y-1 text-left
              ${action.color}
            `}>
						<div className="flex items-start space-x-3">
							<action.icon
								size={24}
								className="flex-shrink-0 mt-1"
							/>
							<div>
								<h3 className="font-semibold mb-1">
									{action.title}
								</h3>
								<p className="text-sm opacity-80">
									{action.description}
								</p>
							</div>
						</div>
					</button>
				))}
			</div>
		</div>
	);
};

// Chat Input Component
const ChatInput = ({ onSendMessage, disabled = false }) => {
	const [message, setMessage] = useState("");
	const [selectedFiles, setSelectedFiles] = useState([]); // chứa nhiều file
	const textareaRef = useRef(null);
	const fileInputRef = useRef(null);

	// Gửi tin nhắn + ảnh
	const handleSubmit = (e) => {
		e.preventDefault();
		if (disabled) return;

		if (message.trim() || selectedFiles.length > 0) {
			onSendMessage(message.trim(), selectedFiles);
			setMessage("");
			setSelectedFiles([]);
			if (textareaRef.current) {
				textareaRef.current.style.height = "auto";
			}
		}
	};

	// Submit khi Enter
	const handleKeyDown = (e) => {
		if (e.key === "Enter" && !e.shiftKey) {
			e.preventDefault();
			handleSubmit(e);
		}
	};

	// Tự động co giãn textarea
	const adjustTextareaHeight = () => {
		if (textareaRef.current) {
			textareaRef.current.style.height = "auto";
			textareaRef.current.style.height =
				textareaRef.current.scrollHeight + "px";
		}
	};

	// Xử lý chọn ảnh từ file input
	const handleFileChange = (e) => {
		const files = Array.from(e.target.files);
		if (files.length > 0) {
			const newFiles = files.map((file) => ({
				file,
				url: URL.createObjectURL(file),
			}));
			setSelectedFiles((prev) => [...prev, ...newFiles]);
		}
		e.target.value = ""; // reset input để lần sau vẫn chọn được cùng ảnh
	};

	// Xử lý paste ảnh từ clipboard
	useEffect(() => {
		const handlePaste = (e) => {
			if (disabled) return;
			if (e.clipboardData?.files?.length > 0) {
				const files = Array.from(e.clipboardData.files).filter((f) =>
					f.type.startsWith("image/")
				);
				if (files.length > 0) {
					const newFiles = files.map((file) => ({
						file,
						url: URL.createObjectURL(file),
					}));
					setSelectedFiles((prev) => [...prev, ...newFiles]);
				}
			}
		};
		window.addEventListener("paste", handlePaste);
		return () => window.removeEventListener("paste", handlePaste);
	}, [disabled]);

	// Xóa ảnh trong preview
	const removeImage = (index) => {
		setSelectedFiles((prev) => {
			const updated = [...prev];
			URL.revokeObjectURL(updated[index].url);
			updated.splice(index, 1);
			return updated;
		});
	};
	const handleClearText = () => {
		setMessage("");
		if (textareaRef.current) {
			textareaRef.current.style.height = "auto";
			textareaRef.current.focus();
		}
	};

	return (
		<div className="border-t border-gray-200 bg-white p-4">
			<div className="max-w-4xl mx-auto">
				{/* Preview nhiều ảnh */}
				{selectedFiles.length > 0 && (
					<div className="flex flex-wrap gap-3 mb-3">
						{selectedFiles.map((item, idx) => (
							<div
								key={idx}
								className="relative w-24 h-24 border border-gray-300 rounded-lg overflow-hidden">
								<img
									src={item.url}
									alt={`preview-${idx}`}
									className="object-cover w-full h-full"
								/>
								<button
									type="button"
									onClick={() => removeImage(idx)}
									className="absolute top-1 right-1 bg-black/60 rounded-full p-1 hover:bg-black/80">
									<X
										size={14}
										className="text-white"
									/>
								</button>
							</div>
						))}
					</div>
				)}

				<form
					onSubmit={handleSubmit}
					className="flex items-center space-x-3">
					{/* Nút upload nhiều ảnh */}
					<div>
						<input
							ref={fileInputRef}
							type="file"
							accept="image/*"
							multiple
							className="hidden"
							onChange={handleFileChange}
							disabled={disabled}
						/>
						<button
							type="button"
							onClick={() => fileInputRef.current?.click()}
							disabled={disabled}
							className={`p-3.5 rounded-xl transition-all duration-200 ${
								!disabled
									? "bg-gray-200 hover:bg-gray-300 text-gray-700"
									: "bg-gray-100 text-gray-400 cursor-not-allowed"
							}`}>
							<ImageIcon size={20} />
						</button>
					</div>

					{/* Textarea nhập tin nhắn */}
					<div className="flex-1 relative">
						<textarea
							ref={textareaRef}
							value={message}
							onChange={(e) => {
								setMessage(e.target.value);
								adjustTextareaHeight();
							}}
							onKeyDown={handleKeyDown}
							placeholder="Nhập câu hỏi hoặc dán ảnh (Ctrl+V)..."
							className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent resize-none max-h-32 min-h-[50px]"
							disabled={disabled}
							rows={1}
						/>
						{message.trim() && (
							<button
								type="button"
								onClick={handleClearText}
								disabled={disabled}
								aria-label="Xoá nội dung đang soạn"
								className={`cursor-pointer absolute right-2 top-1/2  -translate-y-1/2 p-1.5 pb-2 rounded-md transition-colors
        ${
			!disabled
				? "text-gray-500 hover:text-gray-700 hover:bg-gray-100"
				: "text-gray-300 cursor-not-allowed"
		}
      `}>
								<X size={16} />
							</button>
						)}
					</div>

					{/* Nút gửi */}
					<button
						type="submit"
						disabled={
							(!message.trim() && selectedFiles.length === 0) ||
							disabled
						}
						className={`p-3.5 rounded-xl transition-all duration-200 ${
							(message.trim() || selectedFiles.length > 0) &&
							!disabled
								? "bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-xl"
								: "bg-gray-300 text-gray-500 cursor-not-allowed"
						}`}>
						<Send size={20} />
					</button>
				</form>

				<div className="mt-2 text-center">
					<p className="text-xs text-gray-500">
						AgriBot có thể mắc lỗi. Hãy kiểm tra thông tin quan
						trọng.
					</p>
				</div>
			</div>
		</div>
	);
};

// Main Chat Interface Component
const HomePage = () => {
	const [isSidebarOpen, setIsSidebarOpen] = useState(false);
	const [messages, setMessages] = useState([]);
	const [isTyping, setIsTyping] = useState(false);
	const messagesEndRef = useRef(null);
	const { user } = useSelector((state) => state.auth);
	const [currentStep, setCurrentStep] = useState(0);

	const [userId] = useState(user?.id); // ID người dùng
	const [currentConversationId, setCurrentConversationId] = useState(null); // ID cuộc trò chuyện đang hiển thị

	const steps = [
		"Phân tích câu hỏi",
		"Tìm kiếm dữ liệu",
		"Lọc kết quả phù hợp",
		"Xây dựng câu trả lời",
	];

	useEffect(() => {
		if (!isTyping) {
			setCurrentStep(0);
			return;
		}

		const interval = setInterval(() => {
			setCurrentStep((prev) => {
				if (prev === steps.length - 1) {
					return prev;
				}
				return prev + 1;
			});
		}, 3500);

		return () => clearInterval(interval);
	}, [isTyping, steps.length]);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages, isTyping]);

	const toggleSidebar = useCallback(() => {
		setIsSidebarOpen(!isSidebarOpen);
	}, [isSidebarOpen]);

	// Xử lý khi chọn hoặc tạo cuộc trò chuyện từ Sidebar
	const handleConversationSelect = useCallback(
		async (convId) => {
			setIsTyping(false); // Dừng typing nếu có
			setCurrentConversationId(convId); // Cập nhật ID đang chọn

			if (convId === null) {
				// Người dùng muốn tạo cuộc trò chuyện MỚI
				setMessages([]); // Xóa sạch tin nhắn cũ
			} else {
				// Người dùng chọn một cuộc trò chuyện CŨ
				try {
					const response = await apiGetConversationDetails(convId);
					if (
						response.success &&
						response.data &&
						Array.isArray(response.data.messages)
					) {
						// Format lại tin nhắn từ DB sang dạng state của frontend
						const formattedMessages = response.data.messages.map(
							(msg, index) => ({
								id: `${convId}-${index}`, // Tạo ID duy nhất cho tin nhắn
								text: msg.content,
								isBot: msg.sender === "bot",
								timestamp: new Date(
									msg.timestamp
								).toLocaleTimeString("vi-VN", {
									hour: "2-digit",
									minute: "2-digit",
								}),
							})
						);
						setMessages(formattedMessages);
					} else {
						console.error(
							"Failed to load messages or invalid format:",
							response
						);
						setMessages([]); // Reset nếu lỗi
					}
				} catch (error) {
					console.error(
						"Error fetching conversation details:",
						error
					);
					setMessages([]); // Reset nếu lỗi
				}
			}
			if (window.innerWidth < 1024 && isSidebarOpen) {
				// Tự đóng sidebar trên mobile sau khi chọn
				toggleSidebar();
			}
		},
		[isSidebarOpen, toggleSidebar]
	);

	// const handleSendMessage = async (messageText) => {
	// 	const newMessage = {
	// 		id: Date.now(),
	// 		text: messageText,
	// 		isBot: false,
	// 		timestamp: new Date().toLocaleTimeString("vi-VN", {
	// 			hour: "2-digit",
	// 			minute: "2-digit",
	// 		}),
	// 	};

	// 	setMessages((prev) => [...prev, newMessage]);
	// 	setIsTyping(true);

	// 	const responseFromLLM = await apiChatWithLLM({ question: messageText });
	// 	const botResponse = {
	// 		id: Date.now() + 1,
	// 		text:
	// 			responseFromLLM.answer ||
	// 			"Xin lỗi, hiện tại tôi không thể trả lời câu hỏi này.",
	// 		isBot: true,
	// 		timestamp: new Date().toLocaleTimeString("vi-VN", {
	// 			hour: "2-digit",
	// 			minute: "2-digit",
	// 		}),
	// 	};
	// 	setMessages((prev) => [...prev, botResponse]);
	// 	setIsTyping(false);
	// };
	// const handleSendMessage = async (messageText) => {
	// 	const userMsg = {
	// 		id: Date.now(),
	// 		text: messageText,
	// 		isBot: false,
	// 		timestamp: new Date().toLocaleTimeString("vi-VN", {
	// 			hour: "2-digit",
	// 			minute: "2-digit",
	// 		}),
	// 	};
	// 	setMessages((prev) => [...prev, userMsg]);
	// 	setIsTyping(true);

	// 	const payload = {
	// 		question: messageText,
	// 		user_id: userId,
	// 		conversation_id: conversationId,
	// 	};

	// 	const res = await apiChatWithLLM(payload);
	// 	if (res?.conversation_id && !conversationId) {
	// 		setConversationId(res.conversation_id);
	// 	}
	// 	const text =
	// 		res?.answer ||
	// 		"Xin lỗi, hiện tại tôi không thể trả lời câu hỏi này.";

	// 	// thêm bot message với cờ streaming = true
	// 	const botMsgId = Date.now() + 1;
	// 	setMessages((prev) => [
	// 		...prev,
	// 		{
	// 			id: botMsgId,
	// 			text,
	// 			isBot: true,
	// 			streaming: true,
	// 			timestamp: new Date().toLocaleTimeString("vi-VN", {
	// 				hour: "2-digit",
	// 				minute: "2-digit",
	// 			}),
	// 		},
	// 	]);

	// 	// tắt “đang soạn” (vì đã bắt đầu gõ)
	// 	setIsTyping(false);
	// }; // streaming
	const handleSendMessage = async (messageText) => {
		if (!userId) {
			console.error("User ID is missing!");
			// Có thể hiển thị thông báo lỗi cho người dùng
			return;
		}

		const userMsg = {
			id: `user-${Date.now()}`, // ID duy nhất hơn
			text: messageText,
			isBot: false,
			timestamp: new Date().toLocaleTimeString("vi-VN", {
				hour: "2-digit",
				minute: "2-digit",
			}),
		};
		setMessages((prev) => [...prev, userMsg]);
		setIsTyping(true);
		setCurrentStep(0); // Reset animation typing

		// Sử dụng currentConversationId thay vì state cũ
		const payload = {
			question: messageText,
			user_id: userId,
			conversation_id: currentConversationId, // Gửi ID hiện tại (null nếu là cuộc trò chuyện mới)
		};

		try {
			const res = await apiChatWithLLM(payload);

			// Cập nhật currentConversationId nếu đây là tin nhắn đầu tiên của cuộc trò chuyện mới
			if (res?.conversation_id && !currentConversationId) {
				setCurrentConversationId(res.conversation_id);
			}

			const text =
				res?.answer ||
				"Xin lỗi, hiện tại tôi không thể trả lời câu hỏi này.";

			const botMsg = {
				id: `bot-${Date.now() + 1}`, // ID duy nhất hơn
				text: text,
				isBot: true,
				streaming: true,
				timestamp: new Date().toLocaleTimeString("vi-VN", {
					hour: "2-digit",
					minute: "2-digit",
				}),
			};

			setMessages((prev) => [...prev, botMsg]);
		} catch (error) {
			console.error("Error sending message:", error);
			// Hiển thị tin nhắn lỗi cho người dùng
			const errorMsg = {
				id: `error-${Date.now() + 2}`,
				text: "Đã có lỗi xảy ra khi gửi tin nhắn. Vui lòng thử lại.",
				isBot: true,
				timestamp: new Date().toLocaleTimeString("vi-VN", {
					hour: "2-digit",
					minute: "2-digit",
				}),
			};
			setMessages((prev) => [...prev, errorMsg]);
		} finally {
			setIsTyping(false); // Luôn tắt typing sau khi hoàn tất hoặc lỗi
		}
	};
	const handleQuickAction = (actionTitle) => {
		handleSendMessage(`Tôi muốn tìm hiểu về ${actionTitle.toLowerCase()}`);
	};

	return (
		<div className="h-screen flex bg-gray-50">
			<ChatSidebar
				isOpen={isSidebarOpen}
				toggleSidebar={toggleSidebar}
				onConversationSelect={handleConversationSelect}
				currentConversationId={currentConversationId}
			/>

			{/* Main Chat Area */}
			<div className="flex-1 flex flex-col">
				{/* Header */}
				<header className="bg-white shadow-sm border-b border-gray-200 px-4 py-3 flex items-center justify-between sticky top-0 z-30">
					<div className="flex items-center space-x-4">
						<button
							onClick={toggleSidebar}
							className="lg:hidden p-2 hover:bg-gray-100 rounded-lg transition-colors">
							<Menu size={20} />
						</button>
						<div className="flex items-center space-x-3">
							<div className="p-2 bg-green-600 rounded-lg">
								<Leaf className="h-5 w-5 text-white" />
							</div>
							<div>
								<h2 className="font-semibold text-gray-800">
									AgriBot Chat
								</h2>
								<p className="text-sm text-gray-600">
									Trợ lý AI nông nghiệp
								</p>
							</div>
						</div>
					</div>

					<Navbar user={user} />
				</header>

				{/* Messages Area */}
				<div className="flex-1 overflow-y-auto">
					<div className="max-w-4xl mx-auto p-5">
						{messages.length === 0 && !isTyping ? (
							<QuickActions onActionClick={handleQuickAction} />
						) : (
							<div className="space-y-4">
								{/* {messages.map((message) => (
									<Message
										key={message.id}
										message={message.text}
										isBot={message.isBot}
										timestamp={message.timestamp}
									/>
								))} */}
								{messages.map((m) => (
									<Message
										key={m.id}
										message={m.text}
										isBot={m.isBot}
										timestamp={m.timestamp}
										streaming={m.streaming}
										onStreamEnd={() => {
											if (m.streaming) {
												setMessages((prev) =>
													prev.map((x) =>
														x.id === m.id
															? {
																	...x,
																	streaming: false,
															  }
															: x
													)
												);
											}
										}}
									/>
								))}
								{isTyping && (
									<div className="flex w-full mb-6">
										<div className="flex max-w-4xl w-full">
											<div className="flex-shrink-0 mr-4">
												<div className="w-8 h-8 rounded-full flex items-center justify-center bg-green-600">
													<Bot
														size={16}
														className="text-white"
													/>
												</div>
											</div>
											<div className="flex-1 min-w-0">
												<div className="text-left mb-1">
													<span className="text-xs text-gray-500 font-medium">
														AgriBot đang soạn tin...
													</span>
												</div>
												<div className="inline-block px-4 py-3 rounded-2xl bg-white border border-gray-200">
													<div className="flex items-center gap-2 h-6">
														<span className="text-gray-600 text-sm font-medium min-w-fit">
															{steps[currentStep]}
														</span>
														<div className="thinking flex gap-1">
															{[0, 1, 2].map(
																(i) => (
																	<div
																		key={i}
																		className="thinking-dot w-2 h-2 bg-green-600 rounded-full"
																	/>
																)
															)}
														</div>
													</div>
												</div>
											</div>
										</div>
									</div>
								)}
								<div ref={messagesEndRef} />
							</div>
						)}
					</div>
				</div>

				{/* Chat Input */}
				<ChatInput
					onSendMessage={handleSendMessage}
					disabled={isTyping}
				/>
			</div>
		</div>
	);
};

export default HomePage;
