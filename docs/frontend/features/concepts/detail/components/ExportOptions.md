# ExportOptions Component

## Overview

The `ExportOptions` component provides a user interface for exporting concept images in various formats and sizes. It allows users to preview, download, and copy links to exported images, handling all the complexity of image processing and format conversions.

## Component Details

- **File Path**: `frontend/my-app/src/features/concepts/detail/components/ExportOptions.tsx`
- **Type**: React Functional Component

## Props

| Prop                | Type                  | Required | Default     | Description                                      |
|---------------------|----------------------|----------|-------------|--------------------------------------------------|
| `imageUrl`          | `string \| undefined` | Yes      | -           | URL of the image to process and download         |
| `storagePath`       | `string`              | No       | -           | Storage path of the image (extracted from URL if not provided) |
| `conceptTitle`      | `string`              | Yes      | -           | Title/name of the concept                        |
| `variationName`     | `string`              | No       | `''`        | Variation name (for color variations)            |
| `isPaletteVariation`| `boolean`            | No       | `false`     | Indicates if this is a palette variation         |
| `onDownload`        | `(format: ExportFormat, size: ExportSize) => void` | No | - | Callback when download button is clicked |

## Features

- **Multiple Export Formats**: Supports PNG, JPG, and SVG formats
- **Size Options**: Small (256px), Medium (512px), Large (1024px), or Original size
- **Live Preview**: Shows a preview of the exported image before download
- **Enhanced Preview**: Includes zoomable preview in a modal dialog
- **Copy to Clipboard**: Option to copy the exported image URL
- **Error Handling**: Graceful handling of export errors, including rate limits
- **Progress Indicators**: Loading states during export processing

## Implementation Details

### Export Formats

The component supports the following export formats:
- **PNG**: Lossless format with transparency support
- **JPG**: Compressed format for smaller file sizes
- **SVG**: Vector format for scalable graphics (when available)

### Size Options

Users can select from several size options:
- **Small**: 256px (suitable for thumbnails and icons)
- **Medium**: 512px (default, good for web usage)
- **Large**: 1024px (higher quality for presentations)
- **Original**: Maximum available quality

### API Integration

The component uses the `useExportImageMutation` hook to:
1. Send export requests to the backend API
2. Process the response and generate blob URLs
3. Handle downloading or previewing the exported image

### State Management

Several state variables track the component's operation:
- `selectedFormat`: Currently selected export format
- `selectedSize`: Currently selected export size
- `previewUrl`: URL for the current preview image
- `modalPreviewUrl`: URL for the full-screen preview modal
- `errorMessage`: Error message if export fails
- `copySuccess`: Flag when URL is successfully copied to clipboard

## Usage Example

```tsx
import { ExportOptions } from './components/ExportOptions';

const ConceptExport = ({ concept }) => {
  return (
    <div className="export-section">
      <h2>Export Options</h2>
      
      <ExportOptions
        imageUrl={concept.imageUrl}
        conceptTitle={concept.title || 'Concept'}
        variationName={concept.variation || ''}
        isPaletteVariation={Boolean(concept.variation)}
        onDownload={(format, size) => {
          console.log(`Downloading in ${format} format at ${size} size`);
        }}
      />
    </div>
  );
};
```

## Error Handling

The component provides comprehensive error handling for:
- Network failures
- Rate limit errors
- Processing errors
- Invalid image formats

## Resource Management

The component carefully manages resources by:
- Tracking and revoking blob URLs to prevent memory leaks
- Cleaning up resources when unmounting
- Using references to avoid unnecessary re-renders

## Related Components

- [`EnhancedImagePreview`](./EnhancedImagePreview.md) - Used for the full-screen preview modal
- [`ConceptDetailPage`](../ConceptDetailPage.md) - Parent component that integrates the export options 