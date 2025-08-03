// import React, { useState, useEffect } from 'react';
// import { ExternalLink } from 'lucide-react';
// import { RefreshButton } from './RefreshButton';
// import io, { Socket } from 'socket.io-client';


// interface URLEntry {
//   originalUrl: string;
//   shortUrl: string;
//   clicks: number;
// }

// export function Dashboard() {
//   const [urls, setUrls] = useState<URLEntry[]>([]);
//   const [isRefreshing, setIsRefreshing] = useState(false);

//  const [socketStatus, setSocketStatus] = useState('Disconnected');  // Add socket status state
//  const [timeTicks, setTimeTicks] = useState('');  // Add time ticks state
// //  const { socketStatus, timeTicks } = useWebSocket('https://www.bigshort.one');

//   // WebSocket connection
//   useEffect(() => {
//       const socket: Socket = io('https://www.bigshort.one', {
//       reconnection: true, // Enable reconnection
//       reconnectionAttempts: 5, // Number of reconnection attempts
//       reconnectionDelay: 1000, // Delay between reconnection attempts
//     });

//     socket.on('connect', () => {
//       setSocketStatus('Connected');
//     });

//     socket.on('disconnect', () => {
//       setSocketStatus('Disconnected');
//     });

//     socket.on('push-message', (data: { time: string }) => {
//       setTimeTicks(data.time);
//     });

//     return () => {
//       socket.disconnect(); // Cleanup on unmount
//     };
//   }, []);




//   const fetchUrls = async () => {
//     try {
//       const response = await fetch('https://bigshort.one/api/v1/urls');
//       const data = await response.json();
      
//       // Map the response to fit your component's structure
//       const urlData = data.urls.map((entry: any) => ({
//         originalUrl: entry.original_url,
//         shortUrl: entry.short_code,
//         clicks: entry.clicks,
//       }));

//       setUrls(urlData); // Update the state with the new URL data
//     } catch (error) {
//       console.error('Failed to fetch URLs:', error);
//     }
//   };

//   const handleRefresh = async () => {
//     setIsRefreshing(true);
//     await fetchUrls(); // Fetch the updated URLs
//     setIsRefreshing(false);
//   };

//   const truncateUrl = (url: string, maxLength: number = 30) => {
//     return url.length > maxLength ? `${url.substring(0, maxLength)}...` : url;
//   };

//   useEffect(() => {
//     fetchUrls(); // Initial fetch when the component mounts
//   }, []);

//   return (
//     <div className="glass-card rounded-2xl overflow-hidden">
//       <div className="p-4 glossy-black flex justify-between items-center">
//         <h2 className="text-xl font-bold glow-text">Recent Public URLs</h2>
//         <RefreshButton onRefresh={handleRefresh} isLoading={isRefreshing} />
//       </div>
//       <div className="overflow-x-auto">
//         <table className="w-full">
//           <thead>
//             <tr className="border-b border-white/10">
//               <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
//                 Original URL
//               </th>
//               <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
//                 Shortened URL
//               </th>
//               <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
//                 Clicks
//               </th>
//             </tr>
//           </thead>
//           <tbody className="divide-y divide-white/10">
//             {urls.map((entry, index) => (
//               <tr key={index} className="hover:bg-white/5 transition-colors">
//                 <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 hover:text-custom-white">
//                   {truncateUrl(entry.originalUrl)} {/* Truncate long URLs */}
//                 </td>
//                 <td className="px-6 py-4 whitespace-nowrap text-sm">
//                   <a
//                   href={`https://${entry.shortUrl}`} 
//                   target="_blank"
//                     rel="noopener noreferrer"
//                     className="text-custom-light-gray glow-text hover:text-custom-white flex items-center gap-1"
//                   >
//                     {entry.shortUrl}
//                     <ExternalLink size={14} />
//                   </a>
//                 </td>
//                 <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
//                   {entry.clicks}
//                 </td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>



//       {/* WebSocket Status Modal */}
//       <div className="fixed bottom-4 right-4 bg-custom-black p-4 rounded-lg shadow-lg">
//         <div className="text-sm text-custom-white">
//           <p>WebSocket: <span className={socketStatus === 'Connected' ? 'text-green-500' : 'text-red-500'}>{socketStatus}</span></p>
//           <p>Time Tick: <span className="text-custom-blue">{timeTicks}</span></p>
//         </div>
//       </div>
//     </div>
//   );
// }

