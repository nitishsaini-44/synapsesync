import React from 'react';
import { Loader2 } from 'lucide-react';

const LoadingSpinner = ({ text = "Processing..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-6 space-y-4 text-primary">
      <Loader2 className="w-8 h-8 animate-spin" />
      <p className="text-sm font-medium text-slate-400 animate-pulse">{text}</p>
    </div>
  );
};

export default LoadingSpinner;
