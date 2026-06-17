import React from 'react';

const StatCard = ({ title, value, icon, color }) => {
  // Mapping color prop to the new design system
  const colorMap = {
    primary: {
      iconBg: 'bg-primary-light',
      iconText: 'text-primary',
    },
    success: {
      iconBg: 'bg-success-light',
      iconText: 'text-success',
    },
    warning: {
      iconBg: 'bg-warning-light',
      iconText: 'text-warning',
    },
    danger: {
      iconBg: 'bg-error-light',
      iconText: 'text-error',
    },
  };

  const styles = colorMap[color] || colorMap.primary;

  return (
    <div className="bg-surface-card rounded-card p-5 md:p-6 border border-border shadow-card hover:shadow-card-hover transition-all duration-200 group">
      <div className="flex items-center justify-between gap-3">
        <div className="space-y-1.5 min-w-0">
          <p className="text-[13px] font-medium text-muted tracking-wide">{title}</p>
          <p className="text-2xl md:text-3xl font-bold text-heading">{value}</p>
        </div>
        <div className={`p-2.5 md:p-3 rounded-2xl flex-shrink-0 ${styles.iconBg} ${styles.iconText} transition-transform duration-200 group-hover:scale-105`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default StatCard;
