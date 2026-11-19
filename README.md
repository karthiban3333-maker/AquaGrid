# 💧 AquaGrid — Spring Intelligence Workspace

> **Offline-first spring monitoring, hydrogeological mapping, and decision-support workspace for sustainable groundwater and rural water grid management.**

AquaGrid is an advanced hydrogeological intelligence and decision-support platform designed for spring shed revitalization and water security. It empowers field facilitators, hydrogeologists, and regional planners to capture field observations offline, analyze geospatial recharge zones, calculate transparent vulnerability and priority scoring, trace groundwater recharge pathways, and execute human-validated water conservation interventions.

---

## ✨ Features

- 🛰️ **Geospatial & Hydrogeological Mapping** — Interactive GIS mapping powered by Leaflet, Turf.js, and Google Maps API to visualize spring catchments, digital elevation models (DEM), and recharge zones.
- 📶 **Offline-First Field Capture** — Resilient offline observation logging with local device sync queues and uncertainty preservation for remote fieldwork.
- 🧠 **Decision Lab & Scoring Engine** — Transparent, rules-based priority and vulnerability scoring evaluating discharge rates, seasonal variation, water quality, and community dependency.
- 🌊 **Groundwater Recharge Simulation** — Animated recharge pathway tracers and hydrogeological flow vectors indicating subsurface water movement and catchment dynamics.
- 📋 **Spring Registry & Inventory** — Centralized catalog tracking baseline discharge, historical water quality, geo-coordinates, and catchment classifications.
- 📊 **Monitoring & Comparative Analytics** — Time-series monitoring comparing pre- and post-intervention discharge and water table baselines using Recharts.
- 🔐 **Multi-Role Access Control** — Granular role management for Field Facilitators, Hydrogeologists, Regional Administrators, and Public Visitors.
- 🚀 **Full-Stack Type Safety** — End-to-end type safety with TypeScript, tRPC, Drizzle ORM, and Zod schemas.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend Framework** | React 19 + TypeScript + Vite |
| **Routing & State** | Wouter + TanStack React Query v5 |
| **Styling & UI** | Tailwind CSS v4, Radix UI Primitives, Lucide React, Framer Motion |
| **Charts & Visuals** | Recharts, Embla Carousel |
| **Geospatial / GIS** | Turf.js, Google Maps API, Geo-Engine |
| **Backend API** | Node.js + Express + tRPC v11 |
| **Database & ORM** | MySQL / PostgreSQL via Drizzle ORM |
| **Authentication & Cloud** | Firebase Auth / Jose JWT + S3 SDK |
| **Testing & Tooling** | Vitest, Prettier, esbuild |

---

## 📁 Folder Structure

```
AquaGrid/
├── client/                     # Frontend client application
│   ├── public/                 # Static assets and icons
│   └── src/
│       ├── components/         # Reusable UI & GIS components (Radix + Tailwind)
│       ├── hooks/              # Custom React hooks (location, sync, sensors)
│       ├── lib/                # Client utilities and tRPC client setup
│       ├── pages/              # Views (Overview, Registry, Decision Lab, Capture)
│       └── App.tsx             # Root application & routing
├── server/                     # Backend API & service layer
│   ├── _core/                  # Express server bootstrap & middleware
│   ├── routers/                # tRPC routers (springs, observations, analytics)
│   └── services/               # Business logic, scoring engine, geo calculations
├── shared/                     # Shared types, Zod schemas, and contracts
├── drizzle/                    # Database migrations and schema definitions
├── geo-engine/                 # Geospatial analysis and catchment calculation modules
├── patches/                    # Package patches (pnpm)
├── Dockerfile                  # Container definition
├── docker-compose.yml          # Multi-container orchestration
├── drizzle.config.ts           # Drizzle ORM configuration
├── package.json                # Project dependencies and npm scripts
└── vite.config.ts              # Vite configuration
```

---

## 🚀 How to Install and Run

### Prerequisites
- [Node.js](https://nodejs.org/) (v20+ recommended)
- [pnpm](https://pnpm.io/) (`npm install -g pnpm`)
- MySQL or PostgreSQL database instance (optional for local mock mode)

### 1. Clone the Repository
```bash
git clone https://github.com/karthiban3333-maker/AquaGrid.git
cd AquaGrid
```

### 2. Install Dependencies
```bash
pnpm install --frozen-lockfile
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env` and configure credentials:
```bash
cp .env.example .env
```

### 4. Database Setup
```bash
pnpm db:push
```

### 5. Start Development Server
```bash
pnpm dev
```
The application will launch at `http://localhost:3000`.

### 6. Build & Test for Production
```bash
pnpm check      # TypeScript validation
pnpm test       # Run Vitest test suite
pnpm build      # Bundle frontend & backend
pnpm start      # Launch production build
```

---

## 📸 Screenshots

> _Add screenshots here._

---

## 📄 License

This project is proprietary and private. All rights reserved.

---

## 👨‍💻 Author

**Karthiban A** — [Kode Prime](https://github.com/karthiban3333-maker)
