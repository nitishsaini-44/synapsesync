import React, { useState, useEffect } from 'react';
import { Filter, Search } from 'lucide-react';
import { getLeads } from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import UrgencyBadge from '../components/UrgencyBadge';

const LeadManagement = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  const categories = ['all', 'urgent', 'sales', 'support', 'spam'];

  useEffect(() => {
    fetchLeads(filter);
  }, [filter]);

  const fetchLeads = async (category) => {
    try {
      setLoading(true);
      const res = await getLeads(category);
      setLeads(res.data || []);
    } catch (error) {
      console.error("Failed to fetch leads", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-100">Lead Management</h2>
          <p className="text-slate-400">View and filter all processed leads.</p>
        </div>
        
        {/* Filters */}
        <div className="flex items-center space-x-2 bg-dark-surface p-1 rounded-lg border border-slate-700/50 shadow-sm overflow-x-auto">
          <Filter size={16} className="text-slate-500 ml-2 hidden sm:block" />
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-all whitespace-nowrap ${
                filter === cat 
                  ? 'bg-primary text-white shadow-md' 
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="py-20"><LoadingSpinner text="Loading leads..." /></div>
      ) : leads.length === 0 ? (
        <div className="text-center py-20 bg-dark-surface rounded-xl border border-slate-700/50">
          <Search className="w-12 h-12 text-slate-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-300">No leads found</h3>
          <p className="text-slate-500 mt-1">Try changing your filter category or process a new lead.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {leads.map((lead) => (
            <div key={lead.id} className="bg-dark-surface rounded-xl border border-slate-700/50 p-6 shadow-sm hover:border-slate-600 transition-colors">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                <div className="flex-1 space-y-3">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="px-3 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                      {lead.category}
                    </span>
                    <UrgencyBadge level={lead.urgency} />
                    <span className="text-xs text-slate-500">
                      {new Date(lead.created_at).toLocaleString()}
                    </span>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-semibold text-slate-300 mb-1">AI Summary</h4>
                    <p className="text-slate-100 text-sm leading-relaxed bg-slate-800/30 p-3 rounded-lg border border-slate-700/30">
                      {lead.summary || 'No summary generated.'}
                    </p>
                  </div>
                </div>
                
                <div className="md:w-1/3 md:pl-6 md:border-l border-slate-700/50">
                  <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Original Message</h4>
                  <p className="text-slate-400 text-sm line-clamp-4 italic">
                    "{lead.message}"
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LeadManagement;
