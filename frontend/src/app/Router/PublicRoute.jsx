import React from 'react';
import { Navigate } from 'react-router-dom';

const PublicRoute = ({ children }) => {
    // Kiểm tra user trong localStorage
    const user = localStorage.getItem('access_token');

    // Nếu đã có user, điều hướng về trang chủ
    if (user) {
        return <Navigate to="/" replace />;
    }

    // Nếu không có user, cho phép truy cập
    return children;
};

export default PublicRoute;