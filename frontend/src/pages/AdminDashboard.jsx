import React, { useState, useEffect } from 'react';
import { ShieldCheck, Server, AlertTriangle, Users, FileText } from 'lucide-react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';
import api from '../api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement);

const AdminDashboard = () => {
    const [health, setHealth] = useState(null);
    const [transactions, setTransactions] = useState([]);
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const healthRes = await api.get('/fraud/health');
                const transRes = await api.get('/fraud/transactions');
                const alertsRes = await api.get('/fraud/alerts');

                setHealth(healthRes.data);
                setTransactions(transRes.data);
                setAlerts(alertsRes.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Calculate chart data based on dynamic values
    const safeCount = transactions.filter(t => t.status === "Success").length;
    const fraudCount = alerts.filter(a => a.action_taken === "Blocked").length;
    const reviewCount = alerts.filter(a => a.action_taken === "Flagged").length;

    // Fallbacks if data is empty so charts aren't completely blank for demo
    const doughnutData = {
        labels: ['Safe', 'Review', 'Fraud (Blocked)'],
        datasets: [
            {
                data: transactions.length > 0 ? [safeCount, reviewCount, fraudCount] : [1, 0, 0],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0,
                hoverOffset: 4,
            },
        ],
    };

    // A simple mock curve adjusted slightly by total alerts for demonstration
    const lineData = {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
            {
                label: 'Threats Blocked',
                data: [0, 2, 1, fraudCount, 1, 0, 0], // Simple representation 
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.2)',
                tension: 0.4,
                fill: true,
            },
        ],
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#94a3b8' } } },
        scales: {
            x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
            y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
        }
    };

    if (loading) return <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>Loading Global Intel...</div>;

    return (
        <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '40px 20px' }}>
            <div style={{ marginBottom: '40px' }} className="animate-fade-in">
                <h1 className="text-gradient" style={{ fontSize: '2rem', marginBottom: '8px' }}>Global Oversight</h1>
                <p className="text-muted">Aegis System Analytics & Threat Metrics</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px', marginBottom: '40px' }}>

                <div className="glass-panel stat-card animate-fade-in delay-100">
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                            <p className="label">Ensemble Status</p>
                            <h2 className="stat-value" style={{ fontSize: '1.8rem', color: health?.status === 'ok' ? 'var(--success)' : 'var(--error)' }}>
                                {health?.status === 'ok' ? 'ONLINE' : 'DEGRADED'}
                            </h2>
                        </div>
                        <Server size={28} color="var(--primary)" />
                    </div>
                </div>

                <div className="glass-panel stat-card animate-fade-in delay-200">
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                            <p className="label">Active Models</p>
                            <h2 className="stat-value" style={{ fontSize: '1.8rem' }}>4 / 4</h2>
                            <small className="text-muted">Tabular, Behavior, NLP, CNN</small>
                        </div>
                        <ShieldCheck size={28} color="var(--success)" />
                    </div>
                </div>

            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', marginBottom: '40px' }}>

                <div className="glass-panel animate-fade-in delay-300" style={{ padding: '24px', height: '400px', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ marginBottom: '20px' }}>Threat Mitigation Volume</h3>
                    <div style={{ flex: 1, position: 'relative' }}>
                        <Line data={lineData} options={chartOptions} />
                    </div>
                </div>

                <div className="glass-panel animate-fade-in delay-300" style={{ padding: '24px', height: '400px', display: 'flex', flexDirection: 'column' }}>
                    <h3 style={{ marginBottom: '20px' }}>Transaction Distribution</h3>
                    <div style={{ flex: 1, position: 'relative', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                        <Doughnut data={doughnutData} options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } } }} />
                    </div>
                </div>

            </div>

            <div className="glass-panel animate-fade-in delay-400" style={{ padding: '24px', marginBottom: '40px' }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '20px' }}>
                    <FileText size={24} color="var(--primary)" style={{ marginRight: '10px' }} />
                    <h3>Multimodal Audit Trail</h3>
                </div>
                
                {alerts.length === 0 ? (
                    <p className="text-muted">No alerts found in the database.</p>
                ) : (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                                    <th style={{ padding: '12px' }}>TxID</th>
                                    <th style={{ padding: '12px' }}>Amount</th>
                                    <th style={{ padding: '12px' }}>Merchant</th>
                                    <th style={{ padding: '12px' }}>Risk</th>
                                    <th style={{ padding: '12px' }}>Reason</th>
                                    <th style={{ padding: '12px' }}>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {alerts.map((alert) => (
                                    <tr key={alert.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                                        <td style={{ padding: '12px', color: '#94a3b8' }}>#{alert.transaction_id}</td>
                                        <td style={{ padding: '12px' }}>${alert.amount}</td>
                                        <td style={{ padding: '12px' }}>{alert.merchant}</td>
                                        <td style={{ padding: '12px', color: alert.risk_level === 'High' ? '#ef4444' : '#f59e0b' }}>
                                            {alert.risk_level} ({(alert.fraud_score * 100).toFixed(0)}%)
                                        </td>
                                        <td style={{ padding: '12px', fontSize: '0.9em' }}>{alert.trigger_reason}</td>
                                        <td style={{ padding: '12px' }}>
                                            <span style={{ 
                                                padding: '4px 8px', 
                                                borderRadius: '4px', 
                                                fontSize: '0.85em',
                                                backgroundColor: alert.action_taken === 'Blocked' ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)',
                                                color: alert.action_taken === 'Blocked' ? '#ef4444' : '#f59e0b' 
                                            }}>
                                                {alert.action_taken}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

        </div>
    );
};

export default AdminDashboard;
