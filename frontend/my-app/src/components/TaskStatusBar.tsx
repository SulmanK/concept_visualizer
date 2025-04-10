import React, { useEffect, useState } from 'react';
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
    isTaskFailed
  } = useTaskContext();
  
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
      timestamp: new Date().toISOString()
    });
  }, [activeTaskId, activeTaskData, hasActiveTask, isTaskPending, isTaskProcessing, isTaskCompleted, isTaskFailed]);
  
  // FORCE VISIBLE FOR DEBUGGING
  // Always show the bar for debugging, with a test message
  // We'll keep this enabled until we solve the visibility issue
  const forceVisible = true;
  
  // Only show when a task is in progress (pending or processing) or recently completed/failed
  // TEMPORARILY DISABLED THIS CONDITION FOR DEBUGGING
  // if (!hasActiveTask && !isTaskCompleted && !isTaskFailed) {
  //   return null;
  // }
  
  let statusMessage = "No active task";
  let statusColor = "bg-gray-200";
  let statusIcon = null;
  
  if (isTaskPending) {
    statusMessage = "Preparing your request...";
    statusColor = "bg-yellow-100 border-yellow-300";
    statusIcon = <LoadingIndicator size="small" />;
  } else if (isTaskProcessing) {
    statusMessage = "Processing your request...";
    statusColor = "bg-blue-100 border-blue-300";
    statusIcon = <LoadingIndicator size="small" />;
  } else if (isTaskCompleted) {
    statusMessage = "Task completed successfully!";
    statusColor = "bg-green-100 border-green-300";
    statusIcon = (
      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
      </svg>
    );
  } else if (isTaskFailed) {
    statusMessage = activeTaskData?.error_message || "Task failed";
    statusColor = "bg-red-100 border-red-300";
    statusIcon = (
      <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    );
  }
  
  // If we're forcing visibility and have no active task, show a debug message
  if (forceVisible && !hasActiveTask && !isTaskCompleted && !isTaskFailed) {
    statusMessage = "Debug: Task bar should be visible";
    statusColor = "bg-purple-100 border-purple-300";
    statusIcon = (
      <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
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
      </div>
    </div>
  );
};

export default TaskStatusBar; 