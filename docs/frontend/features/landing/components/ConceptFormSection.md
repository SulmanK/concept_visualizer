# ConceptFormSection

The ConceptFormSection component renders a user-friendly form for creating new concept visualizations on the landing page.

## Overview

This component provides the primary interface for users to input their concept description and generate visualizations. It includes form fields, validation, and submission handling.

## Component Structure

```tsx
const ConceptFormSection: React.FC = () => {
  const router = useRouter();
  const { mutate, isPending } = useConceptMutations.useCreateConcept();
  const [formData, setFormData] = useState<CreateConceptFormData>({
    logoDescription: "",
    themeDescription: "",
  });
  const [validationErrors, setValidationErrors] = useState<
    Record<string, string>
  >({});

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();

      // Validate form data
      const errors = validateConceptForm(formData);
      if (Object.keys(errors).length > 0) {
        setValidationErrors(errors);
        return;
      }

      // Submit to API
      mutate(formData, {
        onSuccess: (data) => {
          router.push(`/concepts/${data.conceptId}`);
        },
      });
    },
    [formData, mutate, router],
  );

  return (
    <section className="concept-form-section">
      <h2>Create Your Concept</h2>
      <p className="section-description">
        Describe your brand concept and we'll generate visual representations
      </p>

      <form onSubmit={handleSubmit}>
        <div className="form-fields">
          <div className="form-group">
            <label htmlFor="logoDescription">Logo Description</label>
            <TextArea
              id="logoDescription"
              value={formData.logoDescription}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  logoDescription: e.target.value,
                })
              }
              placeholder="Describe your ideal logo..."
              rows={4}
              error={validationErrors.logoDescription}
            />
          </div>

          <div className="form-group">
            <label htmlFor="themeDescription">Brand Theme</label>
            <TextArea
              id="themeDescription"
              value={formData.themeDescription}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  themeDescription: e.target.value,
                })
              }
              placeholder="Describe your brand's theme, colors, and style..."
              rows={4}
              error={validationErrors.themeDescription}
            />
          </div>
        </div>

        <Button
          type="submit"
          variant="primary"
          isLoading={isPending}
          disabled={isPending}
          className="submit-button"
        >
          Generate Concept
        </Button>
      </form>
    </section>
  );
};
```

## Props

This component does not accept any props as it's designed to be self-contained.

## Features

- **Input Validation**: Validates form fields before submission
- **Loading State**: Displays loading indicator during submission
- **Error Handling**: Shows validation errors and API errors
- **Responsive Design**: Adapts to different screen sizes

## Dependencies

- `TextArea`: Text input component for multiline text
- `Button`: Button component for form submission
- `useCreateConcept`: React Query mutation hook for API interaction
- `validateConceptForm`: Utility function for form validation
- `useRouter`: Router hook for navigation after submission

## Types

```tsx
interface CreateConceptFormData {
  logoDescription: string;
  themeDescription: string;
}
```

## State Management

- Local state for form values and validation errors
- React Query for mutation state (loading, success, error)

## Related Components

- [TextArea](../../../../components/ui/TextArea.md)
- [Button](../../../../components/ui/Button.md)
- [ConceptHeader](./ConceptHeader.md)
- [LandingPage](../LandingPage.md)

## Accessibility

- Form fields have proper labels
- Error messages are associated with form fields
- Loading state is communicated to screen readers
- Focus management during form submission
