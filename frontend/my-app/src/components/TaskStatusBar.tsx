import React, { useEffect, useState, useRef } from 'react';
import { useTaskContext } from '../contexts/TaskContext';
import { LoadingIndicator } from './ui/LoadingIndicator';

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
  // State to handle manually dismissing the status bar
  const [isDismissed, setIsDismissed] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Track when the initiating state was first set
  const initiatingStartTimeRef = useRef<number | null>(null);
  
  // Track completed task ID to detect new completions
  const lastCompletedTaskRef = useRef<string | null>(null);
  
  // Track initiating start time
  useEffect(() => {
    if (isTaskInitiating && initiatingStartTimeRef.current === null) {
      initiatingStartTimeRef.current = Date.now();
    } else if (!isTaskInitiating) {
      initiatingStartTimeRef.current = null;
    }
  }, [isTaskInitiating]);
  
  // When task completes, show the completed status for 1 minute (60 seconds)
  useEffect(() => {
    // Only trigger the completed state display if:
    // 1. A task has completed
    // 2. We're not already showing the completed state for this task
    // 3. The task ID is different from the last one we showed
    if (isTaskCompleted && activeTaskId && 
        (!shouldShowCompleted || lastCompletedTaskRef.current !== activeTaskId)) {
      
      // Store the current task ID
      lastCompletedTaskRef.current = activeTaskId;
      
      // Update the state to show the completed status
      setShouldShowCompleted(true);
      setIsDismissed(false); // Reset dismissed state when a new completion happens
      
      // Clear any existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      // Set a timeout to hide the completed status after 60 seconds
      timeoutRef.current = setTimeout(() => {
        setShouldShowCompleted(false);
      }, 60000); // 60 seconds = 1 minute
    }
    
    // Cleanup timeouts on unmount or status change
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isTaskCompleted, shouldShowCompleted, activeTaskId]);
  
  // Handle dismissing the status bar
  const handleDismiss = () => {
    setIsDismissed(true);
    
    // Clear any existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };
  
  // Calculate how long the initiating state has been active
  const initiatingDuration = initiatingStartTimeRef.current 
    ? Date.now() - initiatingStartTimeRef.current 
    : 0;
  
  // Only show when a task is active, initiating (for a short time), failed, or completed
  // And respect the dismissed state
  const isVisible = (
    !isDismissed && (
      hasActiveTask || 
      (isTaskInitiating && initiatingDuration < 6000) || 
      isTaskFailed || 
      shouldShowCompleted || 
      isTaskCompleted
    )
  );
  
  // If not visible, don't render anything
  if (!isVisible) {
    return null;
  }
  
  // Determine status based solely on context state
  const determineStatus = () => {
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
    statusMessage = "Request queued...";
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
        <div className="flex ml-2">
          <button 
            onClick={refreshTaskStatus}
            className="text-gray-500 hover:text-gray-700 mr-2"
            aria-label="Refresh status"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
          </button>
          <button 
            onClick={handleDismiss}
            className="text-gray-500 hover:text-gray-700"
            aria-label="Close status"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskStatusBar; 