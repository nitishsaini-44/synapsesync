import React from 'react';
import UrgencyBadge from './UrgencyBadge';

const RecentSummaries = ({ summaries }) => {
  if (!summaries || summaries.length === 0) {
    return (
      <div className="text-center py-8 text-slate-400 bg-dark-surface rounded-xl border border-slate-700">
        No recent summaries found.
      </div>
    );
  }

  return (
    <>
      {/* Desktop Table — hidden on small screens */}
      <div className="hidden md:block overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-left text-sm text-slate-300">
          <thead className="bg-dark-surface text-xs uppercase text-slate-400 border-b border-slate-700">
            <tr>
              <th className="px-6 py-4 font-medium">Message Snapshot</th>
              <th className="px-6 py-4 font-medium">Category</th>
              <th className="px-6 py-4 font-medium">Urgency</th>
              <th className="px-6 py-4 font-medium">Date</th>
            </tr>
          </thead>
          <tbody className="bg-dark-surface divide-y divide-slate-700/50">
            {summaries.map((item) => (
              <tr key={item.id} className="hover:bg-dark-surfaceHover transition-colors">
                <td className="px-6 py-4 max-w-xs truncate text-slate-200">
                  {item.message}
                </td>
                <td className="px-6 py-4 capitalize text-slate-300">
                  {item.category}
                </td>
                <td className="px-6 py-4">
                  <UrgencyBadge level={item.urgency} />
                </td>
                <td className="px-6 py-4 text-slate-400 whitespace-nowrap">
                  {new Date(item.created_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Mobile Card Layout — shown only on small screens */}
      <div className="md:hidden space-y-3">
        {summaries.map((item) => (
          <div
            key={item.id}
            className="bg-dark-surface rounded-xl border border-slate-700/50 p-4 space-y-3"
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700 capitalize">
                  {item.category}
                </span>
                <UrgencyBadge level={item.urgency} />
              </div>
              <span className="text-xs text-slate-500 whitespace-nowrap">
                {new Date(item.created_at).toLocaleDateString()}
              </span>
            </div>
            <p className="text-sm text-slate-200 line-clamp-2">
              {item.message}
            </p>
          </div>
        ))}
      </div>
    </>
  );
};

export default RecentSummaries;
