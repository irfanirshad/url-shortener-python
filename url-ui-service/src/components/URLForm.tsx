import React, { useState, useEffect } from 'react';
import { Copy, Link2 } from 'lucide-react';
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
  const [copySuccess, setCopySuccess] = useState(false); // State to track copy status

  // Clear custom URL when switching modes
  useEffect(() => {
    if (!isCustomMode) {
      setCustomUrl('');
    }
  }, [isCustomMode]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCopySuccess(false); // Reset copy status on new submission
    setIsLoading(true);

    try {
      const apiUrl = 'https://bigshort.one/api/shorten-url'; // replace with your API endpoint
      const requestData = isCustomMode ? { url, customUrl, isPublic } : { url, isPublic };

      const response = await axios.post(apiUrl, requestData);
      setShortenedURL(response.data.shortenedUrl);
    } catch (err) {
      setError('Failed to shorten URL. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shortenedURL);
      setCopySuccess(true); // Update copy success state
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* URL input field */}
      <div className="relative">
        <input
          type="url"
          value={isCustomMode ? customUrl : url} // Use custom URL when in custom mode
          onChange={(e) => isCustomMode ? setCustomUrl(e.target.value) : setUrl(e.target.value)}
          placeholder={isCustomMode ? "Enter your custom URL" : "Paste your URL here"}
          className={`w-full px-4 py-3 glossy-black rounded-lg outline-none transition-all
            ${isCustomMode 
              ? 'focus:ring-2 focus:ring-orange-500/50'
              : 'focus:ring-2 focus:ring-teal-500/50'
            }
            text-white font-mono placeholder-gray-500`}
          required
        />
        <Link2 className="absolute right-3 top-3 text-gray-500" size={20} />
      </div>

      {/* Show the custom URL input field if isCustomMode is true */}
      {isCustomMode && (
        <div className="relative">
          <input
            type="url"
            value={customUrl}
            onChange={(e) => setCustomUrl(e.target.value)}
            placeholder="Enter your custom URL"
            className="w-full px-4 py-3 glossy-black rounded-lg outline-none transition-all focus:ring-2 focus:ring-orange-500/50 text-white font-mono placeholder-gray-500"
          />
        </div>
      )}

      {/* Checkbox for public URL */}
      {isCustomMode && (
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
      )}

      {/* Display error message if any */}
      {error && (
        <p className="text-red-500 text-sm">{error}</p>
      )}

      {/* Submit button */}
      <button
        type="submit"
        disabled={isLoading}
        className={`w-full py-3 rounded-lg font-bold text-white transition-all 
          ${isCustomMode
            ? 'bg-gradient-to-r from-custom-grey to-custom-light-gray hover:from-custom-dark-gray hover:to-custom-grey'
            : 'bg-gradient-to-r from-custom-dark-gray to-custom-grey hover:from-custom-grey hover:to-custom-dark-gray'
          }
          disabled:opacity-50 disabled:cursor-not-allowed 
          shadow-lg hover:shadow-2xl hover:shadow-custom-glow`}
      >
        {isLoading ? <LoadingSpinner /> : 'Shorten URL'}
      </button>

      {/* Display shortened URL if available */}
      {shortenedURL && (
        <div className="glossy-black rounded-lg p-4 space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-white font-mono">{shortenedURL}</p>
            <button
              onClick={copyToClipboard}
              className="p-2 hover:bg-white/5 rounded-lg transition-colors"
            >
              <Copy size={20} className={isCustomMode ? 'text-violet-500' : 'text-teal-500'} />
            </button>
          </div>
          {copySuccess && (
            <p className="text-green-500 text-sm mt-2">Link copied to clipboard!</p>
          )}
        </div>
      )}
    </form>
  );
}
