import useAlert from "@hooks/useAlert";
import { logoutUser } from "@redux/auth";
import {
	Bot,
	Bug,
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
import React, { useEffect, useRef, useState } from "react";
import { useDispatch } from "react-redux";

// Chat History Sidebar Component
const ChatSidebar = ({ isOpen, toggleSidebar }) => {
	const [conversations, setConversations] = useState([
		{
			id: 1,
			title: "Tư vấn trồng lúa mùa khô",
			lastMessage: "Cảm ơn bạn đã tư vấn về giống lúa IR64",
			timestamp: "2 giờ trước",
			active: true,
		},
		{
			id: 2,
			title: "Phòng trừ sâu bệnh cà chua",
			lastMessage: "Thuốc nào hiệu quả cho bệnh héo xanh?",
			timestamp: "1 ngày trước",
			active: false,
		},
		{
			id: 3,
			title: "Kỹ thuật tưới tiêu hiệu quả",
			lastMessage: "Lịch tưới nước cho rau màu",
			timestamp: "3 ngày trước",
			active: false,
		},
		{
			id: 4,
			title: "Chọn giống ngô phù hợp",
			lastMessage: "NK7328 có phù hợp với đất chua không?",
			timestamp: "1 tuần trước",
			active: false,
		},
	]);

	const dispatch = useDispatch();
	const { showConfirm } = useAlert();
	const handleLogout = () => {
		showConfirm("Bạn có chắc chắn muốn đăng xuất?").then((result) => {
			if (result.isConfirmed) {
				dispatch(logoutUser());
			}
		});
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

					<button className="w-full flex items-center justify-center space-x-2 bg-gray-800 hover:bg-gray-700 text-white py-3 px-4 rounded-lg border border-gray-600 transition-colors">
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
							className={`
                group relative p-3 rounded-lg cursor-pointer transition-all duration-200
                ${
					conv.active
						? "bg-green-600 text-white"
						: "hover:bg-gray-800 text-gray-300"
				}
              `}>
							<div className="flex items-start justify-between">
								<div className="flex-1 min-w-0">
									<h4 className="font-medium text-sm truncate">
										{conv.title}
									</h4>
									<p
										className={`text-xs mt-1 truncate ${
											conv.active
												? "text-green-100"
												: "text-gray-500"
										}`}>
										{conv.lastMessage}
									</p>
									<span
										className={`text-xs mt-1 block ${
											conv.active
												? "text-green-200"
												: "text-gray-600"
										}`}>
										{conv.timestamp}
									</span>
								</div>
								<div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
									<button className="p-1 hover:bg-gray-600 rounded">
										<Edit3 size={12} />
									</button>
									<button className="p-1 hover:bg-red-600 rounded">
										<Trash2 size={12} />
									</button>
								</div>
							</div>
						</div>
					))}
				</div>

				{/* Footer */}
				<div className="p-4 border-t border-gray-700 space-y-2">
					<button className="w-full flex items-center space-x-3 p-3 hover:bg-gray-800 rounded-lg transition-colors text-left">
						<User size={18} />
						<span>Tài khoản</span>
					</button>
					<button className="w-full flex items-center space-x-3 p-3 hover:bg-gray-800 rounded-lg transition-colors text-left">
						<Settings size={18} />
						<span>Cài đặt</span>
					</button>
					<button
						onClick={handleLogout} // hàm xử lý đăng xuất
						className="w-full flex items-center space-x-3 p-3 hover:bg-red-600/20 text-red-500 rounded-lg transition-colors text-left">
						<LogOut size={18} />
						<span>Đăng xuất</span>
					</button>
				</div>
			</aside>
		</>
	);
};

// Message Component
const Message = ({ message, isBot = false, timestamp }) => {
	return (
		<div
			className={`flex w-full mb-6 ${
				isBot ? "justify-start" : "justify-end"
			}`}>
			<div className="flex max-w-4xl w-full">
				{/* Avatar */}
				<div
					className={`flex-shrink-0 flex items-start ${
						isBot ? "mr-4" : "ml-4 order-2"
					}`}>
					<div
						className={`w-8 h-8 rounded-full flex items-center justify-center ${
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

				{/* Message Content */}
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
						className={`inline-block px-4 py-3 rounded-2xl max-w-[80%] break-words ${
							isBot
								? "bg-white border border-gray-200 text-gray-800"
								: "bg-green-600 text-white"
						}`}>
						<div className="prose prose-sm max-w-none">
							{message}
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

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages, isTyping]);

	const toggleSidebar = () => {
		setIsSidebarOpen(!isSidebarOpen);
	};

	const handleSendMessage = async (messageText) => {
		const newMessage = {
			id: Date.now(),
			text: messageText,
			isBot: false,
			timestamp: new Date().toLocaleTimeString("vi-VN", {
				hour: "2-digit",
				minute: "2-digit",
			}),
		};

		setMessages((prev) => [...prev, newMessage]);
		setIsTyping(true);

		// Simulate bot response
		setTimeout(() => {
			const botResponse = {
				id: Date.now() + 1,
				text: `Cảm ơn bạn đã hỏi về "${messageText}". Đây là một câu hỏi rất hay về nông nghiệp! Tôi sẽ cung cấp thông tin chi tiết để hỗ trợ bạn tốt nhất. Để đưa ra lời khuyên chính xác, bạn có thể cung cấp thêm thông tin về điều kiện thổ nhưỡng, khí hậu và diện tích canh tác không?`,
				isBot: true,
				timestamp: new Date().toLocaleTimeString("vi-VN", {
					hour: "2-digit",
					minute: "2-digit",
				}),
			};
			setMessages((prev) => [...prev, botResponse]);
			setIsTyping(false);
		}, 2000);
	};

	const handleQuickAction = (actionTitle) => {
		handleSendMessage(`Tôi muốn tìm hiểu về ${actionTitle.toLowerCase()}`);
	};

	return (
		<div className="h-screen flex bg-gray-50">
			<ChatSidebar
				isOpen={isSidebarOpen}
				toggleSidebar={toggleSidebar}
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

					<div className="flex items-center space-x-2">
						<div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
						<span className="text-sm text-green-600 font-medium">
							Online
						</span>
					</div>
				</header>

				{/* Messages Area */}
				<div className="flex-1 overflow-y-auto">
					<div className="max-w-4xl mx-auto p-6">
						{messages.length === 0 ? (
							<QuickActions onActionClick={handleQuickAction} />
						) : (
							<div className="space-y-4">
								{messages.map((message) => (
									<Message
										key={message.id}
										message={message.text}
										isBot={message.isBot}
										timestamp={message.timestamp}
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
													<div className="flex space-x-2">
														<div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
														<div
															className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
															style={{
																animationDelay:
																	"0.1s",
															}}></div>
														<div
															className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
															style={{
																animationDelay:
																	"0.2s",
															}}></div>
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
