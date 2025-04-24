import { useState, useEffect, lazy, Suspense } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useLocation,
} from "react-router-dom";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import MainLayout from "./components/layout/MainLayout";
import { AuthProvider } from "./contexts/AuthContext";
import { ToastProvider } from "./hooks/useToast";
import { RateLimitProvider } from "./contexts/RateLimitContext";
import { ErrorBoundary, OfflineStatus, ErrorMessage } from "./components/ui";
import ApiToastListener from "./components/ui/ApiToastListener";
import { TaskProvider } from "./contexts/TaskContext";
import TaskStatusBar from "./components/TaskStatusBar";
import { AnimatePresence, LazyMotion, domAnimation, m } from "framer-motion";
import { useErrorHandling } from "./hooks/useErrorHandling";

// Lazy load pages instead of importing them directly
const LandingPage = lazy(() =>
  import("./features/landing").then((module) => ({
    default: module.LandingPage,
  })),
);
const ConceptDetailPage = lazy(() =>
  import("./features/concepts/detail").then((module) => ({
    default: module.ConceptDetailPage,
  })),
);
const RecentConceptsPage = lazy(() =>
  import("./features/concepts/recent").then((module) => ({
    default: module.RecentConceptsPage,
  })),
);
const CreateConceptPage = lazy(() =>
  import("./features/concepts/create").then((module) => ({
    default: module.CreateConceptPage,
  })),
);
const RefinementPage = lazy(() =>
  import("./features/refinement").then((module) => ({
    default: module.RefinementPage,
  })),
);
const RefinementSelectionPage = lazy(() =>
  import("./features/refinement").then((module) => ({
    default: module.RefinementSelectionPage,
  })),
);

// Loading fallback component
const LoadingFallback = () => (
  <div className="flex justify-center items-center h-screen bg-gradient-to-br from-[#f5f7ff] to-[#c3cfe2]">
    <div className="p-5 rounded-lg bg-white shadow-md flex flex-col items-center">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-indigo-500"></div>
      <p className="mt-4 text-indigo-600 font-medium">Loading...</p>
    </div>
  </div>
);

// Import animations CSS
import "./styles/animations.css";

/**
 * Routes component to handle the route transitions
 */
const AppRoutes = () => {
  const location = useLocation();

  // Define animation variants
  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    in: { opacity: 1, y: 0 },
    out: { opacity: 0, y: -20 },
  };

  // For slide transitions based on route
  const getVariants = (pathname: string) => {
    // Using a slide-up transition for concept detail pages
    if (pathname.includes("/concepts/")) {
      return {
        initial: { opacity: 0, y: 50 },
        in: { opacity: 1, y: 0 },
        out: { opacity: 0, y: -50 },
      };
    }

    // Using slide-left for refinement pages
    if (pathname.includes("/refine")) {
      return {
        initial: { opacity: 0, x: 50 },
        in: { opacity: 1, x: 0 },
        out: { opacity: 0, x: -50 },
      };
    }

    // Default fade transition for other routes
    return pageVariants;
  };

  return (
    <LazyMotion features={domAnimation} strict>
      <AnimatePresence mode="wait">
        <m.div
          key={location.pathname}
          initial="initial"
          animate="in"
          exit="out"
          variants={getVariants(location.pathname)}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className="h-full w-full"
        >
          <Suspense fallback={<LoadingFallback />}>
            <Routes location={location}>
              {/* Main application routes */}
              <Route path="/" element={<MainLayout />}>
                {/* Make LandingPage the default homepage */}
                <Route index element={<LandingPage />} />

                {/* Create page */}
                <Route path="create" element={<CreateConceptPage />} />

                {/* Concept detail page */}
                <Route
                  path="concepts/:conceptId"
                  element={<ConceptDetailPage />}
                />

                {/* Recent concepts page */}
                <Route path="recent" element={<RecentConceptsPage />} />

                {/* Refinement selection page */}
                <Route path="refine" element={<RefinementSelectionPage />} />

                {/* Refinement page with concept ID */}
                <Route path="refine/:conceptId" element={<RefinementPage />} />

                {/* Fallback for unknown routes */}
                <Route path="*" element={<div>Page not found</div>} />
              </Route>
            </Routes>
          </Suspense>
        </m.div>
      </AnimatePresence>
    </LazyMotion>
  );
};

/**
 * Inner app component that uses hooks that require ToastProvider context
 */
