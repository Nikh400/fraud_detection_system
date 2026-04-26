import React, { useState, useContext } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { ShieldAlert, LogIn, Loader2, KeyRound, Mail } from 'lucide-react';
import api from '../api';
import '../index.css';

const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const { login } = useContext(AuthContext);
    const navigate = useNavigate();
    const location = useLocation();

    // Check if we arrived here from a successful signup route
    const [successMessage, setSuccessMessage] = useState(
        location.state?.message || null
    );

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        // FastAPI's OAuth2PasswordRequestForm expects form data (x-www-form-urlencoded)
        const formData = new URLSearchParams();
        formData.append('username', email); // OAuth2 expects 'username' field, which contains our email
        formData.append('password', password);

        try {
            const response = await api.post('/auth/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            const { access_token } = response.data;
            if (access_token) {
                login(access_token);
                navigate('/dashboard');
            }
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                'Login failed. Please check your credentials.'
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', padding: '20px' }}>

            <div
                className="glass-panel animate-fade-in"
                style={{ padding: '48px 40px', maxWidth: '440px', width: '100%', position: 'relative', overflow: 'hidden' }}
            >
                {/* Background Ambient Glow */}
                <div style={{
                    position: 'absolute',
                    top: '-50px',
                    left: '-50px',
                    width: '200px',
                    height: '200px',
                    background: 'var(--primary-glow)',
                    filter: 'blur(80px)',
                    pointerEvents: 'none'
                }} />

                <div style={{ textAlign: 'center', marginBottom: '36px', position: 'relative', zIndex: 1 }}>
                    <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '64px',
                        height: '64px',
                        borderRadius: 'var(--radius-lg)',
                        background: 'var(--bg-glass)',
                        border: '1px solid var(--border-glass)',
                        marginBottom: '24px',
                        boxShadow: 'var(--shadow-glow)'
                    }}>
                        <ShieldAlert size={32} color="#818cf8" />
                    </div>
                    <h1 style={{ fontSize: '2rem', marginBottom: '8px' }}>
                        Enter <span className="text-gradient">Aegis</span>
                    </h1>
                    <p className="text-muted" style={{ fontSize: '0.95rem' }}>
                        Multi-Modal Fraud Defense System
                    </p>
                </div>

                <form onSubmit={handleLogin} style={{ position: 'relative', zIndex: 1 }}>
                    {error && (
                        <div className="animate-fade-in" style={{
                            background: 'var(--error-glow)',
                            border: '1px solid var(--error)',
                            color: '#f87171',
                            padding: '12px 16px',
                            borderRadius: 'var(--radius-sm)',
                            marginBottom: '24px',
                            fontSize: '0.9rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}>
                            <span>⚠️</span>
                            {error}
                        </div>
                    )}
                    
                    {successMessage && (
                        <div className="animate-fade-in" style={{
                            background: 'var(--success-glow)', /* Fallback: rgba(74, 222, 128, 0.1) or similar if undefined */
                            border: '1px solid #4ade80',
                            color: '#4ade80',
                            padding: '12px 16px',
                            borderRadius: 'var(--radius-sm)',
                            marginBottom: '24px',
                            fontSize: '0.9rem',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}>
                            <span>✅</span>
                            {successMessage}
                        </div>
                    )}

                    <div style={{ marginBottom: '20px' }} className="animate-fade-in delay-100">
                        <label className="label">Email Address</label>
                        <div style={{ position: 'relative' }}>
                            <Mail size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)' }} />
                            <input
                                type="email"
                                required
                                className="input-field"
                                style={{ paddingLeft: '44px' }}
                                placeholder="admin@aegis.io"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                    </div>

                    <div style={{ marginBottom: '32px' }} className="animate-fade-in delay-200">
                        <label className="label">Password</label>
                        <div style={{ position: 'relative' }}>
                            <KeyRound size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)' }} />
                            <input
                                type="password"
                                required
                                className="input-field"
                                style={{ paddingLeft: '44px' }}
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary animate-fade-in delay-300"
                        style={{ width: '100%', height: '48px' }}
                        disabled={loading}
                    >
                        {loading ? (
                            <Loader2 className="lucide-spin" size={20} />
                        ) : (
                            <>
                                <LogIn size={20} />
                                Authenticate Identity
                            </>
                        )}
                    </button>
                </form>

                    <div className="animate-fade-in delay-300" style={{ textAlign: 'center', marginTop: '24px', position: 'relative', zIndex: 1 }}>
                        <p className="text-muted" style={{ fontSize: '0.85rem' }}>
                            Secured by AES-256 & Multi-Modal Intel
                        </p>
                        <p className="text-muted" style={{ fontSize: '0.9rem', marginTop: '16px' }}>
                            Don't have an account? <Link to="/signup" style={{ color: '#818cf8', textDecoration: 'none' }}>Register Here</Link>
                        </p>
                    </div>
            </div>
        </div>
    );
};

export default Login;
