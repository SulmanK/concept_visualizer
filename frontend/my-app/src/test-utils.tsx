import React, { ReactElement } from "react";
import { render, RenderOptions } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Create a custom render method that includes providers
interface CustomRenderOptions extends Omit<RenderOptions, "wrapper"> {
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
    (global as any).queryClient ||
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

  return render(ui, { wrapper: AllTheProviders, ...options });
}

// re-export everything from testing-library
export * from "@testing-library/react";

// Override render method
export { customRender as render };
