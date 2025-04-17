import { useEffect, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { supabase } from '../services/supabaseClient';
import { TaskResponse } from '../types/api.types';
import { queryKeys } from '../config/queryKeys';
import { useTaskStatusQuery } from './useTaskQueries';

/**
 * Hook to subscribe to real-time updates for a specific task
 * 
 * @param taskId - ID of the task to subscribe to
 * @returns The latest task data and subscription status
 */
export function useTaskSubscription(taskId: string | null) {
  const [taskData, setTaskData] = useState<TaskResponse | null>(null);
  const [subscriptionError, setSubscriptionError] = useState<Error | null>(null);
  const [subscriptionStatus, setSubscriptionStatus] = useState<string | null>(null);
  const queryClient = useQueryClient();

  // Fetch the initial task data
  const { data: initialData, isError, error } = useTaskStatusQuery(taskId, {
    // Only fetch on initial mount or when taskId changes, then disable
    enabled: !!taskId && !taskData,
  });

  // Set initial data when it's available
  useEffect(() => {
    if (initialData && !taskData) {
      console.log(`[TaskSubscription] Setting initial data for task ${taskId}`);
      setTaskData(initialData);
    }
  }, [initialData, taskData, taskId]);

  // Set up Supabase Realtime subscription
  useEffect(() => {
    if (!taskId) {
      setTaskData(null);
      setSubscriptionStatus(null);
      return;
    }

    console.log(`[TaskSubscription] Setting up subscription for task ${taskId}`);
    
    // Create a channel for this specific task
    const channel = supabase.channel(`task-updates-${taskId}`)
      .on('postgres_changes', { 
        event: 'UPDATE',
        schema: 'public',
        table: 'tasks',
        filter: `id=eq.${taskId}`
      }, (payload) => {
        console.log(`[TaskSubscription] Received update for task ${taskId}:`, payload);
        
        // The payload.new contains the updated task data
        const updatedTask = payload.new as TaskResponse;
        
        // Update the local state
        setTaskData(updatedTask);
        
        // Also update the query cache
        queryClient.setQueryData(
          queryKeys.tasks.detail(taskId),
          updatedTask
        );
      })
      .on('system', { event: 'connection_state_change' }, (status) => {
        console.log(`[TaskSubscription] Connection status changed:`, status);
        setSubscriptionStatus(status?.event);
      })
      .on('system', { event: 'channel_state_change' }, (status) => {
        console.log(`[TaskSubscription] Channel status changed:`, status);
      })
      .on('system', { event: 'disconnected' }, () => {
        console.log(`[TaskSubscription] Disconnected from Supabase Realtime`);
        setSubscriptionStatus('disconnected');
      })
      .on('system', { event: 'error' }, (err) => {
        console.error(`[TaskSubscription] Error in subscription:`, err);
        setSubscriptionError(new Error('Subscription error'));
        setSubscriptionStatus('error');
      });

    // Subscribe to the channel
    channel.subscribe((status) => {
      console.log(`[TaskSubscription] Subscription status:`, status);
      setSubscriptionStatus(status);
      
      if (status === 'SUBSCRIBED') {
        console.log(`[TaskSubscription] Successfully subscribed to updates for task ${taskId}`);
      } else if (status === 'CHANNEL_ERROR') {
        console.error(`[TaskSubscription] Error subscribing to task ${taskId}`);
        setSubscriptionError(new Error('Failed to subscribe to task updates'));
      } else if (status === 'TIMED_OUT') {
        console.error(`[TaskSubscription] Subscription timed out for task ${taskId}`);
        setSubscriptionError(new Error('Subscription timed out'));
      }
    });

    // Cleanup function
    return () => {
      console.log(`[TaskSubscription] Cleaning up subscription for task ${taskId}`);
      supabase.removeChannel(channel);
    };
  }, [taskId, queryClient]);

  // Handle initial fetch error
  useEffect(() => {
    if (isError && error) {
      console.error(`[TaskSubscription] Error fetching initial task data:`, error);
      setSubscriptionError(error);
    }
  }, [isError, error]);

  return {
    taskData, 
    error: subscriptionError,
    status: subscriptionStatus,
  };
} 