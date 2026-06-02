import React from 'react';

const UrgencyBadge = ({ level }) => {
  const normLevel = (level || 'low').toLowerCase();
  
  let colorClass = 'bg-slate-500/20 text-slate-400 border-slate-500/30';
  let dotClass = 'bg-slate-400';
  
  if (normLevel === 'high') {
    colorClass = 'bg-danger/10 text-danger border-danger/20';
    dotClass = 'bg-danger';
  } else if (normLevel === 'medium') {
    colorClass = 'bg-warning/10 text-warning border-warning/20';
    dotClass = 'bg-warning';
  } else if (normLevel === 'low') {
    colorClass = 'bg-success/10 text-success border-success/20';
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
