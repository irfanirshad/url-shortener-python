// import { defineConfig } from 'vite';
// import react from '@vitejs/plugin-react';

// export default defineConfig({
//   plugins: [react()],
//   build: {
//     outDir: 'dist', // Ensure this matches the Dockerfile output directory
//     sourcemap: false, // Disable sourcemaps for production
//   },
//   optimizeDeps: {
//     exclude: ['lucide-react'],
//   },
//   server: {
//     host: '0.0.0.0', // Allows the server to accept requests from outside the container
//     port: 4173, // Matches the port exposed in Dockerfile and docker-compose
//     strictPort: true, // Prevents the server from randomly assigning a different port
//   },
//   base: '/', // Ensures all assets are correctly served from the root path
// });


// import { defineConfig } from 'vite';
// import react from '@vitejs/plugin-react';

// export default defineConfig({
//   plugins: [react()],
//   build: {
//     outDir: 'dist', // Ensure this matches the Dockerfile output directory
//     sourcemap: false, // Disable sourcemaps for production
//   },
//   optimizeDeps: {
//     exclude: ['lucide-react'],
//   },
//   server: {
//     host: '0.0.0.0', // Allows the server to accept requests from outside the container
//     port: 4173, // Matches the port exposed in Dockerfile and docker-compose
//     strictPort: true, // Prevents the server from randomly assigning a different port
//     // Add custom middleware to block requests to /<short_url>
//     proxy: {
//       '/{short_url:[a-zA-Z0-9]+}': {
//         target: 'http://localhost:5000', // Backend service
//         changeOrigin: true,
//         rewrite: (path) => path.replace(/^\/{short_url:[a-zA-Z0-9]+}/, ''),
//       },
//     },
//   },
//   base: '/', // Ensures all assets are correctly served from the root path
// });


import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist', // Ensure this matches the Dockerfile output directory
    sourcemap: false, // Disable sourcemaps for production
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    host: '0.0.0.0', // Allows the server to accept requests from outside the container
    port: 4173, // Matches the port exposed in Dockerfile and docker-compose
    strictPort: true, // Prevents the server from randomly assigning a different port
    proxy: {
      // Proxy HTTP requests
      '/{short_url:[a-zA-Z0-9]+}': {
        target: 'http://localhost:5000', // Backend service
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/{short_url:[a-zA-Z0-9]+}/, ''),
      },
      // Proxy WebSocket requests
      '/socket.io': {
        target: 'ws://localhost:5000', // WebSocket backend service
        ws: true, // Enable WebSocket proxying
        changeOrigin: true,
      },
    },
  },
  base: '/', // Ensures all assets are correctly served from the root path
});