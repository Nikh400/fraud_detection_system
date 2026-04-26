import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { ShieldCheck, ShieldAlert, Activity, DollarSign, Clock, MapPin, Smartphone, CreditCard, LogOut } from 'lucide-react';
import api from '../api';

const UserDashboard = () => {
    const { logout } = useContext(AuthContext);
    const [profile, setProfile] = useState(null);
    const [riskScore, setRiskScore] = useState(null);
    const [loading, setLoading] = useState(true);

    // Transaction form state
    const [amount, setAmount] = useState('25.50');
    const [age, setAge] = useState('30');
    const [hour, setHour] = useState('Fetching...');
    const [category, setCategory] = useState('groceries');
    const [location, setLocation] = useState('Fetching...');
    const [description, setDescription] = useState('Weekly grocery shopping');
    const [merchant, setMerchant] = useState('Whole Foods');
    const [documentImage, setDocumentImage] = useState(null);

    const [prediction, setPrediction] = useState(null);
    const [predicting, setPredicting] = useState(false);

    useEffect(() => {
        const fetchLocation = async () => {
            try {
                const response = await fetch('https://ipapi.co/json/');
                const data = await response.json();

                // Setup timezone hour population
                let currentZone = 'Asia/Kolkata'; // Default to IST
                if (data.timezone) {
                    currentZone = data.timezone;
                }

                // Get current hour (0-23) for that timezone
                try {
                    const localTimeStr = new Intl.DateTimeFormat('en-GB', {
                        timeZone: currentZone,
                        hour: 'numeric',
                        hour12: false
                    }).format(new Date());

                    const extractedHour = parseInt(localTimeStr, 10);
                    setHour(extractedHour >= 24 ? "0" : extractedHour.toString());
                } catch (e) {
                    console.error("Timezone fetch failed", e);
                    setHour(new Date().getHours().toString());
                }

                // Only use location if country is India (IN)
                if (data.country_code === 'IN') {
                    if (data.city && data.region_code) {
                        setLocation(`${data.city}, ${data.region_code}`);
                    } else if (data.city) {
                        setLocation(data.city);
                    } else {
                        setLocation('Mumbai, MH'); // Default Indian fallback
                    }
                } else {
                    setLocation('Mumbai, MH'); // Default Indian fallback if not in India
                }
            } catch (err) {
            console.error('Could not fetch location data:', err);
            setLocation('Mumbai, MH'); // Default Indian fallback on error
            setHour(new Date().getHours().toString()); // Fallback to local machine hour
        }
    };

    fetchLocation();
}, []);

useEffect(() => {
    const fetchUserData = async () => {
        try {
            const [meRes, scoreRes] = await Promise.all([
                api.get('/users/me'),
                api.get('/fraud/score')
            ]);
            setProfile(meRes.data);
            setRiskScore(scoreRes.data);
        } catch (err) {
            console.error("Failed to fetch user data", err);
        } finally {
            setLoading(false);
        }
    };
    fetchUserData();
}, []);

const handlePredict = async (e) => {
    e.preventDefault();
    setPredicting(true);
    setPrediction(null);
    try {
        // Generate basic hardware telemetry footprint
        const rawFingerprint = `${navigator.userAgent}-${window.screen.width}x${window.screen.height}-${navigator.language}`;
        const device_fingerprint = btoa(rawFingerprint).substring(0, 32);

        const formData = new FormData();
        formData.append('amount', parseFloat(amount));
        formData.append('age', parseInt(age));
        formData.append('hour', parseInt(hour));
        formData.append('category', category);
        formData.append('device_fingerprint', device_fingerprint);
        formData.append('location', location);
        formData.append('description', description);
        formData.append('merchant', merchant);

        if (documentImage) {
            formData.append('document_image', documentImage);
        }

        const res = await api.post('/fraud/predict', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        setPrediction(res.data);
    } catch (err) {
        console.error(err);
        alert("Prediction failed: " + (err.response?.data?.detail || err.message));
    } finally {
        setPredicting(false);
    }
};

if (loading) return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>Loading Identity Profile...</div>;

return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>

        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '40px' }} className="animate-fade-in">
            <div>
                <h1 className="text-gradient" style={{ fontSize: '2rem', marginBottom: '8px' }}>Security Cortex</h1>
                <p className="text-muted">Welcome back, {profile?.email}</p>
            </div>
            <button onClick={logout} className="btn btn-glass" style={{ padding: '8px 16px', fontSize: '0.85rem' }}>
                <LogOut size={16} /> Disconnect
            </button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '40px' }}>

            {/* Status Card */}
            <div className="glass-panel stat-card animate-fade-in delay-100">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                        <p className="label">Current Threat Level</p>
                        <h2 className="stat-value">{riskScore?.status || 'UNKNOWN'}</h2>
                    </div>
                    <div style={{
                        background: riskScore?.status === 'LOW_RISK' ? 'var(--success-glow)' : 'var(--warning)',
                        padding: '12px',
                        borderRadius: '50%',
                        color: riskScore?.status === 'LOW_RISK' ? 'var(--success)' : 'white'
                    }}>
                        {riskScore?.status === 'LOW_RISK' ? <ShieldCheck size={28} /> : <ShieldAlert size={28} />}
                    </div>
                </div>
                <div style={{ marginTop: '16px' }}>
                    <div style={{ width: '100%', height: '6px', background: 'var(--bg-darker)', borderRadius: '3px', overflow: 'hidden' }}>
                        <div style={{
                            width: `${riskScore?.risk_score || 0}%`,
                            height: '100%',
                            background: riskScore?.status === 'LOW_RISK' ? 'var(--success)' : 'var(--warning)',
                            transition: 'width 1s ease-in-out'
                        }} />
                    </div>
                    <p className="text-muted" style={{ fontSize: '0.8rem', marginTop: '8px', textAlign: 'right' }}>
                        {riskScore?.risk_score}% Risk Coefficient
                    </p>
                </div>
            </div>

        </div>

        {/* Manual Check Form */}
        <h2 style={{ marginBottom: '24px', fontSize: '1.5rem' }} className="animate-fade-in delay-200">Run Threat Simulation</h2>

        <div className="glass-panel animate-fade-in delay-200" style={{ padding: '32px' }}>
            <form onSubmit={handlePredict} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>

                <div>
                    <label className="label">Amount ($)</label>
                    <div style={{ position: 'relative' }}>
                        <DollarSign size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                        <input type="number" step="0.01" required className="input-field" style={{ paddingLeft: '36px' }} value={amount} onChange={e => setAmount(e.target.value)} />
                    </div>
                </div>

                <div>
                    <label className="label">Hour (0-23)</label>
                    <div style={{ position: 'relative' }}>
                        <Clock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                        <input type="number" required className="input-field" style={{ paddingLeft: '36px' }} value={hour} onChange={e => setHour(e.target.value)} />
                    </div>
                </div>

                <div>
                    <label className="label">Category</label>
                    <div style={{ position: 'relative' }}>
                        <CreditCard size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                        <select
                            required
                            className="input-field"
                            style={{ paddingLeft: '36px', appearance: 'none' }}
                            value={category}
                            onChange={e => setCategory(e.target.value)}
                        >
                            <option value="groceries">Groceries</option>
                            <option value="electronics">Electronics</option>
                            <option value="health">Health & Pharmacy</option>
                            <option value="shopping">Retail & Shopping</option>
                            <option value="travel">Travel & Transport</option>
                            <option value="entertainment">Entertainment</option>
                            <option value="dining">Dining & Food</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label className="label">Location (Auto-Detected via IP)</label>
                    <div style={{ position: 'relative' }}>
                        <MapPin size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
                        <input type="text" required readOnly title="Location is securely pulled from IP context" className="input-field" style={{ paddingLeft: '36px', background: 'rgba(255,255,255,0.05)', cursor: 'not-allowed', color: 'var(--text-muted)' }} value={location} />
                    </div>
                </div>

                <div style={{ gridColumn: '1 / -1' }}>
                    <label className="label">Merchant</label>
                    <input type="text" required className="input-field" style={{ padding: '12px' }} value={merchant} onChange={e => setMerchant(e.target.value)} />
                </div>

                <div style={{ gridColumn: '1 / -1' }}>
                    <label className="label">Description / Context</label>
                    <textarea required className="input-field" style={{ minHeight: '80px', padding: '12px' }} value={description} onChange={e => setDescription(e.target.value)} />
                </div>

                <div style={{ gridColumn: '1 / -1' }}>
                    <label className="label">Evidence Document / Receipt (Optional)</label>
                    <input type="file" className="input-field" accept="image/*" onChange={e => setDocumentImage(e.target.files[0])} style={{ padding: '14px' }} />
                    <small className="text-muted" style={{ display: 'block', marginTop: '5px' }}>Upload receipts or IDs here. The visual CNN engine will analyze it.</small>
                </div>

                <div style={{ gridColumn: '1 / -1', marginTop: '10px' }}>
                    <button type="submit" className="btn btn-primary" disabled={predicting}>
                        {predicting ? 'Evaluating Neural Matrix...' : 'Run Diagnostics'}
                    </button>
                </div>
            </form>

            {prediction && (
                <div className="animate-fade-in" style={{
                    marginTop: '32px',
                    padding: '24px',
                    borderRadius: 'var(--radius-md)',
                    background: 'rgba(0,0,0,0.2)',
                    borderLeft: `4px solid ${prediction.is_fraud ? 'var(--error)' : 'var(--success)'}`
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <p className="label" style={{ marginBottom: '4px' }}>Neural Network Verdict</p>
                            <h3 style={{ fontSize: '1.8rem', color: prediction.is_fraud ? 'var(--error)' : 'var(--success)' }}>
                                {prediction.status}
                            </h3>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <p className="text-muted" style={{ fontSize: '0.85rem' }}>Confidence Score</p>
                            <p style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{(prediction.probability * 100).toFixed(2)}%</p>
                        </div>
                    </div>
                </div>
            )}

        </div>
    </div>
);
};

export default UserDashboard;
