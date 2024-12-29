import React from 'react';
import { RefreshCw } from 'lucide-react';
import { LoadingSpinner } from './LoadingSpinner';

interface RefreshButtonProps {
  onRefresh: () => Promise<void>;
  isLoading: boolean;
}

export function RefreshButton({ onRefresh, isLoading }: RefreshButtonProps) {
  return (
    <button
      onClick={onRefresh}
      disabled={isLoading}
      className="p-2 hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      aria-label="Refresh list"
    >
      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <RefreshCw size={20} className="text-teal-500" />
      )}
    </button>
  );
}