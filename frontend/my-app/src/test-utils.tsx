import React, { ReactElement } from "react";
import {
  render as rtlRender,
  RenderOptions,
  screen,
  waitFor,
  waitForElementToBeRemoved,
  act,
  fireEvent,
  within,
} from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Create a custom render method that includes providers
interface CustomRenderOptions extends Omit<RenderOptions, "wrapper"> {
  queryClient?: QueryClient;
}

// Define the type for global with queryClient
interface GlobalWithQueryClient extends NodeJS.Global {
  queryClient?: QueryClient;
}

/**
 * Custom render function that wraps components with necessary providers
 * for testing, including QueryClientProvider
 */
export function customRender(
  ui: ReactElement,
  options: CustomRenderOptions = {},
) {
  // Use the global queryClient if available or create a new one
  const queryClient =
    options.queryClient ||
    (global as GlobalWithQueryClient).queryClient ||
    new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
        },
      },
    });

  const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };

  return rtlRender(ui, { wrapper: AllTheProviders, ...options });
}

// Export specific functions from testing-library
export { screen, waitFor, waitForElementToBeRemoved, act, fireEvent, within };

// Override render method
export { customRender as render };
