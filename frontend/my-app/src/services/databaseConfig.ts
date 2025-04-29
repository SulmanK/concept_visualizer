/**
 * Database configuration service for Concept Visualizer
 *
 * This service manages database table names from environment variables,
 * allowing for dynamic switching between development and production tables.
 */

// Default table names for fallback
const DEFAULT_TABLE_NAMES = {
  tasks: "tasks",
  concepts: "concepts",
  colorVariations: "color_variations",
};

// Get table names from environment variables with fallbacks
export const DB_TABLE_NAMES = {
  tasks: import.meta.env.VITE_DB_TABLE_TASKS || DEFAULT_TABLE_NAMES.tasks,
  concepts:
    import.meta.env.VITE_DB_TABLE_CONCEPTS || DEFAULT_TABLE_NAMES.concepts,
  colorVariations:
    import.meta.env.VITE_DB_TABLE_COLOR_VARIATIONS ||
    DEFAULT_TABLE_NAMES.colorVariations,
};

/**
 * Get the name of a database table
 *
 * @param table The table identifier ('tasks', 'concepts', or 'colorVariations')
 * @returns The environment-specific table name
 */
export const getTableName = (table: keyof typeof DB_TABLE_NAMES): string => {
  return DB_TABLE_NAMES[table];
};

export default {
  getTableName,
  DB_TABLE_NAMES,
};
