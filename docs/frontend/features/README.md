# Features

This directory contains feature-specific components and logic, organized by domain.

## Structure

Features are organized into domain-specific directories:

- **concepts**: Features related to concept creation, viewing, and management
  - **detail**: Concept detail view and related components
  - **recent**: Recent concepts view and related components
- **landing**: Landing page and related components
- **refinement**: Concept refinement features and related components

## Architecture

Each feature is organized following a similar pattern:

- Top-level page components (e.g., `LandingPage.tsx`)
- Feature-specific components in a `components/` subdirectory
- Feature-specific hooks (if applicable)
- Feature-specific types (if applicable)

## Key Features

- **Concept Generation**: Create new visual concepts based on prompts
- **Concept Browsing**: View and browse previously created concepts
- **Concept Refinement**: Refine concepts through iterative prompting
- **Concept Export**: Export concepts in various formats 