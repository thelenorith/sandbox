# User Interface Standards

Standards for building accessible, consistent, and maintainable user interfaces.

## General Principles

1. **Accessibility first** - All users should be able to use the interface
2. **Consistency** - Similar elements should behave similarly
3. **Progressive enhancement** - Core functionality works without JavaScript
4. **Performance** - Fast load times and smooth interactions

## Accessibility (WCAG 2.1)

Follow [WCAG 2.1](https://www.w3.org/WAI/WCAG21/quickref/) guidelines at Level AA minimum.

### Perceivable

| Requirement | Implementation |
|-------------|----------------|
| Text alternatives | Alt text for images, labels for form fields |
| Captions | Video captions and transcripts |
| Color contrast | 4.5:1 for normal text, 3:1 for large text |
| Resizable text | Support 200% zoom without loss of functionality |

### Operable

| Requirement | Implementation |
|-------------|----------------|
| Keyboard accessible | All interactive elements reachable via keyboard |
| Focus visible | Clear focus indicators on interactive elements |
| Skip links | "Skip to main content" link for screen readers |
| No keyboard traps | Users can always navigate away |

### Understandable

| Requirement | Implementation |
|-------------|----------------|
| Language declared | `<html lang="en">` |
| Predictable navigation | Consistent layout across pages |
| Error identification | Clear error messages with suggestions |
| Labels and instructions | Form fields have visible labels |

### Robust

| Requirement | Implementation |
|-------------|----------------|
| Valid HTML | Use semantic HTML elements |
| ARIA when needed | Supplement HTML with ARIA attributes |
| Compatible | Works with assistive technologies |

### Semantic HTML

```html
<!-- Good: Semantic HTML -->
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/home">Home</a></li>
    <li><a href="/about">About</a></li>
  </ul>
</nav>

<main>
  <article>
    <h1>Page Title</h1>
    <p>Content...</p>
  </article>
</main>

<!-- Bad: Div soup -->
<div class="nav">
  <div class="nav-item" onclick="navigate()">Home</div>
</div>
```

### Focus Management

```css
/* Visible focus styles */
:focus {
  outline: 2px solid #005fcc;
  outline-offset: 2px;
}

/* Remove default only if providing custom */
button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 95, 204, 0.5);
}
```

## Component Design

### Component Structure

```
components/
├── Button/
│   ├── Button.tsx          # Component implementation
│   ├── Button.test.tsx     # Component tests
│   ├── Button.module.css   # Scoped styles
│   └── index.ts            # Public export
├── Form/
│   ├── Input.tsx
│   ├── Select.tsx
│   └── index.ts
└── Layout/
    ├── Header.tsx
    ├── Footer.tsx
    └── index.ts
```

### Component Guidelines

| Guideline | Rationale |
|-----------|-----------|
| Single responsibility | Each component does one thing well |
| Props over state | Prefer controlled components |
| Composition over inheritance | Build complex UIs from simple pieces |
| Explicit dependencies | Import what you need, export what you expose |

### Component API Design

```typescript
// Good: Clear, typed props with sensible defaults
interface ButtonProps {
  /** Button content */
  children: React.ReactNode;
  /** Visual variant */
  variant?: 'primary' | 'secondary' | 'danger';
  /** Size variant */
  size?: 'small' | 'medium' | 'large';
  /** Disabled state */
  disabled?: boolean;
  /** Click handler */
  onClick?: (event: React.MouseEvent) => void;
}

export function Button({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  onClick,
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
```

## Styling

### CSS Architecture

Use one of these established methodologies:

| Methodology | Description | Use When |
|-------------|-------------|----------|
| CSS Modules | Scoped CSS per component | Component libraries |
| Tailwind CSS | Utility-first CSS | Rapid development |
| BEM | Block Element Modifier naming | Traditional CSS |
| CSS-in-JS | Styles in JavaScript | Dynamic styling needs |

### Design Tokens

Use design tokens for consistency:

```css
:root {
  /* Colors */
  --color-primary: #005fcc;
  --color-secondary: #6c757d;
  --color-success: #28a745;
  --color-danger: #dc3545;
  --color-warning: #ffc107;

  /* Typography */
  --font-family-base: system-ui, -apple-system, sans-serif;
  --font-size-base: 1rem;
  --font-size-sm: 0.875rem;
  --font-size-lg: 1.25rem;
  --line-height-base: 1.5;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Borders */
  --border-radius: 0.25rem;
  --border-color: #dee2e6;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}
```

### Responsive Design

Design mobile-first with breakpoints:

```css
/* Mobile first (default styles) */
.container {
  padding: var(--spacing-md);
}

/* Tablet and up */
@media (min-width: 768px) {
  .container {
    padding: var(--spacing-lg);
  }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    margin: 0 auto;
  }
}
```

### Standard Breakpoints

| Name | Min Width | Typical Devices |
|------|-----------|-----------------|
| xs | 0 | Small phones |
| sm | 576px | Phones |
| md | 768px | Tablets |
| lg | 1024px | Small desktops |
| xl | 1280px | Large desktops |

## Forms

### Form Structure

```html
<form>
  <div class="form-group">
    <label for="email">Email address</label>
    <input
      type="email"
      id="email"
      name="email"
      required
      aria-describedby="email-help"
    >
    <small id="email-help" class="form-text">
      We'll never share your email.
    </small>
  </div>

  <div class="form-group">
    <label for="password">Password</label>
    <input
      type="password"
      id="password"
      name="password"
      required
      minlength="8"
      aria-describedby="password-requirements"
    >
    <small id="password-requirements" class="form-text">
      Minimum 8 characters.
    </small>
  </div>

  <button type="submit">Sign in</button>
</form>
```

### Form Validation

```typescript
// Client-side validation with clear feedback
function validateForm(data: FormData): ValidationResult {
  const errors: ValidationError[] = [];

  const email = data.get('email') as string;
  if (!email) {
    errors.push({
      field: 'email',
      message: 'Email is required',
    });
  } else if (!isValidEmail(email)) {
    errors.push({
      field: 'email',
      message: 'Please enter a valid email address',
    });
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}
```

### Error Display

```html
<!-- Error state -->
<div class="form-group has-error">
  <label for="email">Email address</label>
  <input
    type="email"
    id="email"
    aria-invalid="true"
    aria-describedby="email-error"
  >
  <span id="email-error" class="error-message" role="alert">
    Please enter a valid email address
  </span>
</div>
```

## Loading States

### Skeleton Loading

Show content placeholders during loading:

```css
.skeleton {
  background: linear-gradient(
    90deg,
    #f0f0f0 25%,
    #e0e0e0 50%,
    #f0f0f0 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

### Loading Indicators

| Type | Use When |
|------|----------|
| Skeleton | Loading content with known structure |
| Spinner | Short operations (< 3 seconds) |
| Progress bar | Operations with measurable progress |
| Inline loading | Loading within existing content |

### Loading Best Practices

| Do | Don't |
|----|-------|
| Show progress for long operations | Use spinners for everything |
| Maintain layout during loading | Show blank screens |
| Allow cancellation when possible | Block the entire UI |
| Provide feedback on completion | Leave users guessing |

## Performance

### Core Web Vitals Targets

| Metric | Target | Description |
|--------|--------|-------------|
| LCP | < 2.5s | Largest Contentful Paint |
| FID | < 100ms | First Input Delay |
| CLS | < 0.1 | Cumulative Layout Shift |

### Image Optimization

```html
<!-- Responsive images -->
<img
  src="image-800.jpg"
  srcset="
    image-400.jpg 400w,
    image-800.jpg 800w,
    image-1200.jpg 1200w
  "
  sizes="(max-width: 768px) 100vw, 800px"
  alt="Description"
  loading="lazy"
  decoding="async"
>
```

### Code Splitting

```typescript
// Lazy load components
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

## Testing

### What to Test

| Test Type | Focus |
|-----------|-------|
| Unit tests | Component logic, utilities |
| Integration tests | Component interactions |
| Accessibility tests | WCAG compliance |
| Visual regression | Style changes |

### Accessibility Testing

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('Button has no accessibility violations', async () => {
  const { container } = render(<Button>Click me</Button>);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Component Testing

```typescript
import { render, screen, fireEvent } from '@testing-library/react';

test('Button calls onClick when clicked', () => {
  const handleClick = jest.fn();
  render(<Button onClick={handleClick}>Click me</Button>);

  fireEvent.click(screen.getByRole('button'));

  expect(handleClick).toHaveBeenCalledTimes(1);
});

test('Button is disabled when disabled prop is true', () => {
  render(<Button disabled>Click me</Button>);

  expect(screen.getByRole('button')).toBeDisabled();
});
```

## Anti-Patterns

| Avoid | Preferred |
|-------|-----------|
| Divs with click handlers | Semantic buttons and links |
| Color-only indicators | Color + icon/text |
| Disabled buttons without explanation | Explain why action is unavailable |
| Auto-playing media | User-initiated playback |
| Infinite scroll without alternative | Provide pagination option |
| Carousel-only content | Accessible alternatives |
| Custom form controls | Native elements when possible |

## Industry References

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Web Docs](https://developer.mozilla.org/)
- [React Accessibility](https://reactjs.org/docs/accessibility.html)
- [Inclusive Components](https://inclusive-components.design/)
- [Web.dev](https://web.dev/)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
