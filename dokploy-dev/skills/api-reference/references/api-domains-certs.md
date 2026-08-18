# API Reference: Domains, Certificates, Security, Redirects, Ports, Forward Auth

## Contents
- [Domain (9 endpoints)](#domain-9-endpoints)
- [Certificates (4 endpoints)](#certificates-4-endpoints)
- [Security (4 endpoints)](#security-4-endpoints)
- [Redirects (4 endpoints)](#redirects-4-endpoints)
- [Port (4 endpoints)](#port-4-endpoints)
- [Forward Auth (Application Authentication) (10 endpoints)](#forward-auth-application-authentication-10-endpoints)

## Domain (9 endpoints)

Domains map hostnames to applications and compose services via Traefik.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/domain.byApplicationId` | domain.byApplicationId | List domains for an application |
| GET | `/domain.byComposeId` | domain.byComposeId | List domains for a compose service |
| GET | `/domain.one` | domain.one | Get a single domain by ID |
| POST | `/domain.create` | domain.create | Create a new domain mapping |
| POST | `/domain.update` | domain.update | Update domain configuration |
| POST | `/domain.delete` | domain.delete | Remove a domain mapping |
| POST | `/domain.validateDomain` | domain.validateDomain | Check if a domain is valid and resolvable. Input: `domain` (the hostname string, NOT domainId), optional `serverIp` |
| POST | `/domain.generateDomain` | domain.generateDomain | Auto-generate a subdomain (traefik.me) |
| GET | `/domain.canGenerateTraefikMeDomains` | domain.canGenerateTraefikMeDomains | Check if traefik.me auto-domains are available |

### Key parameters

**domain.create**
```json
{
  "host": "string (required — e.g. app.example.com)",
  "path": "string (default: /)",
  "port": "number (default: 80 — container port to route to)",
  "https": "boolean (default: true)",
  "certificateType": "letsencrypt | none (default: letsencrypt)",
  "applicationId": "string (one of applicationId or composeId required)",
  "composeId": "string (one of applicationId or composeId required)",
  "serviceName": "string (required for compose — which service in the compose file)",
  "forwardAuthEnabled": "boolean (v0.29.8+, enterprise — gate this domain behind the server's forward-auth SSO)"
}
```

**domain.update**
```json
{
  "domainId": "string (required)",
  "host": "string",
  "path": "string",
  "port": "number",
  "https": "boolean",
  "certificateType": "string",
  "forwardAuthEnabled": "boolean (v0.29.8+, enterprise)"
}
```

**domain.byApplicationId**
- Query: `applicationId` (required)

**domain.byComposeId**
- Query: `composeId` (required)

---

## Certificates (4 endpoints)

Manage SSL/TLS certificates for custom domains.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/certificates.all` | certificates.all | List all certificates |
| GET | `/certificates.one` | certificates.one | Get a single certificate |
| POST | `/certificates.create` | certificates.create | Upload or create a certificate |
| POST | `/certificates.remove` | certificates.remove | Remove a certificate |

### Key parameters

**certificates.create**
```json
{
  "name": "string (required)",
  "certificateData": "string (PEM certificate content)",
  "privateKey": "string (PEM private key content)",
  "autoRenew": "boolean"
}
```

---

## Security (4 endpoints)

HTTP basic auth rules applied to domains.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/security.one` | security.one | Get security config for a resource |
| POST | `/security.create` | security.create | Add basic auth to a domain |
| POST | `/security.delete` | security.delete | Remove basic auth |
| POST | `/security.update` | security.update | Update basic auth credentials |

### Key parameters

**security.create**
```json
{
  "username": "string (required)",
  "password": "string (required)",
  "applicationId": "string (target resource)"
}
```

---

## Redirects (4 endpoints)

HTTP redirect rules configured in Traefik.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/redirects.one` | redirects.one | Get a redirect rule |
| POST | `/redirects.create` | redirects.create | Create a redirect rule |
| POST | `/redirects.delete` | redirects.delete | Delete a redirect rule |
| POST | `/redirects.update` | redirects.update | Update a redirect rule |

### Key parameters

**redirects.create**
```json
{
  "regex": "string (required — source URL pattern)",
  "replacement": "string (required — target URL)",
  "permanent": "boolean (default: false — 301 vs 302)",
  "applicationId": "string"
}
```

---

## Port (4 endpoints)

Expose additional container ports beyond the main service port.

| Method | Path | operationId | Description |
|--------|------|-------------|-------------|
| GET | `/port.one` | port.one | Get a port mapping |
| POST | `/port.create` | port.create | Add a port mapping |
| POST | `/port.delete` | port.delete | Remove a port mapping |
| POST | `/port.update` | port.update | Update a port mapping |

### Key parameters

**port.create**
```json
{
  "publishedPort": "number (required — host port)",
  "targetPort": "number (required — container port)",
  "protocol": "tcp | udp (default: tcp)",
  "applicationId": "string"
}
```

---

## Forward Auth (Application Authentication) (10 endpoints)

v0.29.8+ (enterprise). Traefik forward-auth powered by **oauth2-proxy**: put an SSO/OIDC login in front of any deployed application's domain **without changing app code**. Managed in the dashboard under **Settings → SSO → Application Authentication**.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/forwardAuth.listProviders` | List available SSO providers for forward-auth (no params) |
| POST | `/forwardAuth.setAuthDomain` | Set the auth domain on a server. Input: `serverId` (req), `authDomain` (req), `https`, `certificateType`, `customCertResolver` |
| GET | `/forwardAuth.getAuthDomain` | Read a server's auth domain. Input: `serverId` (req) |
| POST | `/forwardAuth.removeAuthDomain` | Remove a server's auth domain. Input: `serverId` (req) |
| POST | `/forwardAuth.deployOnServer` | Deploy the oauth2-proxy side-service on a server. Input: `serverId` (req), `providerId` (req) |
| POST | `/forwardAuth.removeOnServer` | Remove the forward-auth deployment from a server. Input: `serverId` (req) |
| GET | `/forwardAuth.serverStatus` | Forward-auth deployment status across servers (no params) |
| POST | `/forwardAuth.enable` | Gate one domain behind forward-auth. Input: `domainId` (req) |
| POST | `/forwardAuth.disable` | Ungate a domain. Input: `domainId` (req) |
| GET | `/forwardAuth.status` | Forward-auth state for one domain. Input: `domainId` (req) |

`domain.create` / `domain.update` accept `forwardAuthEnabled: boolean` to gate a domain at creation/update time.

### Typical flow

1. `forwardAuth.listProviders` → pick a `providerId`
2. `forwardAuth.setAuthDomain { serverId, authDomain, https, certificateType }`
3. `forwardAuth.deployOnServer { serverId, providerId }`
4. `forwardAuth.enable { domainId }` (per app domain to protect)
5. Verify: `forwardAuth.status { domainId }` / `forwardAuth.serverStatus`
