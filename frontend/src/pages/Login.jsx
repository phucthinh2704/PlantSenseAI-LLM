import { GoogleLogin, GoogleOAuthProvider } from "@react-oauth/google";
import {
	Eye,
	EyeOff,
	Leaf,
	MessageCircle,
	TrendingUp,
	Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiLogin } from "../api/auth";
const LoginPage = () => {
	const [showPassword, setShowPassword] = useState(false);
	const [email, setEmail] = useState("");
	const [password, setPassword] = useState("");
	const [isLoading, setIsLoading] = useState(false);
	const [animatedStats, setAnimatedStats] = useState([0, 0, 0]);

	// Animate statistics numbers
	useEffect(() => {
		const targets = [1250, 850, 15000];
		const duration = 2000;
		const increment = 50;

		const timers = targets.map((target, index) => {
			let current = 0;
			return setInterval(() => {
				current += Math.ceil(target / (duration / increment));
				if (current >= target) {
					current = target;
					clearInterval(timers[index]);
				}
				setAnimatedStats((prev) => {
					const newStats = [...prev];
					newStats[index] = current;
					return newStats;
				});
			}, increment);
		});

		return () => timers.forEach((timer) => clearInterval(timer));
	}, []);

	const handleSuccess = async (credentialResponse) => {
		try {
			const token = credentialResponse.credential;
			console.log("Google ID Token:", token);

			// Gửi token lên FastAPI để verify
			const res = await apiLogin({ token });

			console.log("Server response:", res);
			localStorage.setItem("access_token", res.access_token);
		} catch (error) {
			console.error("Error during Google login:", error);
		}
	};

	const handleSubmit = (e) => {
		e.preventDefault();
		setIsLoading(true);
		setTimeout(() => {
			setIsLoading(false);
			alert("Đăng nhập thành công!");
		}, 1000);
	};

	return (
		<div className="min-h-screen bg-gradient-to-br from-green-400 via-emerald-500 to-teal-600 flex items-center justify-center p-4 relative overflow-hidden">
			{/* Animated background elements */}
			<div className="absolute inset-0 overflow-hidden">
				<div className="absolute -top-10 -left-10 w-72 h-72 bg-white/10 rounded-full blur-xl animate-pulse"></div>
				<div className="absolute -bottom-10 -right-10 w-96 h-96 bg-white/5 rounded-full blur-2xl animate-pulse delay-1000"></div>
				<div className="absolute top-1/2 left-1/4 w-64 h-64 bg-emerald-400/10 rounded-full blur-xl animate-bounce duration-3000"></div>
			</div>

			<div className="w-full max-w-6xl mx-auto flex items-center justify-center gap-8 relative z-10">
				{/* Left side - Info Panel */}
				<div className="hidden lg:flex flex-col space-y-8 text-white max-w-lg">
					<div className="space-y-4">
						<div className="flex items-center space-x-3">
							<div className="p-2 bg-white/20 rounded-xl backdrop-blur-sm">
								<Leaf className="w-8 h-8 text-green-100" />
							</div>
							<div>
								<h1 className="text-3xl font-bold">
									AgriChat Bot
								</h1>
								<p className="text-green-100">
									Trợ lý AI cho nông nghiệp thông minh
								</p>
							</div>
						</div>
						<p className="text-lg text-green-50 leading-relaxed">
							Chatbot tư vấn chuyên nghiệp về kỹ thuật trồng trọt,
							chăm sóc cây trồng và giải pháp nông nghiệp bền
							vững.
						</p>
					</div>

					{/* Statistics */}
					<div className="grid grid-cols-3 gap-4">
						<div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center transform hover:scale-105 transition-transform duration-300">
							<Users className="w-6 h-6 mx-auto mb-2 text-green-200" />
							<div className="text-2xl font-bold">
								{animatedStats[0].toLocaleString()}
							</div>
							<div className="text-sm text-green-100">
								Nông dân
							</div>
						</div>
						<div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center transform hover:scale-105 transition-transform duration-300">
							<MessageCircle className="w-6 h-6 mx-auto mb-2 text-green-200" />
							<div className="text-2xl font-bold">
								{animatedStats[1].toLocaleString()}
							</div>
							<div className="text-sm text-green-100">Tư vấn</div>
						</div>
						<div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center transform hover:scale-105 transition-transform duration-300">
							<TrendingUp className="w-6 h-6 mx-auto mb-2 text-green-200" />
							<div className="text-2xl font-bold">
								{animatedStats[2].toLocaleString()}
							</div>
							<div className="text-sm text-green-100">
								Cây trồng
							</div>
						</div>
					</div>

					{/* Features */}
					<div className="space-y-3">
						<div className="flex items-center space-x-3 text-green-50">
							<div className="w-2 h-2 bg-green-300 rounded-full animate-pulse"></div>
							<span>Tư vấn kỹ thuật canh tác 24/7</span>
						</div>
						<div className="flex items-center space-x-3 text-green-50">
							<div className="w-2 h-2 bg-green-300 rounded-full animate-pulse delay-200"></div>
							<span>Chẩn đoán bệnh tật cây trồng</span>
						</div>
						<div className="flex items-center space-x-3 text-green-50">
							<div className="w-2 h-2 bg-green-300 rounded-full animate-pulse delay-400"></div>
							<span>Gợi ý phân bón và thuốc bảo vệ thực vật</span>
						</div>
						<div className="flex items-center space-x-3 text-green-50">
							<div className="w-2 h-2 bg-green-300 rounded-full animate-pulse delay-600"></div>
							<span>Dự báo thời tiết và mùa vụ</span>
						</div>
					</div>
				</div>

				{/* Right side - Login Form */}
				<div className="w-full max-w-md">
					<div className="bg-white/95 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
						<div className="text-center mb-8">
							<div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl mb-4 shadow-lg">
								<Leaf className="w-8 h-8 text-white" />
							</div>
							<h2 className="text-2xl font-bold text-gray-800 mb-2">
								Chào mừng trở lại!
							</h2>
							<p className="text-gray-600">
								Đăng nhập để tiếp tục sử dụng AgriChat Bot
							</p>
						</div>

						{/* Google Login Button */}
						{/* <button
              onClick={handleGoogleLogin}
              disabled={isLoading}
              className="w-full mb-6 bg-white border-2 border-gray-200 text-gray-700 py-3 px-4 rounded-xl font-medium flex items-center justify-center space-x-3 hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <span>
                {isLoading ? 'Đang đăng nhập...' : 'Đăng nhập với Google'}
              </span>
            </button> */}

						{/* Email/Password Form */}
						<div className="space-y-4">
							<div>
								<label
									htmlFor="email"
									className="block text-sm font-medium text-gray-700 mb-2">
									Email
								</label>
								<input
									type="email"
									id="email"
									value={email}
									onChange={(e) => setEmail(e.target.value)}
									className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
									placeholder="example@email.com"
									required
								/>
							</div>

							<div>
								<label
									htmlFor="password"
									className="block text-sm font-medium text-gray-700 mb-2">
									Mật khẩu
								</label>
								<div className="relative">
									<input
										type={
											showPassword ? "text" : "password"
										}
										id="password"
										value={password}
										onChange={(e) =>
											setPassword(e.target.value)
										}
										className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
										placeholder="••••••••"
										required
									/>
									<button
										type="button"
										onClick={() =>
											setShowPassword(!showPassword)
										}
										className="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600">
										{showPassword ? (
											<EyeOff className="w-5 h-5" />
										) : (
											<Eye className="w-5 h-5" />
										)}
									</button>
								</div>
							</div>

							<div className="flex items-center justify-between text-sm">
								<label className="flex items-center">
									<input
										type="checkbox"
										className="rounded border-gray-300 text-green-600 focus:ring-green-500"
									/>
									<span className="ml-2 text-gray-600">
										Ghi nhớ đăng nhập
									</span>
								</label>
								<a
									href="#"
									className="text-green-600 hover:text-green-700 font-medium">
									Quên mật khẩu?
								</a>
							</div>

							<button
								onClick={handleSubmit}
								disabled={isLoading}
								className="w-full bg-gradient-to-r from-green-500 to-emerald-500 text-white py-3 px-4 rounded-xl font-medium hover:from-green-600 hover:to-emerald-600 transform hover:scale-[1.02] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl">
								{isLoading ? (
									<div className="flex items-center justify-center space-x-2">
										<div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
										<span>Đang xử lý...</span>
									</div>
								) : (
									"Đăng nhập"
								)}
							</button>
						</div>
						<div className="flex items-center mt-6">
							<hr className="flex-1 border-gray-300" />
							<span className="px-4 text-gray-500 text-sm">
								hoặc
							</span>
							<hr className="flex-1 border-gray-300" />
						</div>
						<GoogleOAuthProvider
							clientId={`${
								import.meta.env.VITE_GOOGLE_CLIENT_ID
							}`}>
							<div className="App">
								<p className="text-center">
									Đăng nhập với Google
								</p>
								<GoogleLogin
									onSuccess={handleSuccess}
									onError={() => console.log("Login Failed")}
								/>
							</div>
						</GoogleOAuthProvider>
						<p className="text-center text-gray-600 text-sm mt-6">
							Chưa có tài khoản?{" "}
							<a
								href="#"
								className="text-green-600 hover:text-green-700 font-medium">
								Đăng ký ngay
							</a>
						</p>
					</div>

					{/* Mobile stats for small screens */}
					<div className="lg:hidden mt-6 grid grid-cols-3 gap-3">
						<div className="bg-white/20 backdrop-blur-sm rounded-xl p-3 text-center text-white">
							<div className="text-lg font-bold">
								{(animatedStats[0] / 1000).toFixed(1)}K+
							</div>
							<div className="text-xs">Nông dân</div>
						</div>
						<div className="bg-white/20 backdrop-blur-sm rounded-xl p-3 text-center text-white">
							<div className="text-lg font-bold">
								{animatedStats[1].toLocaleString()}
							</div>
							<div className="text-xs">Tư vấn</div>
						</div>
						<div className="bg-white/20 backdrop-blur-sm rounded-xl p-3 text-center text-white">
							<div className="text-lg font-bold">
								{(animatedStats[2] / 1000).toFixed(0)}K+
							</div>
							<div className="text-xs">Cây trồng</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};

export default LoginPage;
