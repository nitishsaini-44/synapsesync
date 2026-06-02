import React from 'react';

const StatCard = ({ title, value, icon, color }) => {
  // Mapping color prop to tailwind classes
  const colorMap = {
    primary: 'bg-primary/20 text-primary',
    success: 'bg-success/20 text-success',
    warning: 'bg-warning/20 text-warning',
    danger: 'bg-danger/20 text-danger',
  };

  const iconBg = colorMap[color] || colorMap.primary;

  return (
    <div className="bg-dark-surface rounded-xl p-4 md:p-6 border border-slate-700/50 shadow-sm hover:shadow-md hover:border-slate-600 transition-all duration-300 group">
      <div className="flex items-center justify-between gap-2">
        <div className="space-y-1 md:space-y-2 min-w-0">
          <p className="text-xs md:text-sm font-medium text-slate-400 truncate">{title}</p>
          <p className="text-2xl md:text-3xl font-bold text-slate-100">{value}</p>
        </div>
        <div className={`p-2 md:p-3 rounded-lg md:rounded-xl flex-shrink-0 ${iconBg} transition-transform duration-300 group-hover:scale-110`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default StatCard;
