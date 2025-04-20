# Card Component

The `Card` component is a flexible container that displays content with a consistent style, providing a clean and organized visual representation of information.

## Overview

The Card component extends Material-UI's Card component with additional styling and functionality, making it easier to create consistently styled content containers throughout the application. It provides options for elevation, hover effects, and click interactions.

## Usage

```tsx
import { Card } from 'components/ui/Card';

// Basic usage
<Card>
  <h3>Card Title</h3>
  <p>Card content goes here</p>
</Card>

// With hover and click functionality
<Card 
  hoverEffect 
  onClick={() => console.log('Card clicked')}
>
  <h3>Interactive Card</h3>
  <p>Click me!</p>
</Card>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `children` | `React.ReactNode` | - | Content to render inside the card |
| `className` | `string` | `''` | Additional CSS class to apply to the card |
| `elevation` | `number` | `1` | Shadow depth, higher values mean more raised appearance |
| `hoverEffect` | `boolean` | `false` | Whether to apply elevation increase on hover |
| `onClick` | `() => void` | - | Function to call when the card is clicked |
| `sx` | `SxProps<Theme>` | `{}` | MUI system props for additional styling |
| `variant` | `'outlined' \| 'elevation'` | `'elevation'` | Card variant style |

## Implementation Details

```tsx
import React from 'react';
import { 
  Card as MuiCard, 
  CardProps as MuiCardProps, 
  styled 
} from '@mui/material';
import { SxProps, Theme } from '@mui/material/styles';

interface CardProps extends Omit<MuiCardProps, 'onClick'> {
  children: React.ReactNode;
  className?: string;
  elevation?: number;
  hoverEffect?: boolean;
  onClick?: () => void;
  sx?: SxProps<Theme>;
  variant?: 'outlined' | 'elevation';
}

const StyledCard = styled(MuiCard, {
  shouldForwardProp: (prop) => prop !== 'hoverEffect',
})<{ hoverEffect?: boolean }>(({ theme, hoverEffect }) => ({
  transition: theme.transitions.create(['box-shadow', 'transform'], {
    duration: theme.transitions.duration.shorter,
  }),
  ...(hoverEffect && {
    '&:hover': {
      transform: 'translateY(-4px)',
      boxShadow: theme.shadows[4],
    },
  }),
}));

export function Card({
  children,
  className = '',
  elevation = 1,
  hoverEffect = false,
  onClick,
  sx = {},
  variant = 'elevation',
  ...rest
}: CardProps) {
  return (
    <StyledCard
      className={className}
      elevation={elevation}
      hoverEffect={hoverEffect}
      onClick={onClick}
      sx={{
        cursor: onClick ? 'pointer' : 'default',
        ...sx,
      }}
      variant={variant}
      {...rest}
    >
      {children}
    </StyledCard>
  );
}
```

## Features

- **Consistent Styling**: Follows the application's design system
- **Interactive Options**: Supports hover effects and click handlers
- **Flexible Content**: Can contain any type of content
- **Customizable Appearance**: Adjustable elevation and variant
- **Styling Extensions**: Supports MUI's `sx` prop for additional styling
- **Accessibility**: Maintains ARIA roles and states when interactive

## Usage Patterns

### Basic Information Card

```tsx
<Card>
  <CardContent>
    <Typography variant="h5" component="div">
      Card Title
    </Typography>
    <Typography variant="body2" color="text.secondary">
      Card description text with details about the content.
    </Typography>
  </CardContent>
</Card>
```

### Interactive Card with Image

```tsx
<Card 
  hoverEffect 
  onClick={() => navigate(`/concepts/${concept.id}`)}
  sx={{ maxWidth: 345 }}
>
  <CardMedia
    component="img"
    height="140"
    image={concept.imageUrl}
    alt={concept.name}
  />
  <CardContent>
    <Typography variant="h6">{concept.name}</Typography>
    <Typography variant="body2" color="text.secondary">
      {concept.description}
    </Typography>
  </CardContent>
</Card>
```

### Outlined Card

```tsx
<Card variant="outlined" sx={{ borderColor: 'primary.light' }}>
  <CardContent>
    <Typography variant="h6">Information Panel</Typography>
    <Typography variant="body2">
      Important information displayed in an outlined card.
    </Typography>
  </CardContent>
</Card>
```

### Card with Action Buttons

```tsx
<Card>
  <CardContent>
    <Typography variant="h6">Feature Card</Typography>
    <Typography variant="body2">
      Feature description and details.
    </Typography>
  </CardContent>
  <CardActions>
    <Button size="small">Learn More</Button>
    <Button size="small" color="primary">
      Try Now
    </Button>
  </CardActions>
</Card>
```

## Best Practices

1. Use cards to group related information and actions
2. Apply the `hoverEffect` only when the card is interactive (has an `onClick` handler)
3. Maintain consistent padding and spacing within cards
4. Use appropriate elevation levels based on the card's importance (higher elevation for more important content)
5. Include clear call-to-action elements in interactive cards 