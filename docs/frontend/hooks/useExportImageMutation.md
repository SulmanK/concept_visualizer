# useExportImageMutation Hook

The `useExportImageMutation` hook provides functionality for exporting concept images in various formats.

## Overview

This hook handles the API interaction and state management for exporting concept images. It allows users to download concept images in different formats and resolutions, with support for transparent backgrounds and other export options.

## Usage

```tsx
import { useExportImageMutation } from "hooks/useExportImageMutation";

function ExportButton({ conceptId }) {
  const { mutate, isPending } = useExportImageMutation();

  const handleExport = () => {
    mutate(
      {
        conceptId,
        format: "png",
        size: "original",
        includeBackground: false,
      },
      {
        onSuccess: (data) => {
          // Trigger download using the URL from the response
          window.open(data.downloadUrl, "_blank");
        },
      },
    );
  };

  return (
    <button
      onClick={handleExport}
      disabled={isPending}
      className="export-button"
    >
      {isPending ? "Exporting..." : "Export PNG"}
    </button>
  );
}
```

## API

### Parameters

The `mutate` function accepts:

| Parameter | Type                 | Required | Description                  |
| --------- | -------------------- | -------- | ---------------------------- |
| `data`    | `ExportImageRequest` | Yes      | Export options               |
| `options` | `MutateOptions`      | No       | React Query mutation options |

```tsx
interface ExportImageRequest {
  conceptId: string; // ID of the concept to export
  format: ImageFormat; // Export format
  size?: ImageSize; // Output size
  quality?: number; // Quality (for JPEG/WebP, 1-100)
  includeBackground?: boolean; // Whether to include background
  backgroundColor?: string; // Background color (hex/rgba, if including background)
  fileName?: string; // Custom filename for download
}

type ImageFormat = "png" | "jpeg" | "webp" | "svg";
type ImageSize = "original" | "large" | "medium" | "small" | "custom";
```

### Return Value

The hook returns a React Query mutation result with these properties:

| Property      | Type                                                                                  | Description                            |
| ------------- | ------------------------------------------------------------------------------------- | -------------------------------------- |
| `mutate`      | `(data: ExportImageRequest, options?: MutateOptions) => void`                         | Function to trigger the export         |
| `mutateAsync` | `(data: ExportImageRequest, options?: MutateOptions) => Promise<ExportImageResponse>` | Async version of mutate                |
| `isPending`   | `boolean`                                                                             | `true` while the export is in progress |
| `isSuccess`   | `boolean`                                                                             | `true` if the export succeeded         |
| `isError`     | `boolean`                                                                             | `true` if the export failed            |
| `error`       | `Error \| null`                                                                       | Error object if the export failed      |
| `data`        | `ExportImageResponse \| undefined`                                                    | Response data if successful            |

```tsx
interface ExportImageResponse {
  downloadUrl: string; // URL to download the exported image
  format: ImageFormat; // Format of the exported image
  fileName: string; // Filename for the download
  fileSizeBytes: number; // Size of the exported file in bytes
  expiration?: string; // When the download URL expires
}
```

## Examples

### Exporting in Different Formats

```tsx
function ExportOptions({ conceptId }) {
  const { mutate, isPending } = useExportImageMutation();

  const exportAs = (format: ImageFormat) => {
    mutate({
      conceptId,
      format,
      fileName: `concept-${conceptId}-export`,
    });
  };

  return (
    <div className="export-options">
      <h3>Export Format</h3>
      <div className="button-group">
        <button onClick={() => exportAs("png")} disabled={isPending}>
          PNG
        </button>
        <button onClick={() => exportAs("jpeg")} disabled={isPending}>
          JPEG
        </button>
        <button onClick={() => exportAs("svg")} disabled={isPending}>
          SVG
        </button>
      </div>
      {isPending && <span>Preparing export...</span>}
    </div>
  );
}
```

### Advanced Export Dialog

```tsx
function AdvancedExportDialog({ conceptId, onClose }) {
  const [options, setOptions] = useState({
    format: "png" as ImageFormat,
    size: "original" as ImageSize,
    includeBackground: true,
    backgroundColor: "#ffffff",
    quality: 90,
  });

  const { mutate, isPending, isSuccess } = useExportImageMutation();

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate(
      {
        conceptId,
        ...options,
      },
      {
        onSuccess: () => {
          // Close dialog after successful export
          setTimeout(onClose, 1500);
        },
      },
    );
  };

  return (
    <dialog className="export-dialog" open>
      <h2>Export Options</h2>
      <form onSubmit={handleSubmit}>
        {/* Format options */}
        <div className="form-group">
          <label>Format</label>
          <select
            value={options.format}
            onChange={(e) =>
              setOptions({
                ...options,
                format: e.target.value as ImageFormat,
              })
            }
          >
            <option value="png">PNG (Transparent)</option>
            <option value="jpeg">JPEG</option>
            <option value="webp">WebP</option>
            <option value="svg">SVG (Vector)</option>
          </select>
        </div>

        {/* More options for size, background, etc. */}

        <div className="dialog-actions">
          <button type="button" onClick={onClose}>
            Cancel
          </button>
          <button type="submit" disabled={isPending} className="primary-button">
            {isPending ? "Exporting..." : "Export"}
          </button>
        </div>

        {isSuccess && (
          <div className="success-message">
            Export complete! Download started.
          </div>
        )}
      </form>
    </dialog>
  );
}
```

## Implementation Details

This hook:

1. Sends the export request to the backend API
2. Tracks loading state during the export process
3. Provides the download URL for the exported image
4. Handles errors that might occur during export

The backend processing may include:

- Converting the image to the requested format
- Resizing the image as requested
- Handling transparency (for PNG) or background color
- Generating a temporary download URL

## Related Hooks

- [useConceptQueries](./useConceptQueries.md) - For fetching concept data
- [useConceptMutations](./useConceptMutations.md) - For creating and updating concepts
