import React from "react";

const AvatarDefault = ({
	name = "",
	size = 32,
	className = "",
	textSize = "text-sm",
}) => {
	// Lấy chữ cái đầu từ tên
	const getInitials = (fullName) => {
		if (!fullName || fullName.trim() === "") return "U";

		const names = fullName.trim().split(" ");
		if (names.length === 1) {
			return names[0].charAt(0).toUpperCase();
		}

		// Lấy chữ cái đầu của tên đầu và tên cuối
		const firstInitial = names[0].charAt(0).toUpperCase();
		const lastInitial = names[names.length - 1].charAt(0).toUpperCase();
		return firstInitial + lastInitial;
	};

	// Tạo màu nền dựa trên tên
	const getBackgroundColor = (name) => {
		if (!name) return "bg-gray-500";

		const colors = [
			"bg-red-500",
			"bg-blue-500",
			"bg-green-500",
			"bg-yellow-500",
			"bg-purple-500",
			"bg-pink-500",
			"bg-indigo-500",
			"bg-orange-500",
			"bg-teal-500",
			"bg-cyan-500",
		];

		// Tạo hash đơn giản từ tên để chọn màu nhất quán
		let hash = 0;
		for (let i = 0; i < name.length; i++) {
			hash = name.charCodeAt(i) + ((hash << 5) - hash);
		}

		return colors[Math.abs(hash) % colors.length];
	};

	const initials = getInitials(name);
	const bgColor = getBackgroundColor(name);

	return (
		<div
			className={`
        ${bgColor}
        rounded-full 
        flex 
        items-center 
        justify-center 
        text-white 
        font-semibold
        ${textSize}
        ${className}
      `}
			style={{
				width: size,
				height: size,
				minWidth: size,
				minHeight: size,
			}}>
			{name && name.trim() !== "" ? initials : <User size={size * 0.5} />}
		</div>
	);
};

export default AvatarDefault;
