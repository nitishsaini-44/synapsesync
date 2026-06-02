import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, Briefcase, HelpCircle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import StatCard from '../components/StatCard';
import RecentSummaries from '../components/RecentSummaries';
import { getAnalytics } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await getAnalytics();
      setStats(response.data);
    } catch (error) {
      console.error("Failed to load analytics", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="h-full flex items-center justify-center"><LoadingSpinner text="Loading Dashboard..." /></div>;
  }

  if (!stats) {
    return <div className="text-center text-slate-400 mt-10">Failed to load dashboard data. Ensure backend is running.</div>;
  }

  const chartData = [
    { name: 'Urgent', value: stats.urgent_count, color: '#ef4444' },
    { name: 'Sales', value: stats.sales_count, color: '#3b82f6' },
    { name: 'Support', value: stats.support_count, color: '#10b981' },
    { name: 'Spam', value: stats.spam_count, color: '#6b7280' },
  ].filter(item => item.value > 0);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h2 className="text-xl md:text-2xl font-bold text-slate-100">Analytics Overview</h2>
        <p className="text-sm md:text-base text-slate-400">Track your AI automated workflow performance.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-6">
        <StatCard title="Total Processed" value={stats.total_processed} icon={<Activity size={24} />} color="primary" />
        <StatCard title="Urgent Requests" value={stats.urgent_count} icon={<AlertTriangle size={24} />} color="danger" />
        <StatCard title="Sales Leads" value={stats.sales_count} icon={<Briefcase size={24} />} color="success" />
        <StatCard title="Support Tickets" value={stats.support_count} icon={<HelpCircle size={24} />} color="warning" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Area */}
        <div className="lg:col-span-1 bg-dark-surface rounded-xl p-6 border border-slate-700/50 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-200 mb-4">Category Distribution</h3>
          {chartData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                    stroke="none"
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9', borderRadius: '8px' }}
                    itemStyle={{ color: '#f1f5f9' }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-500 text-sm">
              No data available for chart.
            </div>
          )}
        </div>

        {/* Recent Summaries Area */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-semibold text-slate-200">Recent Activity</h3>
          <RecentSummaries summaries={stats.recent_summaries} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
