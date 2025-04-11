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
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Track when the initiating state was first set
  const initiatingStartTimeRef = useRef<number | null>(null);
  
  // For debugging purposes, log all task-related state
  useEffect(() => {
    console.log('TaskStatusBar - Debug State:', {
      activeTaskId,
      hasActiveTask,
      taskStatus: activeTaskData?.status,
      isTaskPending,
      isTaskProcessing, 
      isTaskCompleted,
      isTaskFailed,
      isTaskInitiating,
      shouldShowCompleted,
      timestamp: new Date().toISOString()
    });
  }, [activeTaskId, activeTaskData, hasActiveTask, isTaskPending, isTaskProcessing, isTaskCompleted, isTaskFailed, isTaskInitiating, shouldShowCompleted]);
  
  // Track initiating start time
  useEffect(() => {
    if (isTaskInitiating && initiatingStartTimeRef.current === null) {
      initiatingStartTimeRef.current = Date.now();
      console.log('TaskStatusBar - Initiating started at:', initiatingStartTimeRef.current);
    } else if (!isTaskInitiating) {
      initiatingStartTimeRef.current = null;
    }
  }, [isTaskInitiating]);
  
  // When task completes, show the completed status for 5 seconds
  useEffect(() => {
    if (isTaskCompleted && !shouldShowCompleted) {
      console.log('TaskStatusBar - Task completed, showing completed status');
      setShouldShowCompleted(true);
      
      // Clear any existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      // Set a timeout to hide the completed status after 5 seconds
      timeoutRef.current = setTimeout(() => {
        console.log('TaskStatusBar - Completed status timeout finished, hiding status bar');
        setShouldShowCompleted(false);
      }, 5000);
    }
    
    // Cleanup timeouts on unmount or status change
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isTaskCompleted, shouldShowCompleted]);
  
  // Calculate how long the initiating state has been active
  const initiatingDuration = initiatingStartTimeRef.current 
    ? Date.now() - initiatingStartTimeRef.current 
    : 0;
  
  // Only show when a task is active, initiating (for a short time), failed, or completed
  const isVisible = (
    hasActiveTask || 
    (isTaskInitiating && initiatingDuration < 6000) || 
    isTaskFailed || 
    shouldShowCompleted || 
    isTaskCompleted
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
        <button 
          onClick={() => {
            if (timeoutRef.current) clearTimeout(timeoutRef.current);
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