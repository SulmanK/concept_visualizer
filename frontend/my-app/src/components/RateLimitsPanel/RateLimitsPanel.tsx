import React from 'react';
import { useRateLimits } from '../../hooks/useRateLimits';
import { formatTimeRemaining, RateLimitInfo } from '../../services/rateLimitService';

interface RateLimitsPanelProps {
  className?: string;
}

const RateLimitsPanel: React.FC<RateLimitsPanelProps> = ({ className = '' }) => {
  const { rateLimits, isLoading, error, refetch } = useRateLimits();

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
    
    return (
      <div className="mb-3 flex items-center">
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
    );
  };

  return (
    <div className={`rounded-lg rounded-r-none p-4 bg-white/95 backdrop-blur-sm shadow-md border border-r-0 border-gray-100 ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-base font-semibold text-gray-800">API Usage Limits</h3>
        <button 
          onClick={refetch} 
          className="p-1 rounded-full hover:bg-indigo-50 text-indigo-600 transition-colors"
          title="Refresh limits"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
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