import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { toast } from 'react-toastify';

const PrivateRoute = ({ children }) => {
  const [redirect, setRedirect] = useState(false);
  // Kiểm tra user trong localStorage
  const user = localStorage.getItem("access_token");

  useEffect(() => {
    if (!user) {
      toast.info('Bạn cần đăng nhập để vào hệ thống!', {
        autoClose: 2000, // Tự động đóng sau 2 giây
      });
      // Đặt delay để đảm bảo toast hiển thị trước khi điều hướng
      const timer = setTimeout(() => {
        setRedirect(true);
      }, 100); // Delay ngắn để toast có thời gian render
      return () => clearTimeout(timer); // Dọn dẹp timer
    }
  }, [user]);

  // Nếu redirect là true, điều hướng về /login
  if (redirect) {
    return <Navigate to="/login" replace />;
  }

  // Nếu có user, render children
  if (user) {
    return children;
  }

  return null; // Tránh render không cần thiết trong lúc chờ
};

export default PrivateRoute;