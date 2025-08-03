import React, { useState } from 'react';
import { Copy, Link2, ExternalLink } from 'lucide-react';
import axios from 'axios';
import { LoadingSpinner } from './LoadingSpinner';

interface URLFormProps {
  isCustomMode: boolean;
}

export function URLForm({ isCustomMode }: URLFormProps) {
  const [url, setUrl] = useState('');
  const [customUrl, setCustomUrl] = useState('');
  const [isPublic, setIsPublic] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [shortenedURL, setShortenedURL] = useState('');
  const [error, setError] = useState('');
  const [copySuccess, setCopySuccess] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCopySuccess(false);
    setSuccessMessage(''); // Reset success message before submitting
    setIsLoading(true);

    try {
      const apiUrl = 'https://bigshort.one/api/v1/shorten';
      const requestData = isCustomMode
        ? { url, customUrl, isPublic }
        : { url, isPublic };

      const response = await axios.post(apiUrl, requestData, {
        headers: { 'Content-Type': 'application/json' },
      });

      if (response.data.success) {
        setShortenedURL(response.data.shortUrl); // Set the shortened URL
        setSuccessMessage('URL successfully shortened!'); // Set success message
      } else {
        setError('Failed to shorten URL. Please try again.');
      }
    } catch (err) {
      setError('Failed to shorten URL. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async (e: React.MouseEvent) => {
    e.preventDefault(); // Prevent the form submission or other default actions
  
    try {
      await navigator.clipboard.writeText(shortenedURL);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000); // Reset the success message after 2 seconds
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Original URL input field - always visible */}
      <div className="relative">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Paste your URL here"
          className={`w-full px-4 py-3 glossy-black rounded-lg outline-none transition-all
            ${isCustomMode ? 'focus:ring-2 focus:ring-orange-500/50' : 'focus:ring-2 focus:ring-teal-500/50'}
            text-white font-mono placeholder-gray-500`}
          required
        />
        <Link2 className="absolute right-3 top-3 text-gray-500" size={20} />
      </div>

      {/* Custom URL input field - only visible in custom mode */}
      {isCustomMode && (
        <div className="relative">
          <input
            type="text"
            value={customUrl}
            onChange={(e) => setCustomUrl(e.target.value)}
            placeholder="Enter custom URL"
            className="w-full px-4 py-3 glossy-black rounded-lg outline-none transition-all focus:ring-2 focus:ring-orange-500/50 text-white font-mono placeholder-gray-500"
          />
        </div>
      )}

      {/* Public URL checkbox - always visible */}
      <label className="flex items-center space-x-2 text-gray-300">
        <input
          type="checkbox"
          checked={isPublic}
          onChange={(e) => setIsPublic(e.target.checked)}
          className={`w-4 h-4 rounded border-gray-600
            ${isCustomMode ? 'text-violet-500 focus:ring-violet-500' : 'text-teal-500 focus:ring-teal-500'}
            bg-[#121212]`}
        />
        <span>Make this URL public on the dashboard</span>
      </label>

      {error && <p className="text-red-500 text-sm">{error}</p>}
      {successMessage && <p className="text-green-500 text-sm">{successMessage}</p>} {/* Success message */}

      <button
        type="submit"
        disabled={isLoading}
        className={`w-full py-3 rounded-lg font-bold text-white transition-all
          ${isCustomMode
            ? 'bg-gradient-to-r from-custom-grey to-custom-light-gray hover:from-custom-dark-gray hover:to-custom-grey'
            : 'bg-gradient-to-r from-custom-dark-gray to-custom-grey hover:from-custom-grey hover:to-custom-dark-gray'}
          disabled:opacity-50 disabled:cursor-not-allowed
          shadow-lg hover:shadow-2xl hover:shadow-custom-glow`}
      >
        {isLoading ? <LoadingSpinner /> : 'Shorten URL'}
      </button>

      {shortenedURL && (
        <div className="glass-card rounded-lg p-6 space-y-4 border border-white/10">
          <h3 className="text-lg font-semibold text-white">Your shortened URL is ready! 🎉</h3>
          <div className="glossy-black rounded-lg p-4">
            <div className="flex items-center justify-between">
              <a
               href={shortenedURL.startsWith('http') ? shortenedURL : `https://${shortenedURL}`}
                target="_blank"
                rel="noopener noreferrer"
                className="text-white font-mono hover:text-teal-400 transition-colors flex items-center gap-2"
              >
                {shortenedURL}
                <ExternalLink size={16} />
              </a>
              <button
                onClick={(e) => copyToClipboard(e)}
                className="p-2 hover:bg-white/5 rounded-lg transition-colors"
              >
                <Copy size={20} className={isCustomMode ? 'text-violet-500' : 'text-teal-500'} />
              </button>
            </div>
            {copySuccess && <p className="text-green-500 text-sm mt-2">Link copied to clipboard!</p>}
          </div>
        </div>
      )}
    </form>
  );
}
