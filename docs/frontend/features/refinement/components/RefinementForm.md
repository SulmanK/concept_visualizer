# RefinementForm

The RefinementForm component provides a form interface for users to specify how they want to refine their concept.

## Overview

This component presents a structured form that allows users to input additional feedback, specify elements to preserve, and list specific change requests for concept refinement. It helps guide users to provide effective feedback that will lead to better refinement results.

## Component Structure

```tsx
interface RefinementFormData {
  additionalFeedback: string;
  preserveElements: string[];
  changeRequests: string[];
}

interface RefinementFormProps {
  formData: RefinementFormData;
  onChange: (data: RefinementFormData) => void;
  onSubmit: (e: React.FormEvent) => void;
  isSubmitting: boolean;
  originalPrompt: string;
}

const RefinementForm: React.FC<RefinementFormProps> = ({
  formData,
  onChange,
  onSubmit,
  isSubmitting,
  originalPrompt,
}) => {
  const addPreserveElement = useCallback(() => {
    onChange({
      ...formData,
      preserveElements: [...formData.preserveElements, ''],
    });
  }, [formData, onChange]);
  
  const updatePreserveElement = useCallback((index: number, value: string) => {
    const newPreserveElements = [...formData.preserveElements];
    newPreserveElements[index] = value;
    onChange({
      ...formData,
      preserveElements: newPreserveElements,
    });
  }, [formData, onChange]);
  
  const removePreserveElement = useCallback((index: number) => {
    onChange({
      ...formData,
      preserveElements: formData.preserveElements.filter((_, i) => i !== index),
    });
  }, [formData, onChange]);
  
  // Similar methods for change requests...
  
  return (
    <form onSubmit={onSubmit} className="refinement-form">
      <div className="form-section">
        <h3>Original Prompt</h3>
        <div className="original-prompt">
          <p>{originalPrompt}</p>
        </div>
      </div>
      
      <div className="form-section">
        <h3>Additional Feedback</h3>
        <TextArea
          value={formData.additionalFeedback}
          onChange={(e) => onChange({
            ...formData,
            additionalFeedback: e.target.value,
          })}
          placeholder="Provide overall feedback about the concept..."
          rows={4}
        />
      </div>
      
      <div className="form-section">
        <div className="section-header">
          <h3>Elements to Preserve</h3>
          <Button
            type="button"
            variant="secondary"
            size="small"
            onClick={addPreserveElement}
            icon="plus"
          >
            Add Element
          </Button>
        </div>
        
        {formData.preserveElements.map((element, index) => (
          <div key={`preserve-${index}`} className="list-item">
            <Input
              value={element}
              onChange={(e) => updatePreserveElement(index, e.target.value)}
              placeholder="Element to preserve..."
            />
            <Button
              type="button"
              variant="icon"
              onClick={() => removePreserveElement(index)}
              icon="trash"
              aria-label="Remove element"
            />
          </div>
        ))}
        
        {formData.preserveElements.length === 0 && (
          <p className="help-text">
            Specify elements you want to keep in the refined version.
          </p>
        )}
      </div>
      
      {/* Similar section for change requests */}
      
      <div className="form-actions">
        <Button
          type="submit"
          variant="primary"
          isLoading={isSubmitting}
          disabled={isSubmitting}
        >
          Generate Refined Concept
        </Button>
      </div>
    </form>
  );
};
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `formData` | `RefinementFormData` | Yes | - | Current form data values |
| `onChange` | `(data: RefinementFormData) => void` | Yes | - | Callback when form data changes |
| `onSubmit` | `(e: React.FormEvent) => void` | Yes | - | Callback when form is submitted |
| `isSubmitting` | `boolean` | Yes | - | Whether form submission is in progress |
| `originalPrompt` | `string` | Yes | - | The original prompt used for concept generation |

## Features

- **Original Prompt Display**: Shows the original prompt for reference
- **Additional Feedback**: Text area for general feedback
- **Preserve Elements List**: Dynamic list of elements to preserve
- **Change Requests List**: Dynamic list of specific changes to make
- **Add/Remove Controls**: Buttons to add or remove list items
- **Form Validation**: Validates input before submission
- **Loading State**: Shows loading state during submission

## Dependencies

- `TextArea`: Text input component for multiline text
- `Input`: Text input component for single-line text
- `Button`: Button component for actions

## Types

```tsx
interface RefinementFormData {
  additionalFeedback: string;
  preserveElements: string[];
  changeRequests: string[];
}
```

## State Management

- Form data managed by parent component
- Local state for UI interactions

## Related Components

- [RefinementPage](../RefinementPage.md)
- [ComparisonView](./ComparisonView.md)

## Accessibility

- Form inputs have proper labels
- Dynamic lists have proper ARIA attributes
- Interactive elements are keyboard accessible
- Error states are properly communicated

## Usage Example

```tsx
const RefinementPageContent: React.FC = () => {
  const [formData, setFormData] = useState<RefinementFormData>({
    additionalFeedback: '',
    preserveElements: [],
    changeRequests: [],
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Submit refinement request
  };
  
  return (
    <div className="refinement-container">
      <RefinementForm
        formData={formData}
        onChange={setFormData}
        onSubmit={handleSubmit}
        isSubmitting={false}
        originalPrompt="Original concept prompt text..."
      />
    </div>
  );
};
```

## Styling

- Form sections clearly separated
- List items have consistent styling
- Add/remove controls are visually distinguished
- Proper spacing between form elements 