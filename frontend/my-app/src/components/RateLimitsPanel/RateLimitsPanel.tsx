import React, { useState, useEffect } from 'react';
// Remove the direct hook import
// import { useRateLimits } from '../../hooks/useRateLimits'; 
import { useRateLimitContext } from '../../contexts/RateLimitContext'; // Import the context hook
import { formatTimeRemaining, RateLimitInfo } from '../../services/rateLimitService';

interface RateLimitsPanelProps {
  className?: string;
}

// Create a threshold helper for warnings
const WARNING_THRESHOLDS = {
  high: { percent: 10, message: 'Critical' },
  medium: { percent: 30, message: 'Low' },
};

// Cooldown period for refresh button in milliseconds
const REFRESH_COOLDOWN_MS = 30000; // 30 seconds

const RateLimitsPanel: React.FC<RateLimitsPanelProps> = ({ className = '' }) => {
  // Use the context hook instead of the direct hook
  const { rateLimits, isLoading, error, refetch } = useRateLimitContext(); 
  const [refreshing, setRefreshing] = useState<boolean>(false);
  
  // Add state for tracking cooldown
  const [lastRefreshTime, setLastRefreshTime] = useState<number>(0);
  const [cooldownRemaining, setCooldownRemaining] = useState<number>(0);
  
  // Track cooldown timer
  useEffect(() => {
    // If there's no active cooldown, don't set up the timer
    if (cooldownRemaining <= 0) return;
    
    // Set up interval to update the remaining cooldown time
    const intervalId = setInterval(() => {
      const remaining = Math.max(0, REFRESH_COOLDOWN_MS - (Date.now() - lastRefreshTime));
      setCooldownRemaining(remaining);
    }, 1000); // Update every second
    
    // Clean up the interval when the component unmounts or cooldown ends
    return () => clearInterval(intervalId);
  }, [lastRefreshTime, cooldownRemaining]);
  
  // Add visual indicator when data refreshes
  const handleRefresh = async () => {
    // Update last refresh time and set cooldown
    const now = Date.now();
    setLastRefreshTime(now);
    setCooldownRemaining(REFRESH_COOLDOWN_MS);
    
    setRefreshing(true);
    await refetch(true);
    
    // Keep the refresh animation visible for at least 500ms
    setTimeout(() => {
      setRefreshing(false);
    }, 500);
  };
  
  // Compute whether the refresh button should be disabled
  const isRefreshDisabled = isLoading || cooldownRemaining > 0;
  
  // Format the cooldown time for display
  const formatCooldown = (): string => {
    if (cooldownRemaining <= 0) return '';
    const seconds = Math.ceil(cooldownRemaining / 1000);
    return `${seconds}s`;
  };
  
  // Add visual effect on load and when data changes
  useEffect(() => {
    if (!isLoading && rateLimits) {
      setRefreshing(true);
      const timer = setTimeout(() => {
        setRefreshing(false);
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [rateLimits, isLoading]);

  const getStatusColor = (info: RateLimitInfo, limitType: string): string => {
    if (!info || info.error) return 'text-gray-400';
    
    const [limit] = info.limit.split('/');
    const total = parseInt(limit, 10);
    const percentRemaining = (info.remaining / total) * 100;
    
    // Higher limits for concept generation get more conservative thresholds
    if (limitType.includes('concept') && percentRemaining <= 20) {
      return 'text-red-500';
    } else if (limitType.includes('concept') && percentRemaining <= 50) {
      return 'text-yellow-500';
    }
    
    // Standard thresholds for other endpoints
    if (percentRemaining <= 10) {
      return 'text-red-500';
    } else if (percentRemaining <= 30) {
      return 'text-yellow-500';
    }
    
    return 'text-green-500';
  };

  // Helper to check if a warning should be shown
  const shouldShowWarning = (info: RateLimitInfo | undefined, name: string): { show: boolean; level: 'high' | 'medium'; message: string } | null => {
    if (!info || info.error) return null;
    
    const [limit] = info.limit.split('/');
    const total = parseInt(limit, 10);
    
    if (!total) return null;
    
    const percentRemaining = (info.remaining / total) * 100;
    
    // Higher limits for concept generation get more conservative thresholds
    if (name.includes('concept')) {
      if (percentRemaining <= 20) {
        return { show: true, level: 'high', message: `${info.remaining} uses left` };
      } else if (percentRemaining <= 50) {
        return { show: true, level: 'medium', message: `${info.remaining} uses left` };
      }
    } else {
      // Standard thresholds for other endpoints
      if (percentRemaining <= WARNING_THRESHOLDS.high.percent) {
        return { show: true, level: 'high', message: `${info.remaining} uses left` };
      } else if (percentRemaining <= WARNING_THRESHOLDS.medium.percent) {
        return { show: true, level: 'medium', message: `${info.remaining} uses left` };
      }
    }
    
    return null;
  };

  const renderCircularProgress = (percentage: number, colorClass: string) => {
    // Circle parameters
    const radius = 14;
    const strokeWidth = 2.5;
    const normalizedRadius = radius - strokeWidth;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;
    
    return (
      <div className="relative h-8 w-8 flex items-center justify-center">
        <svg height={radius * 2} width={radius * 2} className="absolute">
          <circle
            stroke="#e2e8f0" // Light gray background
            fill="transparent"
            strokeWidth={strokeWidth}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          <circle
            stroke="currentColor"
            fill="transparent"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference + ' ' + circumference}
            style={{ strokeDashoffset }}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            className={colorClass}
            transform={`rotate(-90 ${radius} ${radius})`}
          />
        </svg>
        <span className="text-xs font-semibold">{Math.round(percentage)}%</span>
      </div>
    );
  };

  const renderRateLimitItem = (info: RateLimitInfo | undefined, name: string, title: string) => {
    if (!info) return null;

    const [limit, period] = info.limit.split('/');
    const total = parseInt(limit, 10);
    const percentRemaining = info.error ? 0 : (info.remaining / total) * 100;
    const statusColor = getStatusColor(info, name);
    const warning = shouldShowWarning(info, name);
    
    return (
      <div className="mb-3">
        <div className="flex items-center">
          <div className={statusColor}>
            {renderCircularProgress(percentRemaining, statusColor)}
          </div>
          
          <div className="ml-2 flex-1">
            <div className="flex justify-between items-center">
              <span className="font-medium text-gray-700 text-sm">{title}</span>
              <span className={`font-semibold text-sm ${statusColor}`}>
                {info.error ? 'Error' : `${info.remaining}/${limit}`}
              </span>
            </div>
            
            {!info.error && (
              <div className="text-xs text-gray-500">
                Resets in {formatTimeRemaining(info.reset_after)}
              </div>
            )}
          </div>
        </div>

        {/* Proactive warning message */}
        {warning && (
          <div className={`mt-1 px-2 py-1 rounded-sm text-xs font-medium flex items-center
            ${warning.level === 'high' ? 'bg-red-50 text-red-600' : 'bg-yellow-50 text-yellow-600'}`}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span>
              <strong>{WARNING_THRESHOLDS[warning.level].message}:</strong> {warning.message}
            </span>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`rounded-lg rounded-r-none p-4 bg-white/95 backdrop-blur-sm shadow-md border border-r-0 border-gray-100 ${className} ${refreshing ? 'border-indigo-300 bg-indigo-50/80 transition-colors duration-300 ease-in-out' : ''}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-base font-semibold text-gray-800">API Usage Limits</h3>
        
        <div className="flex items-center">
          {cooldownRemaining > 0 && (
            <span className="text-xs text-gray-500 mr-2">
              {formatCooldown()}
            </span>
          )}
          
          <button 
            onClick={handleRefresh}
            disabled={isRefreshDisabled}
            className={`p-1 rounded-full hover:bg-indigo-50 text-indigo-600 transition-colors ${isRefreshDisabled ? 'opacity-50 cursor-not-allowed' : ''}`}
            title={cooldownRemaining > 0 ? `Refresh available in ${formatCooldown()}` : "Refresh limits"}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="flex justify-center items-center py-4">
          <div className="animate-spin h-5 w-5 border-2 border-indigo-500 border-t-transparent rounded-full"></div>
          <span className="ml-2 text-sm text-gray-600">Loading...</span>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 text-red-600 p-2 rounded-md text-xs">
          <div className="font-semibold">Error loading limits</div>
          <div className="mt-0.5">{error}</div>
        </div>
      )}
      
      {!isLoading && !error && rateLimits && (
        <div>
          <div className="space-y-3">
            {renderRateLimitItem(
              rateLimits.limits.generate_concept, 
              'generate_concept', 
              'Concept Generation'
            )}
            
            {renderRateLimitItem(
              rateLimits.limits.store_concept, 
              'store_concept', 
              'Concept Storage'
            )}
            
            {renderRateLimitItem(
              rateLimits.limits.refine_concept, 
              'refine_concept', 
              'Concept Refinement'
            )}
            
            {renderRateLimitItem(
              rateLimits.limits.svg_conversion, 
              'svg_conversion', 
              'SVG Conversion'
            )}
          </div>
          
          <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
            <div className="flex items-center">
              <span className="font-medium">ID:</span>
              <span className="ml-1 font-mono">{rateLimits.user_identifier}</span>
            </div>
            <div className="mt-1 flex items-center text-xs">
              <span className="font-medium">Default:</span>
              <span className="ml-1">{rateLimits.default_limits.join(', ')}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RateLimitsPanel; 