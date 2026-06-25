import React from 'react';
import { Clock } from 'lucide-react';
import UrgencyBadge from './UrgencyBadge';
import { formatDate } from '../utils/helpers';

const RecentSummaries = ({ summaries, onItemClick }) => {
  if (!summaries || summaries.length === 0) {
    return (
      <div className="text-center py-12 text-muted bg-surface-card rounded-card border border-border">
        <svg className="w-12 h-12 mx-auto mb-3 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
        </svg>
        <p className="text-sm font-medium text-body">No recent summaries</p>
        <p className="text-xs text-muted mt-1">Summaries will appear here once you process messages.</p>
      </div>
    );
  }

  return (
    <>
      {/* Desktop Table — card-style with rounded headers */}
      <div className="hidden md:block bg-surface-card rounded-card border border-border shadow-card overflow-hidden">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="bg-divider/60">
              <th className="px-6 py-4 font-medium text-xs uppercase tracking-wider text-muted">Message Snapshot</th>
              <th className="px-6 py-4 font-medium text-xs uppercase tracking-wider text-muted">Category</th>
              <th className="px-6 py-4 font-medium text-xs uppercase tracking-wider text-muted">Urgency</th>
              <th className="px-6 py-4 font-medium text-xs uppercase tracking-wider text-muted">Date</th>
            </tr>
          </thead>
          <tbody>
            {summaries.map((item, index) => (
              <tr 
                key={item.id}
                onClick={() => onItemClick && onItemClick(item)}
                className={`hover:bg-gray-50/80 transition-colors cursor-pointer ${
                  index !== summaries.length - 1 ? 'border-b border-divider' : ''
                }`}
              >
                <td className="px-6 py-4 max-w-xs truncate text-heading font-medium text-sm">
                  {item.message}
                </td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-body border border-border capitalize">
                    {item.category}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <UrgencyBadge level={item.urgency} />
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-muted">
                  {formatDate(item.created_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card Layout */}
      <div className="md:hidden space-y-3">
        {summaries.map((item) => (
          <div
            key={item.id}
            onClick={() => onItemClick && onItemClick(item)}
            className="bg-surface-card rounded-card border border-border p-4 space-y-3 shadow-card cursor-pointer hover:shadow-card-hover transition-all duration-200"
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-body border border-border capitalize">
                  {item.category}
                </span>
                <UrgencyBadge level={item.urgency} />
              </div>
              <span className="text-xs text-muted flex items-center gap-1.5 mt-1 sm:mt-0">
                <Clock size={12} />
                {formatDate(item.created_at)}
              </span>
            </div>
            <p className="text-sm text-heading leading-relaxed line-clamp-2">
              {item.message}
            </p>
          </div>
        ))}
      </div>
    </>
  );
};

export default RecentSummaries;
