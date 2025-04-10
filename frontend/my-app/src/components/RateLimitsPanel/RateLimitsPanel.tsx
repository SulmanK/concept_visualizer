import React, { useState, useEffect, useCallback } from 'react';
import { 
  Box, 
  Divider, 
  LinearProgress, 
  Tooltip, 
  Typography,
  Paper,
  Button,
  useTheme
} from '@mui/material';
import { formatTimeRemaining, RateLimitCategory } from '../../services/rateLimitService';
import { useRateLimitsQuery } from '../../hooks/useRateLimitsQuery';

const COOLDOWN_DURATION = 5; // 5 seconds

interface RateLimitsPanelProps {
  /** Title to display at the top of the panel */
  title?: string;
  /** Whether to display the refresh button */
  showRefresh?: boolean;
  /** Function to close the panel (optional) */
  onClose?: () => void;
  /** CSS className for additional styling */
  className?: string;
}

/**
 * Component for displaying current rate limits with visual indicators
 */
export const RateLimitsPanel: React.FC<RateLimitsPanelProps> = ({
  title = 'API Rate Limits',
  showRefresh = true,
  onClose,
  className
}) => {
  const theme = useTheme();
  const [refreshCooldown, setRefreshCooldown] = useState(0);
  
  // Use React Query hook 
  const { 
    data: rateLimits, 
    isLoading, 
    error,
    refetch,
    decrementLimit
  } = useRateLimitsQuery();
  
  // Handle refresh button click with cooldown
  const handleRefresh = useCallback(() => {
    if (refreshCooldown > 0) return;
    
    console.log('RateLimitsPanel: Manual refresh requested');
    
    // Call the enhanced refetch function that forces a true refresh
    refetch().then(result => {
      if (result.isSuccess) {
        console.log('RateLimitsPanel: Manual refresh completed successfully', result.data);
      } else {
        console.error('RateLimitsPanel: Manual refresh failed', result.error);
      }
    });
    
    setRefreshCooldown(COOLDOWN_DURATION);
  }, [refreshCooldown, refetch]);
  
  // Cooldown timer for refresh button
  useEffect(() => {
    if (refreshCooldown <= 0) return;
    
    const interval = setInterval(() => {
      setRefreshCooldown(prev => Math.max(0, prev - 1));
    }, 1000);
    
    return () => clearInterval(interval);
  }, [refreshCooldown]);
  
  // Helper function to render a rate limit item
  const renderRateLimitItem = (
    label: string, 
    category: RateLimitCategory
  ) => {
    if (!rateLimits?.limits) return null;
    
    const limitInfo = rateLimits.limits[category];
    if (!limitInfo) return null;
    
    const { limit, remaining, reset_after: resetAfter, error: limitError } = limitInfo;
    const percentage = limit ? Math.min(100, (remaining / parseInt(limit.split('/')[0], 10)) * 100) : 0;
    
    // Determine color based on percentage
    let color = theme.palette.success.main;
    if (percentage <= 20) {
      color = theme.palette.error.main;
    } else if (percentage <= 50) {
      color = theme.palette.warning.main;
      }
    
    // Format reset time
    const resetTime = formatTimeRemaining(resetAfter);
    
    return (
      <Box key={category} sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="body2">{label}</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {limitError ? (
              <Tooltip title={limitError}>
                <div style={{ 
                  color: theme.palette.error.main, 
                  marginRight: '4px',
                  fontWeight: 'bold'
                }}>!</div>
              </Tooltip>
            ) : (
              <Tooltip title="Active">
                <div style={{
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  backgroundColor: color,
                  marginRight: '4px',
                  animation: remaining <= 0 ? 'pulse 2s infinite ease-in-out' : 'none'
                }} />
              </Tooltip>
            )}
            <Typography variant="body2" fontWeight="medium">
              {remaining}/{limit.split('/')[0]} remaining
            </Typography>
          </Box>
        </Box>
        
        <Tooltip 
          title={`Resets in ${resetTime}`} 
          placement="top"
        >
          <Box sx={{ position: 'relative', height: 8, width: '100%', bgcolor: theme.palette.grey[200], borderRadius: 1 }}>
            <Box 
              sx={{ 
                height: '100%', 
                width: `${percentage}%`, 
                bgcolor: color,
                borderRadius: 1,
                transition: 'width 0.5s ease-in-out'
              }} 
            />
          </Box>
        </Tooltip>
      </Box>
    );
  };

  return (
    <Paper 
      elevation={3} 
      className={className}
      sx={{ 
        p: 2, 
        width: '100%', 
        maxWidth: 400,
        position: 'relative',
        backdropFilter: 'blur(10px)',
        backgroundColor: 'rgba(255, 255, 255, 0.9)',
      }}
    >
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" fontWeight="bold">{title}</Typography>
        
        {showRefresh && (
          <Tooltip title={refreshCooldown > 0 ? `Refresh again in ${refreshCooldown}s` : 'Refresh rate limits'}>
            <span>
              <Button
                size="small"
                onClick={handleRefresh}
                disabled={refreshCooldown > 0 || isLoading}
                sx={{ 
                  minWidth: 'auto',
                  opacity: refreshCooldown > 0 ? 0.5 : 1,
                }}
              >
                {refreshCooldown > 0 ? `${refreshCooldown}s` : '↻ Refresh'}
              </Button>
            </span>
          </Tooltip>
        )}
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      {/* Loading state */}
      {isLoading && !rateLimits && (
        <Box sx={{ mb: 2 }}>
          <LinearProgress />
          <Typography variant="body2" sx={{ mt: 1, textAlign: 'center' }}>
            Loading rate limits...
          </Typography>
        </Box>
      )}
      
      {/* Error state */}
      {error && (
        <Box sx={{ mb: 2, p: 1, bgcolor: theme.palette.error.light, borderRadius: 1 }}>
          <Typography variant="body2" color="error">
            {typeof error === 'string' ? error : 'Failed to load rate limits'}
          </Typography>
        </Box>
      )}
      
      {/* Rate limit items */}
      {rateLimits?.limits && (
        <>
          {renderRateLimitItem('Concept Generation', 'generate_concept')}
          {renderRateLimitItem('Concept Refinement', 'refine_concept')}
          {renderRateLimitItem('Store Concepts', 'store_concept')}
          {renderRateLimitItem('List Concepts', 'get_concepts')}
          {renderRateLimitItem('Image Export', 'export_action')}
          {renderRateLimitItem('Active Sessions', 'sessions')}
        </>
      )}
      
      {/* User identifier */}
      {rateLimits?.user_identifier && (
        <Box sx={{ mt: 2, pt: 1, borderTop: `1px solid ${theme.palette.divider}` }}>
          <Typography variant="caption" color="textSecondary">
            User ID: {rateLimits.user_identifier}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};