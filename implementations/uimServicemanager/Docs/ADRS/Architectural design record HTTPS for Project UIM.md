Architectural design record HTTPS for Project UIM-protocol

Date: 19/11/2025

Writer: Rik Heerholtz

**Enabling HTTPS for the Catalogue Service**

**Context:**  
The catalogue service exposes API endpoints that may be consumed by external agents, internal tools, and potentially third-party services. These requests often contain sensitive metadata or configuration details. To ensure confidentiality, integrity, and trustworthiness of the communication, the service requires a secure transport layer. Relying on plain HTTP would leave data vulnerable to interception, tampering, or unauthorized access.

**Decision:**  
HTTPS (HTTP over TLS) was enabled as the default transport protocol for the catalogue service.

**Rationale:**

- **Confidentiality:** HTTPS encrypts all traffic between clients and the service, preventing attackers from reading or intercepting sensitive data.
- **Integrity:** TLS ensures that data cannot be modified or tampered with in transit without detection.
- **Authentication:** Using trusted certificates allows clients to verify the identity of the service and avoid man-in-the-middle attacks.
- **Security compliance:** Modern standards, browsers, and API clients expect encrypted communication by default; HTTP-only APIs are considered insecure.
- **Future-proofing:** Many advanced features (e.g., service-to-service auth, OAuth flows, secure cookies, cross-service tokens) require HTTPS to function correctly.

**Consequences:**

- **Positive:** Secure communication, improved reliability, client trust, compliance with modern security practices, and compatibility with advanced authentication mechanisms.
- **Negative:** Requires managing TLS certificates (self-signed, Let's Encrypt, or internal CA) and configuring reverse proxies such as Nginx or Traefik; slightly more overhead in setup.
- **Mitigation:** Automate certificate renewal (e.g., Certbot), use Dockerized reverse proxies for consistent deployment, and maintain dev certificates for local testing.

**Sources:**

- "Why HTTPS Matters" - Google Developers  
    <https://developers.google.com/web/fundamentals/security/encrypt-in-transit/why-https-matters>
- "What is HTTPS?" - Cloudflare  
    <https://www.cloudflare.com/learning/ssl/what-is-https/>
- "HTTP vs HTTPS: Difference and Importance" - SSL.com  
    <https://www.ssl.com/faqs/what-is-the-difference-between-http-and-https/>
- "Transport Layer Security (TLS) Overview" - Mozilla MDN  
    <https://developer.mozilla.org/en-US/docs/Web/Security/Transport_Layer_Security>