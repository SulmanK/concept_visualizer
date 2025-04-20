# RefinementActions

The RefinementActions component provides a set of action buttons for managing refinement operations such as saving, exporting, and discarding changes.

## Overview

This component renders a set of action buttons that allow users to save their refined concepts, export them in various formats, or discard the refinement process. It typically appears at the bottom of the refinement page and provides an interface for finalizing the refinement workflow.

## Component Structure

```tsx
interface RefinementActionsProps {
  onSave: () => void;
  onExport: () => void;
  onDiscard: () => void;
  isSaving?: boolean;
  isExporting?: boolean;
  disableSave?: boolean;
  disableExport?: boolean;
}

const RefinementActions: React.FC<RefinementActionsProps> = ({
  onSave,
  onExport,
  onDiscard,
  isSaving = false,
  isExporting = false,
  disableSave = false,
  disableExport = false,
}) => {
  return (
    <div className="refinement-actions">
      <div className="action-buttons">
        <Button
          variant="secondary"
          onClick={onDiscard}
          className="discard-button"
        >
          Discard Changes
        </Button>
        
        <div className="primary-actions">
          <Button
            variant="secondary"
            onClick={onExport}
            isLoading={isExporting}
            disabled={disableExport || isExporting}
            icon="download"
            className="export-button"
          >
            Export
          </Button>
          
          <Button
            variant="primary"
            onClick={onSave}
            isLoading={isSaving}
            disabled={disableSave || isSaving}
            icon="save"
            className="save-button"
          >
            Save
          </Button>
        </div>
      </div>
      
      <div className="action-info">
        <p className="info-text">
          <Icon name="info" size="small" />
          Saving will store this refined concept in your account. 
          Exporting will download the concept in your preferred format.
        </p>
      </div>
    </div>
  );
};
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `onSave` | `() => void` | Yes | - | Callback when save button is clicked |
| `onExport` | `() => void` | Yes | - | Callback when export button is clicked |
| `onDiscard` | `() => void` | Yes | - | Callback when discard button is clicked |
| `isSaving` | `boolean` | No | false | Whether save operation is in progress |
| `isExporting` | `boolean` | No | false | Whether export operation is in progress |
| `disableSave` | `boolean` | No | false | Whether save button should be disabled |
| `disableExport` | `boolean` | No | false | Whether export button should be disabled |

## Features

- **Save Action**: Button to save the refined concept
- **Export Action**: Button to export the concept in various formats
- **Discard Action**: Button to discard refinement changes
- **Loading States**: Visual indication of save/export operations in progress
- **Disabled States**: Proper handling of when actions should be disabled
- **Informational Text**: Helper text explaining the actions
- **Visual Icons**: Icon indicators for each action type

## Dependencies

- `Button`: Button component for action buttons
- `Icon`: Icon component for button and info icons

## Styling

- **Button Grouping**: Clear visual grouping of related actions
- **Consistent Button Styles**: Follows the application's button styling patterns
- **Visual Hierarchy**: Primary action (save) is visually distinct
- **Responsive Layout**: Adapts to different screen sizes
- **Loading Indicators**: Clear visual feedback during operations

## Related Components

- [RefinementPage](../RefinementPage.md)
- [RefinementForm](./RefinementForm.md)

## Accessibility

- Buttons have descriptive text
- Loading states are properly communicated
- Disabled states have proper ARIA attributes
- Icon buttons have text labels

## Usage Example

```tsx
const RefinementPage: React.FC = () => {
  const router = useRouter();
  const { mutate: saveConcept, isPending: isSaving } = useConceptMutations.useSaveConcept();
  const { mutate: exportConcept, isPending: isExporting } = useConceptMutations.useExportConcept();
  
  const handleSave = useCallback(() => {
    saveConcept({ conceptId: 'concept-123' }, {
      onSuccess: () => {
        // Handle success
      },
    });
  }, [saveConcept]);
  
  const handleExport = useCallback(() => {
    exportConcept({ conceptId: 'concept-123', format: 'png' }, {
      onSuccess: (data) => {
        // Handle download
      },
    });
  }, [exportConcept]);
  
  const handleDiscard = useCallback(() => {
    // Show confirmation dialog
    if (window.confirm('Are you sure you want to discard your changes?')) {
      router.push('/concepts');
    }
  }, [router]);
  
  return (
    <div className="refinement-page">
      {/* Refinement content */}
      
      <RefinementActions
        onSave={handleSave}
        onExport={handleExport}
        onDiscard={handleDiscard}
        isSaving={isSaving}
        isExporting={isExporting}
      />
    </div>
  );
};
```

## Behavior

- **Save Button**: Saves the current state of the refinement
- **Export Button**: Initiates an export process for the current concept
- **Discard Button**: Discards changes, typically with a confirmation dialog
- **Loading State**: Buttons show loading indicators during operations
- **Disabled State**: Buttons are disabled when operations are not possible 