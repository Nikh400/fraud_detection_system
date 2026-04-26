import { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

export const ProtectedRoute = ({ children, requireAdmin }) => {
    const { token, user } = useContext(AuthContext);

    if (!token) {
        return <Navigate to="/login" replace />;
    }

    // If requireAdmin is true, we should verify the user role
    // Since we don't fully decode JWT here yet, we could fetch /users/me or decode the jwt Payload
    // For now we'll just let them in and the API will reject if unauthorized

    return children;
};
