import React, { useEffect, useState } from 'react';
import { Activity, AlertTriangle, Briefcase, HelpCircle } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import StatCard from '../components/StatCard';
import RecentSummaries from '../components/RecentSummaries';
import LeadDetailModal from '../components/LeadDetailModal';
import { getAnalytics } from '../api/client';
import socket from '../api/socket';
import LoadingSpinner from '../components/LoadingSpinner';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState(null);

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

  useEffect(() => {
    const handleNewLead = (newLead) => {
      setStats((prevStats) => {
        if (!prevStats) return prevStats;
        
        // Dynamically increment counters
        const categoryKey = `${newLead.category}_count`;
        
        return {
          ...prevStats,
          total_processed: prevStats.total_processed + 1,
          [categoryKey]: (prevStats[categoryKey] || 0) + 1,
          recent_summaries: [newLead, ...prevStats.recent_summaries].slice(0, 10) // Keep top 10
        };
      });
    };

    socket.on('new_lead', handleNewLead);
    
    return () => {
      socket.off('new_lead', handleNewLead);
    };
  }, []);

  if (loading) {
    return <div className="h-full flex items-center justify-center"><LoadingSpinner text="Loading Dashboard..." /></div>;
  }

  if (!stats) {
    return (
      <div className="text-center py-20">
        <div className="bg-surface-card rounded-card border border-border p-10 max-w-md mx-auto shadow-card">
          <svg className="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
          </svg>
          <p className="text-heading font-medium">Unable to load dashboard</p>
          <p className="text-muted text-sm mt-1">Ensure the backend is running and try again.</p>
        </div>
      </div>
    );
  }

  const chartData = [
    { name: 'Urgent', value: stats.urgent_count, color: '#F05656' }, /* error */
    { name: 'Sales', value: stats.sales_count, color: '#D72660' },  /* primary */
    { name: 'Support', value: stats.support_count, color: '#3FA46A' }, /* success */
    { name: 'Spam', value: stats.spam_count, color: '#888888' },    /* muted */
  ].filter(item => item.value > 0);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl md:text-[32px] font-bold text-heading leading-tight">Analytics Overview</h1>
        <p className="text-sm md:text-[15px] text-muted mt-1">Track your AI automated workflow performance.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
        <StatCard title="Total Processed" value={stats.total_processed} icon={<Activity size={24} />} color="primary" />
        <StatCard title="Urgent Requests" value={stats.urgent_count} icon={<AlertTriangle size={24} />} color="danger" />
        <StatCard title="Sales Leads" value={stats.sales_count} icon={<Briefcase size={24} />} color="success" />
        <StatCard title="Support Tickets" value={stats.support_count} icon={<HelpCircle size={24} />} color="warning" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Card */}
        <div className="lg:col-span-1 bg-surface-card rounded-card p-6 border border-border shadow-card">
          <h3 className="text-lg font-semibold text-heading mb-5">Category Distribution</h3>
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
                    contentStyle={{ 
                      backgroundColor: '#FFFFFF', 
                      borderColor: '#EAEAEA', 
                      color: '#111111', 
                      borderRadius: '14px',
                      boxShadow: '0 4px 16px rgba(0,0,0,.06)',
                      padding: '10px 14px',
                      fontSize: '13px',
                    }}
                    itemStyle={{ color: '#555555' }}
                  />
                  <Legend 
                    wrapperStyle={{ fontSize: '13px', color: '#888888' }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-muted">
              <svg className="w-10 h-10 mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 6a7.5 7.5 0 1 0 7.5 7.5h-7.5V6Z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 10.5H21A7.5 7.5 0 0 0 13.5 3v7.5Z" />
              </svg>
              <p className="text-sm">No data available for chart.</p>
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-lg font-semibold text-heading">Recent Activity</h3>
          <RecentSummaries summaries={stats.recent_summaries} onItemClick={(item) => setSelectedLead(item)} />
        </div>
      </div>

      {/* Detail Modal */}
      {selectedLead && (
        <LeadDetailModal lead={selectedLead} onClose={() => setSelectedLead(null)} />
      )}
    </div>
  );
};

export default Dashboard;
