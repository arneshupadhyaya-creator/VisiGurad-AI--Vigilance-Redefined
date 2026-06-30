# Security Notes - Hardening and Best Practices

This document provides a comprehensive security assessment and future hardening checklist for VisiGuard AI.

---

## Token Storage Strategies

### 1. LocalStorage (Current Development Mode)
* **Risk**: Vulnerable to Cross-Site Scripting (XSS). If a malicious script runs on the page (e.g. through third-party dependencies or injected content), it can access `localStorage.getItem('token')`.
* **Benefit**: Zero-configuration setup, works out-of-the-box for SPAs, easily bypasses CORS during cross-domain local development.

### 2. HTTP-only Cookies (Production Recommended)
For production environments, the frontend must receive the JWT inside a `Set-Cookie` header:
* **Flags**:
  * `HttpOnly`: Prevents client-side Javascript scripts from reading the cookie.
  * `Secure`: Forces transmission only over encrypted HTTPS links.
  * `SameSite=Strict`: Restricts cookie attachments on cross-origin requests, completely mitigating CSRF attacks.

---

## Cross-Site Scripting (XSS) Mitigation
To protect the dashboard and forms from XSS:
* **React Rendering**: React automatically escapes strings rendered in the virtual DOM. We strictly avoid `dangerouslySetInnerHTML`.
* **Helmet Middleware**: Install `helmet` on the backend to append secure HTTP response headers (Content-Security-Policy, Frame-Options, X-Content-Type-Options).
* **Sanitization**: Standard sanitize input strings to strip HTML elements.

---

## Cross-Site Request Forgery (CSRF) Mitigation
* Since our current authentication uses bearer authorization headers (`Authorization: Bearer <JWT>`), **it is immune to CSRF** because browsers do not automatically attach auth headers to requests (unlike cookies).
* If switching to cookie storage, a double-submit CSRF token framework (or configuring `SameSite=Lax` / `SameSite=Strict` cookies) must be configured.

---

## Password Hashing Strategy
* **Algorithm**: `bcryptjs`
* **Salt Rounds**: 10
* **Data Flow**: Plaintext passwords are intercepted in `authService`, hashed, and saved to MongoDB. The database never logs or preserves plaintext passwords.

---

## Hardening Checklist
* [ ] Enforce Content-Security-Policy (CSP) header values.
* [ ] Implement HTTPS TLS certs (e.g. Let's Encrypt) on the production reverse-proxy (Nginx).
* [ ] Reduce JWT expiration to `15 minutes`.
* [ ] Regularly run `npm audit` to check for compromised node modules.
