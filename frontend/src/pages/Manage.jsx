import React, { useState } from 'react';
import { 
  MessageCircle, 
  Leaf, 
  Users, 
  BookOpen, 
  BarChart3, 
  Settings,
  Menu,
  X,
  ChevronRight,
  Sprout,
  Tractor,
  Sun,
  Droplets,
  Award,
  TrendingUp
} from 'lucide-react';

// Header Component
const Header = ({ toggleSidebar, isSidebarOpen }) => {
  return (
    <header className="bg-white shadow-lg border-b border-green-100 sticky top-0 z-40">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-600 rounded-lg">
              <Leaf className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">AgroBot</h1>
              <p className="text-sm text-gray-600">Tư vấn nông nghiệp thông minh</p>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <div className="hidden md:flex items-center space-x-2 bg-green-50 px-4 py-2 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-700 font-medium">Trực tuyến</span>
          </div>
          <button className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2">
            <MessageCircle size={18} />
            <span>Bắt đầu chat</span>
          </button>
        </div>
      </div>
    </header>
  );
};

// Sidebar Component
const Sidebar = ({ isOpen, toggleSidebar }) => {
  const menuItems = [
    { icon: MessageCircle, label: 'Chatbot', active: true },
    { icon: Sprout, label: 'Giống cây trồng' },
    { icon: Tractor, label: 'Kỹ thuật canh tác' },
    { icon: BookOpen, label: 'Thư viện kiến thức' },
    { icon: BarChart3, label: 'Thống kê' },
    { icon: Users, label: 'Cộng đồng' },
    { icon: Settings, label: 'Cài đặt' },
  ];

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={toggleSidebar}
        />
      )}
      
      {/* Sidebar */}
      <aside className={`
        fixed left-0 top-0 h-full w-64 bg-white shadow-xl border-r border-gray-200 z-50 transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:z-auto
      `}>
        <div className="p-6 border-b border-gray-200 lg:hidden">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-600 rounded-lg">
                <Leaf className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold text-gray-800">AgroBot</span>
            </div>
            <button onClick={toggleSidebar}>
              <X size={20} className="text-gray-600" />
            </button>
          </div>
        </div>
        
        <nav className="mt-6 lg:mt-8">
          {menuItems.map((item, index) => (
            <a
              key={index}
              href="#"
              className={`
                flex items-center space-x-3 px-6 py-3 text-sm font-medium transition-colors relative group
                ${item.active 
                  ? 'text-green-600 bg-green-50 border-r-2 border-green-600' 
                  : 'text-gray-600 hover:text-green-600 hover:bg-green-50'
                }
              `}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
              {item.active && (
                <ChevronRight size={16} className="ml-auto" />
              )}
            </a>
          ))}
        </nav>
        
        <div className="absolute bottom-6 left-6 right-6">
          <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-lg p-4 text-white">
            <div className="flex items-center space-x-2 mb-2">
              <Award size={16} />
              <span className="font-medium text-sm">Tip của ngày</span>
            </div>
            <p className="text-xs opacity-90">
              Tưới nước vào buổi sáng sớm giúp cây hấp thụ tốt nhất!
            </p>
          </div>
        </div>
      </aside>
    </>
  );
};

// Stats Card Component
const StatsCard = ({ icon: Icon, title, value, change, color = "green" }) => {
  const colorClasses = {
    green: "bg-green-50 text-green-600 border-green-100",
    blue: "bg-blue-50 text-blue-600 border-blue-100",
    yellow: "bg-yellow-50 text-yellow-600 border-yellow-100",
    purple: "bg-purple-50 text-purple-600 border-purple-100"
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon size={24} />
        </div>
        {change && (
          <div className="flex items-center space-x-1 text-green-600">
            <TrendingUp size={16} />
            <span className="text-sm font-medium">+{change}%</span>
          </div>
        )}
      </div>
      <div className="mt-4">
        <h3 className="text-2xl font-bold text-gray-800">{value}</h3>
        <p className="text-sm text-gray-600 mt-1">{title}</p>
      </div>
    </div>
  );
};

// Feature Card Component
const FeatureCard = ({ icon: Icon, title, description, color = "green" }) => {
  const colorClasses = {
    green: "bg-green-50 text-green-600",
    blue: "bg-blue-50 text-blue-600",
    yellow: "bg-yellow-50 text-yellow-600"
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-all duration-300 group cursor-pointer">
      <div className={`inline-flex p-3 rounded-lg ${colorClasses[color]} group-hover:scale-110 transition-transform`}>
        <Icon size={24} />
      </div>
      <h3 className="text-lg font-semibold text-gray-800 mt-4 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm leading-relaxed">{description}</p>
      <div className="flex items-center text-green-600 text-sm font-medium mt-4 group-hover:translate-x-2 transition-transform">
        <span>Tìm hiểu thêm</span>
        <ChevronRight size={16} className="ml-1" />
      </div>
    </div>
  );
};

