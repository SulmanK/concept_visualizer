import { useEffect, useState, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { supabase } from "../services/supabaseClient";
import { TaskResponse } from "../types/api.types";
import { queryKeys } from "../config/queryKeys";
import { useTaskStatusQuery } from "./useTaskQueries";
import { getTableName } from "../services/databaseConfig";

// Constants for reconnection
const RECONNECT_TIMEOUT = 5000; // 5 seconds
const MAX_RECONNECT_ATTEMPTS = 5;

/**
 * Hook to subscribe to real-time updates for a specific task
 *
 * @param taskId - ID of the task to subscribe to
 * @returns The latest task data and subscription status
 */
export function useTaskSubscription(taskId: string | null) {
  const [taskData, setTaskData] = useState<TaskResponse | null>(null);
  const [subscriptionError, setSubscriptionError] = useState<Error | null>(
    null,
  );
  const [subscriptionStatus, setSubscriptionStatus] = useState<string | null>(
    null,
  );
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [shouldReconnect, setShouldReconnect] = useState(false);
  const channelRef = useRef<ReturnType<typeof supabase.channel> | null>(null);
  const queryClient = useQueryClient();

  // Get the tasks table name from environment
  const tasksTable = getTableName("tasks");

  // Fetch the initial task data
  const {
    data: initialData,
    isError,
    error,
  } = useTaskStatusQuery(taskId, {
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
      setShouldReconnect(false);
      setReconnectAttempts(0);
      return;
    }

    console.log(
      `[TaskSubscription] Setting up subscription for task ${taskId} on table ${tasksTable}`,
    );

    // Function to create and subscribe to a channel
    const createAndSubscribeToChannel = (taskId: string) => {
      if (!taskId) return null;

      console.log(`[TaskSubscription] Creating channel for task ${taskId}`);

      try {
        // Create a channel for this specific task
        const channel = supabase
          .channel(`task-updates-${taskId}`)
          .on(
            "postgres_changes",
            {
              event: "UPDATE",
              schema: "public",
              table: tasksTable,
              filter: `id=eq.${taskId}`,
            },
            (payload) => {
              console.log(
                `[TaskSubscription] Received update for task ${taskId}:`,
                payload,
              );

              // The payload.new contains the updated task data
              const updatedTask = payload.new as TaskResponse;

              // Update the local state
              setTaskData(updatedTask);

              // Also update the query cache
              queryClient.setQueryData(
                queryKeys.tasks.detail(taskId),
                updatedTask,
              );
            },
          )
          .on("system", { event: "connection_state_change" }, (status) => {
            console.log(
              `[TaskSubscription] Connection status changed:`,
              status,
            );
            setSubscriptionStatus(status?.event);

            // If connection state is CLOSED, attempt reconnection
            if (status?.event === "CLOSED") {
              console.log(
                `[TaskSubscription] Connection closed, will attempt reconnect`,
              );
              setShouldReconnect(true);
            }
          })
          .on("system", { event: "channel_state_change" }, (status) => {
            console.log(`[TaskSubscription] Channel status changed:`, status);
          })
          .on("system", { event: "disconnected" }, () => {
            console.log(
              `[TaskSubscription] Disconnected from Supabase Realtime`,
            );
            setSubscriptionStatus("disconnected");
            setShouldReconnect(true);
          })
          .on("system", { event: "error" }, (err) => {
            // Only set error if the message indicates an actual error
            // "Subscribed to PostgreSQL" with status "ok" is not an error
            if (err.status !== "ok") {
              console.error(`[TaskSubscription] Error in subscription:`, err);
              setSubscriptionError(new Error("Subscription error"));
              setSubscriptionStatus("error");
              setShouldReconnect(true);
            } else {
              console.log(`[TaskSubscription] System event:`, err);
            }
          });

        // Subscribe to the channel
        channel.subscribe((status) => {
          console.log(`[TaskSubscription] Subscription status:`, status);
          setSubscriptionStatus(status);

          if (status === "SUBSCRIBED") {
            console.log(
              `[TaskSubscription] Successfully subscribed to updates for task ${taskId} on table ${tasksTable}`,
            );
            // Reset reconnection attempts on successful subscription
            setReconnectAttempts(0);
            setShouldReconnect(false);
            // Clear any previous errors since we're now successfully subscribed
            setSubscriptionError(null);
          } else if (status === "CHANNEL_ERROR") {
            console.error(
              `[TaskSubscription] Error subscribing to task ${taskId}`,
            );
            setSubscriptionError(
              new Error("Failed to subscribe to task updates"),
            );
            setShouldReconnect(true);
          } else if (status === "TIMED_OUT") {
            console.error(
              `[TaskSubscription] Subscription timed out for task ${taskId}`,
            );
            setSubscriptionError(new Error("Subscription timed out"));
            setShouldReconnect(true);
          }
        });

        return channel;
      } catch (error) {
        console.error(`[TaskSubscription] Error creating channel:`, error);
        setSubscriptionError(new Error(`Failed to create channel: ${error}`));
        setShouldReconnect(true);
        return null;
      }
    };

    // Create and subscribe to the channel
    channelRef.current = createAndSubscribeToChannel(taskId);

    // Cleanup function
    return () => {
      if (channelRef.current) {
        console.log(
          `[TaskSubscription] Cleaning up subscription for task ${taskId}`,
        );
        supabase.removeChannel(channelRef.current);
        channelRef.current = null;
      }
    };
  }, [taskId, queryClient, shouldReconnect, tasksTable]);

  // Handle reconnection logic
  useEffect(() => {
    let reconnectTimer: NodeJS.Timeout | null = null;

    if (shouldReconnect && reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      console.log(
        `[TaskSubscription] Planning reconnection attempt ${
          reconnectAttempts + 1
        }/${MAX_RECONNECT_ATTEMPTS} in ${RECONNECT_TIMEOUT / 1000}s`,
      );

      reconnectTimer = setTimeout(() => {
        if (taskId) {
          console.log(
            `[TaskSubscription] Attempting to reconnect for task ${taskId}`,
          );
          setReconnectAttempts((prev) => prev + 1);

          // Clean up previous channel if it exists
          if (channelRef.current) {
            supabase.removeChannel(channelRef.current);
            channelRef.current = null;
          }

          // Trigger reconnection by toggling shouldReconnect
          setShouldReconnect(false);
          setTimeout(() => setShouldReconnect(true), 100);
        }
      }, RECONNECT_TIMEOUT);
    } else if (shouldReconnect && reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.error(
        `[TaskSubscription] Giving up after ${MAX_RECONNECT_ATTEMPTS} reconnection attempts`,
      );
      setShouldReconnect(false);
      // Keep the error state to indicate reconnection failed
    }

    return () => {
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }
    };
  }, [shouldReconnect, reconnectAttempts, taskId]);

  // Handle initial fetch error
  useEffect(() => {
    if (isError && error) {
      console.error(
        `[TaskSubscription] Error fetching initial task data:`,
        error,
      );
      setSubscriptionError(error);
    }
  }, [isError, error]);

  return {
    taskData,
    error: subscriptionError,
    status: subscriptionStatus,
    reconnectAttempts,
    maxReconnectAttemptsReached: reconnectAttempts >= MAX_RECONNECT_ATTEMPTS,
  };
}
