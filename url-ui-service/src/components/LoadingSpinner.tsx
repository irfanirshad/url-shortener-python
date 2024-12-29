import React from 'react';

export function LoadingSpinner() {
  return (
    <div className="loader" role="status">
      <span className="sr-only">Loading...</span>
    </div>
  );
}