# CI Integration & Test File Organization

## CI Integration (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 24
          cache: 'npm'
      - run: npm ci
      - run: npm run test:run

  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 24
          cache: 'npm'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npm run build
      - run: npx playwright test
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: playwright-report
          path: playwright-report/
```

## Test File Organization

```
src/
├── components/
│   ├── counter.tsx
│   └── __tests__/
│       └── counter.test.tsx
├── app/
│   └── actions/
│       ├── post-actions.ts
│       └── __tests__/
│           └── post-actions.test.ts
e2e/
├── auth.setup.ts
├── home.spec.ts
├── create-post.spec.ts
└── .auth/
    └── user.json          # gitignored
```

### Conventions

- Unit/component tests: colocate in `__tests__/` next to the source file
- E2E tests: top-level `e2e/` directory
- Auth state for Playwright: `e2e/.auth/` (add to `.gitignore`)
- Test files: `*.test.tsx` for Vitest, `*.spec.ts` for Playwright
