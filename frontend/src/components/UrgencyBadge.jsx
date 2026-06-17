import React from 'react';

const UrgencyBadge = ({ level }) => {
  const normLevel = (level || 'low').toLowerCase();
  
  let colorClass = 'bg-gray-50 text-muted border-gray-200';
  let dotClass = 'bg-muted';
  
  if (normLevel === 'high') {
    colorClass = 'bg-error-light text-error border-error/15';
    dotClass = 'bg-error';
  } else if (normLevel === 'medium') {
    colorClass = 'bg-warning-light text-warning border-warning/20';
    dotClass = 'bg-warning';
  } else if (normLevel === 'low') {
    colorClass = 'bg-success-light text-success border-success/15';
    dotClass = 'bg-success';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium border ${colorClass}`}>
      <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${dotClass}`}></span>
      <span className="capitalize">{normLevel}</span>
    </span>
  );
};

export default UrgencyBadge;