const AppContent = () => {
  const [debugInfo, setDebugInfo] = useState<any>(null);
  const errorHandler = useErrorHandling({
    // Don't show toasts for errors that will be displayed in the global error UI
    showToasts: false,
  });

  // Set basic debug info for development environment
  useEffect(() => {
    if (process.env.NODE_ENV === "development") {
      setDebugInfo({
        environment: process.env.NODE_ENV,
        apiBaseUrl:
          import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
        supabaseUrl: import.meta.env.VITE_SUPABASE_URL || "Not configured",
      });
    }
  }, []);

  // Listen for global error events that should be displayed in the UI
  useEffect(() => {
    // Listen for auth errors
    const authErrorHandler = () => {
      errorHandler.setError(
        "Your session has expired",
        "auth",
        "Please sign in again to continue.",
      );
    };

    // Listen for network status changes
    const networkErrorHandler = (event: CustomEvent) => {
      if (!event.detail.isOnline) {
        errorHandler.setError(
          "You are offline",
          "network",
          "Please check your internet connection and try again.",
        );
      } else {
        // Clear network errors when back online
        if (errorHandler.error?.category === "network") {
          errorHandler.clearError();
        }
      }
    };

    // Add event listeners
    document.addEventListener("auth-error-needs-logout", authErrorHandler);
    document.addEventListener(
      "network-status-change",
      networkErrorHandler as EventListener,
    );

    // Clean up listeners
    return () => {
      document.removeEventListener("auth-error-needs-logout", authErrorHandler);
      document.removeEventListener(
        "network-status-change",
        networkErrorHandler as EventListener,
      );
    };
  }, [errorHandler]);

  return (
    <>
      <ErrorBoundary errorMessage="Something went wrong in the application. Please try refreshing the page.">
        <ApiToastListener />
        <AuthProvider>
          <RateLimitProvider>
            <Router>
              {/* Global Error Message */}
              {errorHandler.hasError && errorHandler.error && (
                <div
                  className="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 w-[90%] max-w-[600px] animate-slide-down shadow-xl"
                  role="alert"
                  aria-live="assertive"
                >
                  {errorHandler.error.category === "rateLimit" ? (
                    <ErrorMessage
                      message={errorHandler.error.message}
                      details={errorHandler.error.details}
                      type="rateLimit"
                      className="shadow-lg border-2"
                      onDismiss={errorHandler.clearError}
                      rateLimitData={{
                        limit: errorHandler.error.limit || 0,
                        current: errorHandler.error.current || 0,
                        period: errorHandler.error.period || "unknown",
                        resetAfterSeconds:
                          errorHandler.error.resetAfterSeconds || 0,
                      }}
                    />
                  ) : errorHandler.error.category === "validation" &&
                    errorHandler.error.validationErrors ? (
                    <ErrorMessage
                      message={errorHandler.error.message}
                      details={errorHandler.error.details}
                      type="validation"
                      className="shadow-lg border-2"
                      onDismiss={errorHandler.clearError}
                      validationErrors={errorHandler.error.validationErrors}
                    />
                  ) : (
                    <ErrorMessage
                      message={errorHandler.error.message}
                      details={errorHandler.error.details}
                      type={errorHandler.error.category as any}
                      className="shadow-lg border-2"
                      status={errorHandler.error.status}
                      onDismiss={errorHandler.clearError}
                      onRetry={
                        errorHandler.error.category === "network"
                          ? () => {
                              window.location.reload();
                            }
                          : undefined
                      }
                    />
                  )}
                </div>
              )}

              {/* Offline status notification */}
              <OfflineStatus position="top" showConnectionInfo={true} />

              {/* TaskProvider needs to be inside Router but wrap both AppRoutes and TaskStatusBar */}
              <TaskProvider>
                <AppRoutes />
                <TaskStatusBar />
              </TaskProvider>
            </Router>
          </RateLimitProvider>
        </AuthProvider>
      </ErrorBoundary>

      {/* Debugging overlay - only shown in development */}
      {debugInfo && process.env.NODE_ENV === "development" && (
        <div className="fixed bottom-0 right-0 bg-black/70 text-white p-2.5 text-xs z-[9999] max-w-[300px]">
          <strong>Debug Info:</strong>
          <pre>{JSON.stringify(debugInfo, null, 2)}</pre>
        </div>
      )}

      {/* React Query Devtools - only in development */}
      {process.env.NODE_ENV === "development" && (
        <ReactQueryDevtools initialIsOpen={false} />
      )}
    </>
  );
};

export default function App() {
  return (
    <div className="m-0 p-0 w-full min-h-screen flex flex-col relative overflow-hidden bg-gradient-to-br from-[#f5f7ff] to-[#c3cfe2] font-inter">
      <ToastProvider
        position="bottom-right"
        defaultDuration={5000}
        maxToasts={5}
      >
        <AppContent />
      </ToastProvider>
    </div>
  );
}
