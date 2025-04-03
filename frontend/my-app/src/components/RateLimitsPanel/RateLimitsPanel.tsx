import React, { useState } from 'react';
import { useRateLimits } from '../../hooks/useRateLimits';
import { formatTimeRemaining, RateLimitInfo } from '../../services/rateLimitService';

interface RateLimitsPanelProps {
  className?: string;
}

const RateLimitsPanel: React.FC<RateLimitsPanelProps> = ({ className = '' }) => {
  const { rateLimits, isLoading, error, refetch } = useRateLimits();
  const [isExpanded, setIsExpanded] = useState(false);

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const getProgressBarColor = (info: RateLimitInfo, limitType: string): string => {
    if (!info || info.error) return 'bg-gray-300';
    
    const [limit] = info.limit.split('/');
    const total = parseInt(limit, 10);
    const percentRemaining = (info.remaining / total) * 100;
    
    // Higher limits for concept generation get more conservative thresholds
    if (limitType.includes('concept') && percentRemaining <= 20) {
      return 'bg-red-500';
    } else if (limitType.includes('concept') && percentRemaining <= 50) {
      return 'bg-yellow-500';
    }
    
    // Standard thresholds for other endpoints
    if (percentRemaining <= 10) {
      return 'bg-red-500';
    } else if (percentRemaining <= 30) {
      return 'bg-yellow-500';
    }
    
    return 'bg-green-500';
  };

  const renderRateLimitItem = (info: RateLimitInfo | undefined, name: string, title: string) => {
    if (!info) return null;

    const [limit, period] = info.limit.split('/');
    const total = parseInt(limit, 10);
    const percentRemaining = info.error ? 0 : (info.remaining / total) * 100;
    const progressColor = getProgressBarColor(info, name);
    
    return (
      <div className="mb-3">
        <div className="flex justify-between text-sm mb-1">
          <span className="font-medium text-indigo-700">{title}</span>
          <span className="text-gray-600">
            {info.error ? 'Error' : `${info.remaining}/${limit} remaining`}
          </span>
        </div>
        <div className="h-2 bg-gray-200 rounded overflow-hidden">
          <div 
            className={`h-full ${progressColor} rounded`} 
            style={{ width: `${percentRemaining}%` }}
          />
        </div>
        {!info.error && (
          <div className="text-xs text-gray-500 mt-1">
            Resets in {formatTimeRemaining(info.reset_after)}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`rounded-lg p-4 bg-white/90 backdrop-blur-sm shadow ${className}`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold text-indigo-900">API Usage Limits</h3>
        <div className="flex gap-2">
          <button 
            onClick={refetch} 
            className="p-1 rounded hover:bg-indigo-100 text-indigo-700"
            title="Refresh"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
          <button 
            onClick={toggleExpanded} 
            className="p-1 rounded hover:bg-indigo-100 text-indigo-700"
            title={isExpanded ? "Collapse" : "Expand"}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path 
                strokeLinecap="round" 
                strokeLinejoin="round" 
                strokeWidth={2} 
                d={isExpanded 
                  ? "M5 15l7-7 7 7" 
                  : "M19 9l-7 7-7-7"}
              />
            </svg>
          </button>
        </div>
      </div>

      {isLoading && <div className="text-gray-500">Loading rate limits...</div>}
      
      {error && <div className="text-red-500">Error: {error}</div>}
      
      {!isLoading && !error && rateLimits && (
        <div>
          {/* Always show the most important limits */}
          {renderRateLimitItem(
            rateLimits.limits.generate_concept, 
            'generate_concept', 
            'Concept Generation'
          )}
          
          {isExpanded && (
            <>
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
                rateLimits.limits.get_concepts, 
                'get_concepts', 
                'Retrieving Concepts'
              )}
              
              {renderRateLimitItem(
                rateLimits.limits.sessions, 
                'sessions', 
                'Session Operations'
              )}
              
              {renderRateLimitItem(
                rateLimits.limits.svg_conversion, 
                'svg_conversion', 
                'SVG Conversion'
              )}
              
              <div className="mt-4 text-xs text-gray-500">
                <div>User ID: {rateLimits.user_identifier}</div>
                <div className="mt-1">
                  Default limits: {rateLimits.default_limits.join(', ')}
                </div>
              </div>
            </>
          )}
          
          {!isExpanded && (
            <div className="mt-2 text-xs text-indigo-500 cursor-pointer hover:underline" onClick={toggleExpanded}>
              Click to show all rate limits
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RateLimitsPanel; 