// Main Content Component
const MainContent = () => {
  return (
    <main className="flex-1 p-6 space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-green-500 via-green-600 to-green-700 rounded-2xl text-white p-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-black bg-opacity-10"></div>
        <div className="relative z-10">
          <div className="max-w-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Chào mừng đến với AgroBot
            </h2>
            <p className="text-green-100 text-lg mb-6 leading-relaxed">
              Trợ lý AI thông minh giúp bạn tư vấn về giống cây trồng, kỹ thuật canh tác 
              và quản lý nông nghiệp hiệu quả. Hãy bắt đầu cuộc trò chuyện ngay!
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="bg-white text-green-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2">
                <MessageCircle size={20} />
                <span>Bắt đầu tư vấn</span>
              </button>
              <button className="border-2 border-white text-white px-6 py-3 rounded-lg font-medium hover:bg-white hover:text-green-600 transition-colors">
                Xem hướng dẫn
              </button>
            </div>
          </div>
        </div>
        
        {/* Decorative elements */}
        <div className="absolute -top-10 -right-10 w-32 h-32 bg-white bg-opacity-10 rounded-full"></div>
        <div className="absolute -bottom-16 -left-16 w-48 h-48 bg-white bg-opacity-5 rounded-full"></div>
      </div>

      {/* Stats Section */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          icon={Users}
          title="Người dùng hoạt động"
          value="2,847"
          change="12"
          color="green"
        />
        <StatsCard
          icon={MessageCircle}
          title="Cuộc trò chuyện hôm nay"
          value="1,234"
          change="8"
          color="blue"
        />
        <StatsCard
          icon={BookOpen}
          title="Kiến thức trong CSDL"
          value="856"
          color="yellow"
        />
        <StatsCard
          icon={Award}
          title="Độ chính xác"
          value="97.5%"
          change="2"
          color="purple"
        />
      </div>

      {/* Features Section */}
      <div>
        <div className="mb-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-2">
            Tính năng chính
          </h3>
          <p className="text-gray-600">
            Khám phá các công cụ mạnh mẽ giúp bạn canh tác hiệu quả hơn
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <FeatureCard
            icon={Sprout}
            title="Tư vấn giống cây"
            description="Nhận gợi ý về giống cây phù hợp với điều kiện thổ nhưỡng, khí hậu và mục đích canh tác của bạn."
            color="green"
          />
          <FeatureCard
            icon={Sun}
            title="Kỹ thuật canh tác"
            description="Hướng dẫn chi tiết về kỹ thuật trồng, chăm sóc, phòng trừ sâu bệnh và thu hoạch."
            color="yellow"
          />
          <FeatureCard
            icon={Droplets}
            title="Quản lý tưới tiêu"
            description="Tối ưu hóa việc tưới nước dựa trên thời tiết, độ ẩm đất và giai đoạn sinh trưởng."
            color="blue"
          />
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Hoạt động gần đây</h3>
        <div className="space-y-4">
          {[
            {
              user: "Nguyễn Văn A",
              action: "đã hỏi về kỹ thuật trồng lúa",
              time: "2 phút trước",
              type: "question"
            },
            {
              user: "Trần Thị B",
              action: "được tư vấn về giống cà chua",
              time: "5 phút trước",
              type: "advice"
            },
            {
              user: "Lê Văn C",
              action: "đã cập nhật thông tin vườn",
              time: "10 phút trước",
              type: "update"
            }
          ].map((activity, index) => (
            <div key={index} className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-lg transition-colors">
              <div className={`w-2 h-2 rounded-full ${
                activity.type === 'question' ? 'bg-blue-500' : 
                activity.type === 'advice' ? 'bg-green-500' : 'bg-yellow-500'
              }`}></div>
              <div className="flex-1">
                <p className="text-sm text-gray-800">
                  <span className="font-medium">{activity.user}</span> {activity.action}
                </p>
                <p className="text-xs text-gray-500">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
};

// Main Homepage Component
const HomePage = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header toggleSidebar={toggleSidebar} isSidebarOpen={isSidebarOpen} />
      
      <div className="flex">
        <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
        
        <div className="flex-1 lg:ml-64">
          <MainContent />
        </div>
      </div>
    </div>
  );
};

export default HomePage;