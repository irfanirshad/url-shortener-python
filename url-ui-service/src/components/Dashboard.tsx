
import React, { useState, useEffect, useRef } from 'react';
import { ExternalLink, Activity, BarChart3, Users } from 'lucide-react';
import { RefreshButton } from './RefreshButton';

interface URLEntry {
  originalUrl: string;
  shortUrl: string;
  clicks: number;
}

interface Stats {
  timestamp: string;
  total_urls: number;
  total_clicks: number;
  active_users: number;
  urls_created_today: number;
  top_domain: string;
  avg_clicks_per_url: number;
  server_status: string;
}

interface ActivityItem {
  timestamp: string;
  activity: string;
  user_agent: string;
  location: string;
  id: string;
}

interface URLUpdate {
  timestamp: string;
  type: 'new_url' | 'click_update';
  original_url: string;
  short_code: string;
  clicks: number;
  created_at: string;
}

export function Dashboard() {
  const [urls, setUrls] = useState<URLEntry[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // SSE states
  const [stats, setStats] = useState<Stats | null>(null);
  const [activities, setActivities] = useState<ActivityItem[]>([]);
  const [urlUpdates, setUrlUpdates] = useState<URLUpdate[]>([]);
  const [sseStatus, setSseStatus] = useState({
    stats: 'Disconnected',
    activity: 'Disconnected',
    urlUpdates: 'Disconnected'
  });

  // SSE refs to manage connections
  const statsEventSourceRef = useRef<EventSource | null>(null);
  const activityEventSourceRef = useRef<EventSource | null>(null);
  const urlUpdatesEventSourceRef = useRef<EventSource | null>(null);

  // SSE connection setup
  useEffect(() => {
    const baseUrl = 'https://bigshort.one'; // Your backend URL

    // Stats SSE connection
    const setupStatsSSE = () => {
      const statsEventSource = new EventSource(`${baseUrl}/api/v1/sse/stats`);
      
      statsEventSource.onopen = () => {
        console.log('Stats SSE connected');
        setSseStatus(prev => ({ ...prev, stats: 'Connected' }));
      };

      statsEventSource.onmessage = (event) => {
        try {
          const data: Stats = JSON.parse(event.data);
          setStats(data);
        } catch (error) {
          console.error('Error parsing stats data:', error);
        }
      };

      statsEventSource.onerror = (error) => {
        console.error('Stats SSE error:', error);
        setSseStatus(prev => ({ ...prev, stats: 'Error' }));
      };

      statsEventSourceRef.current = statsEventSource;
    };

    // Activity SSE connection
    const setupActivitySSE = () => {
      const activityEventSource = new EventSource(`${baseUrl}/api/v1/sse/activity`);
      
      activityEventSource.onopen = () => {
        console.log('Activity SSE connected');
        setSseStatus(prev => ({ ...prev, activity: 'Connected' }));
      };

      activityEventSource.onmessage = (event) => {
        try {
          const data: ActivityItem = JSON.parse(event.data);
          setActivities(prev => [data, ...prev.slice(0, 9)]); // Keep last 10 activities
        } catch (error) {
          console.error('Error parsing activity data:', error);
        }
      };

      activityEventSource.onerror = (error) => {
        console.error('Activity SSE error:', error);
        setSseStatus(prev => ({ ...prev, activity: 'Error' }));
      };

      activityEventSourceRef.current = activityEventSource;
    };

    // URL Updates SSE connection
    const setupUrlUpdatesSSE = () => {
      const urlUpdatesEventSource = new EventSource(`${baseUrl}/api/v1/sse/url-updates`);
      
      urlUpdatesEventSource.onopen = () => {
        console.log('URL Updates SSE connected');
        setSseStatus(prev => ({ ...prev, urlUpdates: 'Connected' }));
      };

      urlUpdatesEventSource.onmessage = (event) => {
        try {
          const data: URLUpdate = JSON.parse(event.data);
          setUrlUpdates(prev => [data, ...prev.slice(0, 4)]); // Keep last 5 updates
        } catch (error) {
          console.error('Error parsing URL update data:', error);
        }
      };

      urlUpdatesEventSource.onerror = (error) => {
        console.error('URL Updates SSE error:', error);
        setSseStatus(prev => ({ ...prev, urlUpdates: 'Error' }));
      };

      urlUpdatesEventSourceRef.current = urlUpdatesEventSource;
    };

    // Setup all SSE connections
    setupStatsSSE();
    setupActivitySSE();
    setupUrlUpdatesSSE();

    // Cleanup function
    return () => {
      if (statsEventSourceRef.current) {
        statsEventSourceRef.current.close();
      }
      if (activityEventSourceRef.current) {
        activityEventSourceRef.current.close();
      }
      if (urlUpdatesEventSourceRef.current) {
        urlUpdatesEventSourceRef.current.close();
      }
    };
  }, []);

  const fetchUrls = async () => {
    try {
      const response = await fetch('https://bigshort.one/api/v1/urls');
      const data = await response.json();
      
      const urlData = data.urls.map((entry: any) => ({
        originalUrl: entry.original_url,
        shortUrl: entry.short_code,
        clicks: entry.clicks,
      }));

      setUrls(urlData);
    } catch (error) {
      console.error('Failed to fetch URLs:', error);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await fetchUrls();
    setIsRefreshing(false);
  };

  const truncateUrl = (url: string, maxLength: number = 30) => {
    return url.length > maxLength ? `${url.substring(0, maxLength)}...` : url;
  };

  useEffect(() => {
    fetchUrls();
  }, []);

  return (
    <div className="space-y-6">
      {/* Real-time Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="glass-card p-4 rounded-xl">
            <div className="flex items-center gap-3">
              <BarChart3 className="text-blue-400" size={24} />
              <div>
                <p className="text-sm text-gray-400">Total URLs</p>
                <p className="text-2xl font-bold text-white">{stats.total_urls}</p>
              </div>
            </div>
          </div>
          
          <div className="glass-card p-4 rounded-xl">
            <div className="flex items-center gap-3">
              <Activity className="text-green-400" size={24} />
              <div>
                <p className="text-sm text-gray-400">Total Clicks</p>
                <p className="text-2xl font-bold text-white">{stats.total_clicks}</p>
              </div>
            </div>
          </div>
          
          <div className="glass-card p-4 rounded-xl">
            <div className="flex items-center gap-3">
              <Users className="text-purple-400" size={24} />
              <div>
                <p className="text-sm text-gray-400">Active Users</p>
                <p className="text-2xl font-bold text-white">{stats.active_users}</p>
              </div>
            </div>
          </div>
          
          <div className="glass-card p-4 rounded-xl">
            <div className="flex items-center gap-3">
              <ExternalLink className="text-orange-400" size={24} />
              <div>
                <p className="text-sm text-gray-400">URLs Today</p>
                <p className="text-2xl font-bold text-white">{stats.urls_created_today}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* URLs Table */}
        <div className="lg:col-span-2">
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
                          href={`https://${entry.shortUrl}`} 
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
        </div>

        {/* Activity Feed */}
        <div className="space-y-6">
          {/* Real-time Activity */}
          <div className="glass-card rounded-2xl overflow-hidden">
            <div className="p-4 glossy-black">
              <h3 className="text-lg font-bold glow-text">Live Activity</h3>
            </div>
            <div className="p-4 max-h-80 overflow-y-auto">
              {activities.map((activity, index) => (
                <div key={activity.id} className="mb-3 p-3 bg-white/5 rounded-lg">
                  <p className="text-sm text-white">{activity.activity}</p>
                  <p className="text-xs text-gray-400 mt-1">
                    {activity.location} • {new Date(activity.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* URL Updates */}
          <div className="glass-card rounded-2xl overflow-hidden">
            <div className="p-4 glossy-black">
              <h3 className="text-lg font-bold glow-text">URL Updates</h3>
            </div>
            <div className="p-4 max-h-60 overflow-y-auto">
              {urlUpdates.map((update, index) => (
                <div key={index} className="mb-3 p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-1 text-xs rounded ${
                      update.type === 'new_url' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                    }`}>
                      {update.type === 'new_url' ? 'NEW' : 'CLICK'}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(update.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-white">{truncateUrl(update.original_url, 25)}</p>
                  <p className="text-xs text-gray-400">{update.clicks} clicks</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* SSE Status Modal */}
      <div className="fixed bottom-4 right-4 bg-custom-black p-4 rounded-lg shadow-lg border border-white/10">
        <div className="text-sm text-custom-white">
          <h4 className="font-bold mb-2">Connection Status</h4>
          <div className="space-y-1">
            <p>Stats: <span className={getStatusColor(sseStatus.stats)}>{sseStatus.stats}</span></p>
            <p>Activity: <span className={getStatusColor(sseStatus.activity)}>{sseStatus.activity}</span></p>
            <p>Updates: <span className={getStatusColor(sseStatus.urlUpdates)}>{sseStatus.urlUpdates}</span></p>
          </div>
          {stats && (
            <p className="mt-2 text-xs text-gray-400">
              Last update: {new Date(stats.timestamp).toLocaleTimeString()}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'Connected':
      return 'text-green-500';
    case 'Error':
      return 'text-red-500';
    default:
      return 'text-yellow-500';
  }
}