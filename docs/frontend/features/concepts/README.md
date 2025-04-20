# Concepts Feature

The Concepts feature encompasses all functionality related to creating, viewing, and refining visual concepts.

## Structure

The Concepts feature is divided into two main sections:

- **detail**: Components for viewing and interacting with a single concept
  - `ConceptDetailPage`: Main component for displaying concept details
  - `EnhancedImagePreview`: Component for viewing concept images with additional controls
  - `ExportOptions`: Component for exporting concepts in various formats
- **recent**: Components for viewing and browsing recently created concepts
  - `RecentConceptsPage`: Main component for displaying recent concepts
  - `ConceptList`: Component for displaying a list of concepts
  - `RecentConceptsHeader`: Header component for the recent concepts page

## User Flows

### Concept Creation Flow

1. User navigates to the Landing page
2. User enters concept description
3. System generates concept image
4. User views the generated concept

### Concept Viewing Flow

1. User navigates to Recent Concepts page
2. User browses the list of recently created concepts
3. User selects a concept to view details
4. User can export, refine, or delete the concept

### Concept Refinement Flow

1. User views a concept
2. User requests refinement
3. User provides refinement instructions
4. System generates refined concept
5. User compares original and refined concepts

## Key Components

### ConceptDetailPage

The `ConceptDetailPage` component displays detailed information about a single concept, including:

- Concept image
- Generation details
- Color palette
- Export options
- Refinement options

### RecentConceptsPage

The `RecentConceptsPage` component displays a list of recently created concepts, with options to:

- Filter concepts
- Sort concepts
- Navigate to concept details
- Delete concepts

## Data Model

Concepts have the following key properties:

- `id`: Unique identifier
- `prompt`: Original text prompt used to generate the concept
- `imageUrl`: URL to the generated image
- `palette`: Color palette extracted from the image
- `createdAt`: Creation timestamp
- `userId`: ID of the user who created the concept
- `refinements`: Array of refinement objects associated with the concept 