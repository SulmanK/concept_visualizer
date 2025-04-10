import React, { useEffect, useState, useRef } from 'react';
import { useTaskContext } from '../contexts/TaskContext';
import { LoadingIndicator } from './ui/LoadingIndicator';
import { apiClient } from '../services/apiClient';
import { TaskResponse } from '../types/api.types';

/**
 * Displays the current task status as a floating bar
 */
const TaskStatusBar: React.FC = () => {
  // Get the task state from the global context
  const { 
    activeTaskId,
    activeTaskData,
    hasActiveTask,
    isTaskPending,
    isTaskProcessing,
    isTaskCompleted,
    isTaskFailed,
    isTaskInitiating,
    refreshTaskStatus
  } = useTaskContext();
  
  // State to handle showing the completed status for a short time
  const [shouldShowCompleted, setShouldShowCompleted] = useState(false);
  // State to override context status when direct API check is different
  const [directTaskStatus, setDirectTaskStatus] = useState<string | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const statusRefreshIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const directApiCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Track when the initiating state was first set
  const [initiatingStartTime, setInitiatingStartTime] = useState<number | null>(null);
  
  // For debugging purposes, log all task-related state
  useEffect(() => {
    console.log('TaskStatusBar - Debug State:', {
      activeTaskId,
      hasActiveTask,
      taskStatus: activeTaskData?.status,
      directTaskStatus,
      isTaskPending,
      isTaskProcessing, 
      isTaskCompleted,
      isTaskFailed,
      isTaskInitiating,
      shouldShowCompleted,
      timestamp: new Date().toISOString()
    });
  }, [activeTaskId, activeTaskData, hasActiveTask, isTaskPending, isTaskProcessing, isTaskCompleted, isTaskFailed, isTaskInitiating, shouldShowCompleted, directTaskStatus]);
  
  // Directly check task status via API when needed
  useEffect(() => {
    if (activeTaskId && (isTaskPending || isTaskProcessing)) {
      // Set up direct API check for task status
      console.log('TaskStatusBar - Setting up direct API check for task status');
      
      // Function to check task status directly
      const checkTaskStatus = async () => {
        try {
          if (!activeTaskId) return;
          
          console.log(`TaskStatusBar - Direct API check for task ${activeTaskId}`);
          const response = await apiClient.get<TaskResponse>(`/tasks/${activeTaskId}`);
          const status = response.data.status;
          
          console.log(`TaskStatusBar - Direct API status: ${status}, Context status: ${activeTaskData?.status}`);
          
          // If direct status is different from context status, use direct status
          if (status !== activeTaskData?.status) {
            console.log(`TaskStatusBar - Status mismatch! Setting direct status: ${status}`);
            setDirectTaskStatus(status);
            
            // If task is completed, show completion status
            if (status === 'completed') {
              console.log('TaskStatusBar - Direct check shows task completed');
              setShouldShowCompleted(true);
              
              // Set a timeout to hide the completed status after 5 seconds
              if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
              }
              
              timeoutRef.current = setTimeout(() => {
                console.log('TaskStatusBar - Direct check completion timeout finished');
                setShouldShowCompleted(false);
                setDirectTaskStatus(null);
              }, 5000);
            }
          }
        } catch (error) {
          console.error('TaskStatusBar - Error in direct API check:', error);
        }
      };
      
      // Call it immediately
      checkTaskStatus();
      
      // Clear any existing interval
      if (directApiCheckIntervalRef.current) {
        clearInterval(directApiCheckIntervalRef.current);
      }
      
      // Check every 2 seconds
      directApiCheckIntervalRef.current = setInterval(checkTaskStatus, 2000);
    } else if (directApiCheckIntervalRef.current) {
      // Clear interval if task is no longer active
      clearInterval(directApiCheckIntervalRef.current);
      directApiCheckIntervalRef.current = null;
    }
    
    return () => {
      if (directApiCheckIntervalRef.current) {
        clearInterval(directApiCheckIntervalRef.current);
        directApiCheckIntervalRef.current = null;
      }
    };
  }, [activeTaskId, isTaskPending, isTaskProcessing, activeTaskData?.status]);
  
  // Set up periodic task status refresh
  useEffect(() => {
    if (activeTaskId && (isTaskPending || isTaskProcessing)) {
      // If we have an active task that's not in a terminal state, set up periodic refresh
      console.log('TaskStatusBar - Setting up periodic task status refresh');
      
      // Clear any existing interval
      if (statusRefreshIntervalRef.current) {
        clearInterval(statusRefreshIntervalRef.current);
      }
      
      // Refresh every 3 seconds
      statusRefreshIntervalRef.current = setInterval(() => {
        console.log('TaskStatusBar - Forcing task status refresh');
        refreshTaskStatus();
      }, 3000);
    }
    
    return () => {
      if (statusRefreshIntervalRef.current) {
        clearInterval(statusRefreshIntervalRef.current);
        statusRefreshIntervalRef.current = null;
      }
    };
  }, [activeTaskId, isTaskPending, isTaskProcessing, refreshTaskStatus]);
  
  // When task completes, show the completed status for 5 seconds
  useEffect(() => {
    if (isTaskCompleted) {
      console.log('Task completed, showing completed status');
      setShouldShowCompleted(true);
      
      // Clear any existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      // Set a timeout to hide the completed status after 5 seconds
      timeoutRef.current = setTimeout(() => {
        console.log('Completed status timeout finished, hiding status bar');
        setShouldShowCompleted(false);
      }, 5000);
    }
    
    // Cleanup timeouts on unmount or status change
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isTaskCompleted]);
  
  // Update initiatingStartTime when isTaskInitiating changes
  useEffect(() => {
    if (isTaskInitiating && initiatingStartTime === null) {
      setInitiatingStartTime(Date.now());
    } else if (!isTaskInitiating) {
      setInitiatingStartTime(null);
    }
  }, [isTaskInitiating, initiatingStartTime]);
  
  // Add this new effect to monitor the initiating state
  useEffect(() => {
    // If there's an initiating state but no active task ID after a few seconds,
    // we likely have a stale initiating state that never got cleared
    if (isTaskInitiating && !activeTaskId) {
      console.log('TaskStatusBar - Detected initiating state with no task ID, setting up auto-clear timer');
      
      // Set a timeout to auto-clear the initiating state if no task ID appears
      const timeoutId = setTimeout(() => {
        console.log('TaskStatusBar - Auto-clearing stale initiating state since no task ID was assigned');
        
        // Access the original TaskContext to clear the initiating state
        try {
          const { useTaskContext } = require('../contexts/TaskContext');
          const taskContext = useTaskContext();
          taskContext.setIsTaskInitiating(false);
        } catch (error) {
          console.error('TaskStatusBar - Error clearing stale initiating state:', error);
        }
        
        // Also clear our local state
        setShouldShowCompleted(false);
        setDirectTaskStatus(null);
      }, 5000); // 5 seconds should be enough for a task ID to be assigned
      
      return () => clearTimeout(timeoutId);
    }
  }, [isTaskInitiating, activeTaskId]);
  
  // Calculate how long the initiating state has been active
  const initiatingDuration = initiatingStartTime ? Date.now() - initiatingStartTime : 0;
  
  // Only show when a task is active, initiating (with a valid task ID or for a short time), failed or completed
  const isVisible = (hasActiveTask || 
                     (isTaskInitiating && (!!activeTaskId || initiatingDuration < 6000)) || 
                     isTaskFailed || 
                     shouldShowCompleted || 
                     isTaskCompleted);
  
  // If not visible, don't render anything
  if (!isVisible) {
    return null;
  }
  
  // Determine status based on both context state and direct API check
  const determineStatus = () => {
    // If we have a direct API status that's completed, override context status
    if (directTaskStatus === 'completed') {
      return 'completed';
    }
    
    // Otherwise, use context state
    if (isTaskCompleted || shouldShowCompleted) {
      return 'completed';
    }
    
    if (isTaskProcessing) {
      return 'processing';
    }
    
    if (isTaskPending) {
      return 'pending';
    }
    
    if (isTaskInitiating) {
      return 'initiating';
    }
    
    if (isTaskFailed) {
      return 'failed';
    }
    
    return 'unknown';
  };
  
  const status = determineStatus();
  
  let statusMessage = "No active task";
  let statusColor = "bg-gray-200";
  let statusIcon = null;
  
  if (status === 'initiating') {
    statusMessage = "Preparing your request...";
    statusColor = "bg-yellow-100 border-yellow-300";
    statusIcon = <LoadingIndicator size="small" />;
  } else if (status === 'pending') {
    statusMessage = "Preparing your request...";
    statusColor = "bg-yellow-100 border-yellow-300";
    statusIcon = <LoadingIndicator size="small" />;
  } else if (status === 'processing') {
    statusMessage = "Processing your request...";
    statusColor = "bg-blue-100 border-blue-300";
    statusIcon = <LoadingIndicator size="small" />;
  } else if (status === 'completed') {
    statusMessage = "Task completed successfully!";
    statusColor = "bg-green-100 border-green-300";
    statusIcon = (
      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
      </svg>
    );
  } else if (status === 'failed') {
    statusMessage = activeTaskData?.error_message || "Task failed";
    statusColor = "bg-red-100 border-red-300";
    statusIcon = (
      <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    );
  }
  
  return (
    <div className={`fixed top-6 right-6 min-w-[320px] z-50 p-3 rounded-lg shadow-2xl border-2 ${statusColor} transition-all duration-300`}>
      <div className="flex items-center">
        <div className="mr-3 flex-shrink-0">
          {statusIcon}
        </div>
        <div className="flex-grow">
          <p className="text-sm font-medium">{statusMessage}</p>
          {activeTaskId && (
            <p className="text-xs opacity-60">Task ID: {activeTaskId.substring(0, 8)}...</p>
          )}
        </div>
        <button 
          onClick={() => {
            clearInterval(directApiCheckIntervalRef.current!);
            clearInterval(statusRefreshIntervalRef.current!);
            clearTimeout(timeoutRef.current!);
            setDirectTaskStatus(null);
            setShouldShowCompleted(false);
            refreshTaskStatus();
          }}
          className="ml-2 text-gray-500 hover:text-gray-700"
          aria-label="Refresh status"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default TaskStatusBar; 