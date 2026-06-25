import React, { useState, useEffect } from 'react';
import { Filter, Search } from 'lucide-react';
import { getLeads } from '../api/client';
import socket from '../api/socket';
import LoadingSpinner from '../components/LoadingSpinner';
import UrgencyBadge from '../components/UrgencyBadge';
import LeadDetailModal from '../components/LeadDetailModal';
import { formatDate } from '../utils/helpers';

const LeadManagement = () => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [selectedLead, setSelectedLead] = useState(null);

  const categories = ['all', 'urgent', 'sales', 'support', 'spam'];

  useEffect(() => {
    fetchLeads(filter);
  }, [filter]);

  const fetchLeads = async (category) => {
    try {
      setLoading(true);
      const res = await getLeads(category);
      const allLeads = res.data || [];
      const limit = category === 'all' ? 40 : 30;
      setLeads(allLeads.slice(0, limit));
    } catch (error) {
      console.error("Failed to fetch leads", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const handleNewLead = (newLead) => {
      setLeads((prevLeads) => {
        // If we are filtering and the new lead doesn't match the current filter, ignore it
        if (filter !== 'all' && newLead.category !== filter) {
          return prevLeads;
        }
        
        // Prevent duplicates just in case
        if (prevLeads.find(l => l.id === newLead.id)) return prevLeads;
        
        return [newLead, ...prevLeads];
      });
    };

    socket.on('new_lead', handleNewLead);
    return () => {
      socket.off('new_lead', handleNewLead);
    };
  }, [filter]);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Header + Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl md:text-[32px] font-bold text-heading leading-tight">Lead Management</h1>
          <p className="text-sm md:text-[15px] text-muted mt-1">View and filter all processed leads.</p>
        </div>
        
        {/* Segmented Filter Control */}
        <div className="flex items-center gap-1 bg-surface-card p-1 rounded-2xl border border-border shadow-card overflow-x-auto">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`px-3.5 md:px-4 py-2 rounded-xl text-xs md:text-sm font-medium capitalize transition-all duration-200 whitespace-nowrap ${
                filter === cat 
                  ? 'bg-primary text-white shadow-sm' 
                  : 'text-muted hover:text-heading hover:bg-gray-50'
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
        /* Empty State */
        <div className="text-center py-20 bg-surface-card rounded-card border border-border shadow-card">
          <div className="w-16 h-16 rounded-2xl bg-surface-bg flex items-center justify-center mx-auto mb-4">
            <Search className="w-7 h-7 text-gray-300" />
          </div>
          <h3 className="text-lg font-semibold text-heading">No leads found</h3>
          <p className="text-muted text-sm mt-1.5 max-w-sm mx-auto">Try changing your filter category or process a new lead through the AI Assistant.</p>
        </div>
      ) : (
        /* Lead Cards */
        <div className="grid grid-cols-1 gap-4">
          {leads.map((lead) => (
            <div key={lead.id} onClick={() => setSelectedLead(lead)} className="bg-surface-card rounded-card border border-border p-5 md:p-6 shadow-card hover:shadow-card-hover hover:border-gray-300 transition-all duration-200 cursor-pointer">
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-5">
                <div className="flex-1 space-y-3.5">
                  {/* Badges Row */}
                  <div className="flex flex-wrap items-center gap-2.5">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-body border border-border capitalize">
                      {lead.category}
                    </span>
                    <UrgencyBadge level={lead.urgency} />
                    <div className="text-sm text-muted">
                      {formatDate(lead.created_at)}
                    </div>
                  </div>
                  
                  {/* AI Summary */}
                  <div>
                    <h4 className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">AI Summary</h4>
                    <p className="text-heading text-sm leading-relaxed bg-surface-bg p-3.5 rounded-2xl border border-border">
                      {lead.summary || 'No summary generated.'}
                    </p>
                  </div>
                </div>
                
                {/* Original Message */}
                <div className="md:w-1/3 md:pl-6 md:border-l border-divider">
                  <h4 className="text-xs font-semibold text-muted uppercase tracking-wider mb-2">Original Message</h4>
                  <p className="text-body text-sm line-clamp-4 italic leading-relaxed">
                    "{lead.message}"
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {selectedLead && (
        <LeadDetailModal lead={selectedLead} onClose={() => setSelectedLead(null)} />
      )}
    </div>
  );
};

export default LeadManagement;
