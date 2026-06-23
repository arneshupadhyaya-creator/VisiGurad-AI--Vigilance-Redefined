# Authentication Notes - JWT Session Strategy

This document details the architectural choices, security configurations, advantages, and future improvements for the VisiGuard AI authentication framework.

---

## Why JWT (JSON Web Tokens) Was Chosen

JWT was selected as the default session management strategy to enable stateless authentication in our React-Express monorepo structure.

### 1. Advantages
* **Stateless Scaling**: The backend does not need to store session states in database tables (or Redis) to verify user logins, reducing database load.
* **Decoupled Deployment Ready**: JWTs are highly portable, allowing future microservices (like a python service or external reporting suite) to verify requests simply by reading the signature using the shared secret.
* **Native SPA Integration**: Simple to store in memory or localStorage on the frontend, attaching as authorization headers with Axios interceptors.

### 2. Drawbacks & Mitigations
* **Revocation Complexity**: Because JWTs are stateless, they cannot be easily blacklisted before they expire.
  * *Mitigation*: We set a reasonable token lifespan (`24h` for development, to be reduced to `15m` in production combined with refresh tokens).
* **Storage Hazards**: LocalStorage is vulnerable to Cross-Site Scripting (XSS).
  * *Mitigation*: Implementation details for HTTP-only cookies are documented in the Security Guide for staging/production deployments.

---

## Refresh Token Architecture

To combine security with smooth user sessions, a future Refresh Token flow will be integrated:

```text
+-------------------+             +-----------------------+
|  React client     |             | Express server        |
+---------+---------+             +-----------+-----------+
          |                                   |
          |  1. POST /login                   |
          +---------------------------------->+ Hashes pwd, generates
          |                                   | AccessToken (15m, short-lived)
          |  2. Returns tokens                | RefreshToken (7d, db-stored)
          +<----------------------------------+
          |                                   |
          |  3. Call API (Bearer AccessToken) |
          +---------------------------------->+ Verifies sig (Stateless)
          |                                   |
          |  4. Token expires (401)           |
          +<----------------------------------+
          |                                   |
          |  5. POST /refresh (RefreshToken)  |
          +---------------------------------->+ Validates token in DB,
          |                                   | issues new AccessToken
          |  6. Returns new AccessToken       |
          +<----------------------------------+
```

### Refresh Token Schema
* Stored in a database table: `userId`, `token`, `expiresAt`, `deviceInfo`, `revoked`.
* AccessToken: Transmitted in standard Bearer headers.
* RefreshToken: Transmitted in an HTTP-only cookie.

---

## Future Alternatives
1. **Redis Sessions**: Transitioning to traditional stateful session cookies stored in a fast Redis cache. This allows instant revocation capability but requires maintaining a state database.
2. **OAuth2 / OpenID Connect**: Delegating logins to enterprise-grade OAuth providers (e.g. Auth0, Okta, Firebase Auth) using standard client libraries.
