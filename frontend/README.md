# CareerIQ Web

Next.js frontend for CareerIQ. See the repository root `README.md` for full
setup instructions.

```bash
cp .env.example .env.local
npm install
npm run dev     # http://localhost:3000
npm test        # vitest
npm run lint
npm run build
```

Design tokens live in `app/globals.css` and are derived from `DESIGN.md` at the
repository root. Do not hardcode colours in components.
