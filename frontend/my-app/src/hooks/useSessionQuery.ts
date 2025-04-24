import { useMutation, UseMutationResult } from "@tanstack/react-query";
import { apiClient } from "../services/apiClient";
import { useErrorHandling } from "./useErrorHandling";
import { createQueryErrorHandler } from "../utils/errorUtils";

interface SessionResponse {
  session_id: string;
  created: boolean;
  [key: string]: any;
}

interface SyncSessionInput {
  client_session_id: string;
}

/**
 * Hook for syncing the session with the backend
 *
 * @returns Mutation for syncing the session
 */
export function useSessionSyncMutation(): UseMutationResult<
  SessionResponse,
  Error,
  SyncSessionInput,
  unknown
> {
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: "Failed to sync session. Please try again.",
  });

  return useMutation<SessionResponse, Error, SyncSessionInput>({
    mutationFn: async (input: SyncSessionInput) => {
      console.log(
        `[useSessionSyncMutation] Syncing session (masked ID: ${maskSessionId(
          input.client_session_id,
        )})`,
      );
      const { data } = await apiClient.post<SessionResponse>(
        "/sessions/sync",
        input,
      );
      return data;
    },
    onError: onQueryError,
    retry: 1, // Try once more if it fails
  });
}

/**
 * Helper to mask a session ID for logging (security/privacy)
 */
function maskSessionId(sessionId: string, visibleChars: number = 4): string {
  if (!sessionId) return "null";
  if (sessionId.length <= visibleChars * 2) return "***";

  const start = sessionId.substring(0, visibleChars);
  const end = sessionId.substring(sessionId.length - visibleChars);
  return `${start}...${end}`;
}
