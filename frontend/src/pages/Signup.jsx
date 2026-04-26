import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldAlert, UserPlus, Loader2, KeyRound, Mail } from 'lucide-react';
import api from '../api';
import '../index.css';

const Signup = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const navigate = useNavigate();

    const handleSignup = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        if (password !== confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        try {
            await api.post('/users/', {
                email,
                password
            });
            // Auto redirect to login upon success
            navigate('/login', { state: { message: 'Signup successful! Please log in.' } });
        } catch (err) {
            console.error(err);
            setError(
                err.response?.data?.detail ||
                'Signup failed. Please try again.'
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
                        Join <span className="text-gradient">Aegis</span>
                    </h1>
                    <p className="text-muted" style={{ fontSize: '0.95rem' }}>
                        Create a new operative clearance
                    </p>
                </div>

                <form onSubmit={handleSignup} style={{ position: 'relative', zIndex: 1 }}>
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

                    <div style={{ marginBottom: '20px' }} className="animate-fade-in delay-100">
                        <label className="label">Email Address</label>
                        <div style={{ position: 'relative' }}>
                            <Mail size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)' }} />
                            <input
                                type="email"
                                required
                                className="input-field"
                                style={{ paddingLeft: '44px' }}
                                placeholder="operative@aegis.io"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            />
                        </div>
                    </div>

                    <div style={{ marginBottom: '20px' }} className="animate-fade-in delay-200">
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

                    <div style={{ marginBottom: '32px' }} className="animate-fade-in delay-200">
                        <label className="label">Confirm Password</label>
                        <div style={{ position: 'relative' }}>
                            <KeyRound size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)' }} />
                            <input
                                type="password"
                                required
                                className="input-field"
                                style={{ paddingLeft: '44px' }}
                                placeholder="••••••••"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary animate-fade-in delay-300"
                        style={{ width: '100%', height: '48px', marginBottom: '16px' }}
                        disabled={loading}
                    >
                        {loading ? (
                            <Loader2 className="lucide-spin" size={20} />
                        ) : (
                            <>
                                <UserPlus size={20} />
                                Register Identity
                            </>
                        )}
                    </button>
                    
                    <div className="animate-fade-in delay-300" style={{ textAlign: 'center' }}>
                        <p className="text-muted" style={{ fontSize: '0.9rem' }}>
                            Already have clearance? <Link to="/login" style={{ color: '#818cf8', textDecoration: 'none' }}>Authenticate Here</Link>
                        </p>
                    </div>
                </form>

            </div>
        </div>
    );
};

export default Signup;
