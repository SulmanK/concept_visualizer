/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_SUPABASE_URL: string;
  readonly VITE_SUPABASE_ANON_KEY: string;
  readonly VITE_APP_ENV: string;

  // Database table names
  readonly VITE_DB_TABLE_TASKS: string;
  readonly VITE_DB_TABLE_CONCEPTS: string;
  readonly VITE_DB_TABLE_COLOR_VARIATIONS: string;

  // Feature flags
  readonly VITE_ENABLE_DEBUG_TOOLS: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
