# HB Track - Frontend (Phase 5 - Cycle 1)

React + TypeScript + Vite frontend for HB Track platform.

## Tech Stack

- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Routing**: React Router v6
- **State Management**: Zustand
- **API Client**: openapi-fetch (auto-generated from OpenAPI spec)
- **UI Framework**: Tailwind CSS
- **Testing**: Vitest + React Testing Library
- **HTTP Client**: axios

## Getting Started

### Prerequisites

- Node.js 16+ 
- npm or yarn

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

This starts the dev server on `http://localhost:5173` with proxy to backend API at `http://localhost:8000/api`.

### Build

```bash
npm run build
```

### Generate API Types

```bash
npm run api:generate
```

This commands regenerates `src/api/schema.d.ts` from `contracts/openapi/openapi.yaml`.

### Testing

```bash
npm run test
```

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts         # openapi-fetch client
│   │   └── schema.d.ts       # Generated OpenAPI types
│   ├── stores/
│   │   └── authStore.ts      # Zustand auth store
│   ├── features/
│   │   ├── auth/             # Auth module (Phase 5.3)
│   │   ├── users/            # Users module (Phase 5.4)
│   │   ├── teams/            # Teams module (Phase 5.5)
│   │   ├── seasons/          # Seasons module (Phase 5.6)
│   │   └── training/         # Training module (Phase 5.7)
│   ├── shared/
│   │   └── layouts/          # Layout components
│   ├── App.tsx               # Root component
│   └── main.tsx              # Entry point
├── public/                    # Static assets
├── vite.config.ts            # Vite configuration
├── tailwind.config.ts        # Tailwind configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies
```

## Phase 5 Roadmap

- **5.1** ✅ Bootstrap frontend (done)
- **5.2** ⏳ API client generation
- **5.3** ⏳ Auth module
- **5.4** ⏳ Users module
- **5.5** ⏳ Teams module
- **5.6** ⏳ Seasons module
- **5.7** ⏳ Training module
- **5.8** ⏳ Testing
- **5.9** ⏳ CI/CD integration
