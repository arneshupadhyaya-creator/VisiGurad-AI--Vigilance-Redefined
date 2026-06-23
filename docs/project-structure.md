# Monorepo Project Structure

VisiGuard AI is organized as a scalable monorepo, separating frontend components, backend services, shared contract definitions, and ML computational blocks.

---

## Workspace Map

```text
VisiGuard-AI/
│
├── apps/
│   ├── backend/             # Node.js + Express web API
│   │   ├── src/
│   │   │   ├── audit/       # Security event logger middleware/services
│   │   │   ├── config/      # MongoDB configuration files
│   │   │   ├── controllers/ # Route handlers (auth, scan controllers)
│   │   │   ├── middlewares/ # Rate limiters, JWT authorization, error handlers
│   │   │   ├── models/      # Mongoose models (User, Scan, AuditLog schemas)
│   │   │   ├── monitoring/  # Observability/metrics monitoring classes
│   │   │   ├── repositories/# Database abstract query layer
│   │   │   ├── routes/      # Express API endpoint maps
│   │   │   ├── services/    # Business services (auth, ELA processor, queues)
│   │   │   └── storage/     # Storage abstraction providers (Local, S3, Azure)
│   │   └── index.js         # Backend application entry point
│   │
│   └── frontend/            # React + Vite + Tailwind CSS client
│       ├── src/
│       │   ├── components/  # Reusable UI elements (Navbar, Footer, Hero)
│       │   ├── contexts/    # Global AuthContext API
│       │   ├── hooks/       # Custom hooks (useAuth)
│       │   ├── pages/       # Page components (Home, Login, Register, Dashboard, Docs)
│       │   ├── routes/      # ProtectedRoute component guards
│       │   └── services/    # Axios API client services
│
├── shared/
│   └── contracts/           # Common Zod schema validators
│
├── docs/                    # Extensive developer documentation files
├── tests/                   # Jest and Vitest test spec templates
└── ML/                      # Core Error Level Analysis Python code
```

---

## Decoupled Project Philosophy
Each folder is strictly self-contained. The `frontend/` app only communicates with `backend/` via standard REST endpoints validated by `shared/contracts/`, making it simple to swap the React application with a native mobile client or migrate backend services to a microservice mesh.
