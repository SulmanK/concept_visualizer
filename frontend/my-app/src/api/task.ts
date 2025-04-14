import { TaskResponse } from '../types/api.types';
import { apiClient } from '../services/apiClient';
import { API_ENDPOINTS } from '../config/apiEndpoints';

/**
 * Fetches the status of a task from the API
 * @param taskId The ID of the task to fetch
 * @returns The task response object
 */
export async function fetchTaskStatus(taskId: string): Promise<TaskResponse> {
  if (!taskId) {
    throw new Error('No task ID provided for status check');
  }
  
  console.log(`[API] Fetching status for task ${taskId}`);
  const response = await apiClient.get<TaskResponse>(API_ENDPOINTS.TASK_STATUS(taskId));
  
  // Normalize the response by ensuring the id field is set properly
  if (response.data.task_id && !response.data.id) {
    response.data.id = response.data.task_id;
  }
  
  console.log(`[API] Received status for task ${taskId}: ${response.data.status}`);
  return response.data;
}

/**
 * Cancels a running task
 * @param taskId The ID of the task to cancel
 * @returns The updated task response
 */
export async function cancelTask(taskId: string): Promise<TaskResponse> {
  if (!taskId) {
    throw new Error('No task ID provided for cancellation');
  }
  
  console.log(`[API] Cancelling task ${taskId}`);
  const response = await apiClient.post<TaskResponse>(API_ENDPOINTS.TASK_CANCEL(taskId));
  return response.data;
} 