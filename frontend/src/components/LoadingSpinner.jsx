import React from 'react';

const LoadingSpinner = ({ text = "Processing..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-6 space-y-5">
      {/* Skeleton loader blocks */}
      <div className="w-full max-w-sm space-y-3">
        <div className="skeleton h-4 w-3/4 rounded-lg"></div>
        <div className="skeleton h-4 w-full rounded-lg"></div>
        <div className="skeleton h-4 w-5/6 rounded-lg"></div>
        <div className="skeleton h-10 w-1/2 rounded-xl mt-4"></div>
      </div>
      <p className="text-sm font-medium text-muted">{text}</p>
    </div>
  );
};

export default LoadingSpinner;
