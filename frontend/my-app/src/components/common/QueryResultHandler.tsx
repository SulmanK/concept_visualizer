import React, { ReactNode } from "react";
import { LoadingIndicator } from "../ui/LoadingIndicator";
import { ErrorMessage } from "../ui/ErrorMessage";

interface QueryResultHandlerProps<T> {
  /** Is the query currently loading */
  isLoading: boolean;

  /** Any error that occurred during the query */
  error: Error | null | unknown;

  /** The data returned by the query */
  data: T | null | undefined;

  /** Optional custom loading component */
  loadingComponent?: ReactNode;

  /** Optional custom error component */
  errorComponent?: ReactNode;

  /** Optional custom empty data component */
  emptyComponent?: ReactNode;

  /** Children function that renders when data is available */
  children: (data: T) => ReactNode;

  /** Optional error message to display when error is truthy but lacks detail */
  fallbackErrorMessage?: string;

  /** Optional empty message when data is null/empty */
  emptyMessage?: string;
}

const DefaultEmpty = ({
  message = "No data available",
}: {
  message?: string;
}) => (
  <div className="w-full p-6 text-center text-gray-500 bg-gray-50 rounded-lg">
    <p>{message}</p>
  </div>
);

/**
 * QueryResultHandler provides standardized handling for React Query results
 *
 * This component handles:
 * - Loading states
 * - Error states
 * - Empty data states
 * - Rendering data when available
 */
export function QueryResultHandler<T>({
  isLoading,
  error,
  data,
  loadingComponent,
  errorComponent,
  emptyComponent,
  children,
  fallbackErrorMessage = "An error occurred while fetching data",
  emptyMessage = "No data available",
}: QueryResultHandlerProps<T>) {
  if (isLoading) {
    return loadingComponent ? (
      <>{loadingComponent}</>
    ) : (
      <div className="w-full flex justify-center p-6">
        <LoadingIndicator />
      </div>
    );
  }

  if (error) {
    if (errorComponent) {
      return <>{errorComponent}</>;
    }

    const errorMessage =
      error instanceof Error ? error.message : fallbackErrorMessage;

    return <ErrorMessage message={errorMessage} />;
  }

  // Check for empty data
  if (
    data === null ||
    data === undefined ||
    (Array.isArray(data) && data.length === 0)
  ) {
    return emptyComponent ? (
      <>{emptyComponent}</>
    ) : (
      <DefaultEmpty message={emptyMessage} />
    );
  }

  // If we have data, render the children function
  return <>{children(data)}</>;
}
