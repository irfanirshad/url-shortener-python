import React, { useState } from 'react';
import { ExternalLink } from 'lucide-react';
import { RefreshButton } from './RefreshButton';

interface URLEntry {
  originalUrl: string;
  shortUrl: string;
  clicks: number;
}

export function Dashboard() {
  const [urls, setUrls] = useState<URLEntry[]>([
    {
      originalUrl: 'https://example.com/very/long/url/that/needs/to/be/shortened',
      shortUrl: 'https://short.url/abc123',
      clicks: 42
    }
  ]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      // Update URLs here with fresh data
    } catch (error) {
      console.error('Failed to refresh URLs:', error);
    } finally {
      setIsRefreshing(false);
    }
  };

  const truncateUrl = (url: string, maxLength: number = 30) => {
    return url.length > maxLength ? `${url.substring(0, maxLength)}...` : url;
  };

  return (
    <div className="glass-card rounded-2xl overflow-hidden">
      <div className="p-4 glossy-black flex justify-between items-center">
        <h2 className="text-xl font-bold glow-text">Recent Public URLs</h2>
        <RefreshButton onRefresh={handleRefresh} isLoading={isRefreshing} />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/10">
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Original URL
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Shortened URL
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Clicks
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {urls.map((entry, index) => (
              <tr key={index} className="hover:bg-white/5 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 hover:text-custom-white">
                  {truncateUrl(entry.originalUrl)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <a
                    href={entry.shortUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-custom-light-gray glow-text hover:text-custom-white flex items-center gap-1"
                    >
                    {entry.shortUrl}
                    <ExternalLink size={14} />
                  </a>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                  {entry.clicks}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}