# Validation Utilities

The `validationUtils.js` module provides functions for validating user input in forms and other contexts throughout the application.

## Overview

These utilities handle common validation patterns for form inputs, ensuring that data meets specific requirements before being sent to the backend.

## Functions

### `validateRequired(value)`

Validates that a value is not empty.

#### Parameters:

- `value` (string): The value to validate

#### Returns:

- `null` if the value is valid
- Error message string if the value is invalid

#### Example:

```js
const error = validateRequired("");
// Returns: 'This field is required'

const error = validateRequired("Hello");
// Returns: null
```

### `validateLength(value, minLength, maxLength)`

Validates that a string is within specified length constraints.

#### Parameters:

- `value` (string): The value to validate
- `minLength` (number, optional): Minimum required length
- `maxLength` (number, optional): Maximum allowed length

#### Returns:

- `null` if the value is valid
- Error message string if the value is invalid

#### Example:

```js
const error = validateLength("Hi", 3, 10);
// Returns: 'Must be at least 3 characters'

const error = validateLength("This is too long", 3, 10);
// Returns: 'Must be no more than 10 characters'
```

### `validateEmail(value)`

Validates that a string is a properly formatted email address.

#### Parameters:

- `value` (string): The email to validate

#### Returns:

- `null` if the email is valid
- Error message string if the email is invalid

#### Example:

```js
const error = validateEmail("not-an-email");
// Returns: 'Please enter a valid email address'

const error = validateEmail("user@example.com");
// Returns: null
```

### `validatePrompt(value)`

Specialized validator for concept generation prompts.

#### Parameters:

- `value` (string): The prompt to validate

#### Returns:

- `null` if the prompt is valid
- Error message string if the prompt is invalid

#### Example:

```js
const error = validatePrompt("");
// Returns: 'Please enter a description for your concept'

const error = validatePrompt("A minimalist logo");
// Returns: null
```

## Integration with Form Libraries

These utilities can be used with form libraries such as Formik or React Hook Form:

```jsx
import { useFormik } from "formik";
import { validateRequired, validateEmail } from "../utils/validationUtils";

function ContactForm() {
  const formik = useFormik({
    initialValues: {
      name: "",
      email: "",
      message: "",
    },
    validate: (values) => {
      const errors = {};

      const nameError = validateRequired(values.name);
      if (nameError) errors.name = nameError;

      const emailError = validateEmail(values.email);
      if (emailError) errors.email = emailError;

      const messageError = validateRequired(values.message);
      if (messageError) errors.message = messageError;

      return errors;
    },
    onSubmit: (values) => {
      // Submit form
    },
  });

  // Form JSX
}
```

## Creating Custom Validators

You can compose existing validators to create custom validation functions:

```js
import { validateRequired, validateLength } from "../utils/validationUtils";

function validateUsername(value) {
  const requiredError = validateRequired(value);
  if (requiredError) return requiredError;

  const lengthError = validateLength(value, 3, 20);
  if (lengthError) return lengthError;

  // Additional validation
  if (!/^[a-zA-Z0-9_]+$/.test(value)) {
    return "Username can only contain letters, numbers, and underscores";
  }

  return null;
}
```
