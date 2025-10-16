import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";

export default function MarkdownFormatter({ value, className }) {
	function normalizeInput(src) {
		if (!src) return "";
		let s = String(src);

		// 1) Chuẩn hoá newline
		s = s.replace(/\r\n?/g, "\n");
		s = s.replace(/\\n/g, "\n");

		// 2) Bỏ escape dấu nháy
		s = s.replace(/\\"/g, '"').replace(/\\'/g, "'");

		// 3) Thay mọi unicode-space thành space thường (NBSP, thin space, ideographic space...)
		s = s.replace(
			/[\u00A0\u1680\u180E\u2000-\u200B\u202F\u205F\u3000]/g,
			" "
		);

		// 4) Gom nhiều dòng trống
		s = s.replace(/\n{3,}/g, "\n\n");

		// 5) Đảm bảo có dòng trống trước các list đánh số
		// nếu ngay sau một đoạn văn là dòng bắt đầu bằng `1. ` mà chưa có dòng trống
		s = s.replace(/([^\n])\n(1\.\s)/g, "$1\n\n$2");

		// 6) Dọn khoảng trắng sau số thứ tự: "1.    \t" -> "1. "
		s = s.replace(/^(\s*\d+\.)\s+/gm, (m) => m.trim() + " ");

		// 7) Heading không thừa space đầu dòng
		s = s.replace(/^\s+(#{1,6})\s/gm, "$1 ");

		return s.trim();
	}

	const normalized = normalizeInput(value);
	return (
		<article className={className || "prose max-w-none"}>
			<ReactMarkdown
				remarkPlugins={[remarkGfm]}
				rehypePlugins={[rehypeSanitize]} // nếu vẫn lỗi, tạm thời bỏ hẳn prop này để test
				components={{
					ol: (props) => (
						<ol
							style={{
								paddingLeft: "1.25rem",
								listStyle: "decimal",
							}}
							{...props}
						/>
					),
					ul: (props) => (
						<ul
							style={{
								paddingLeft: "1.25rem",
								listStyle: "disc",
							}}
							{...props}
						/>
					),
				}}>
				{normalized}
			</ReactMarkdown>
		</article>
	);
}
