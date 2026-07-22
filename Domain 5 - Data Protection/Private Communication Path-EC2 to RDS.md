# Private Communication Path: EC2 to RDS (MySQL/PostgreSQL)

An EC2 app connecting to an RDS instance is one of the most common internal paths in AWS, and the trap is assuming that because the traffic stays inside the VPC it is encrypted. It is not, by default. RDS accepts both encrypted and unencrypted connections, and unless the client explicitly requests TLS (JDBC flags, `sslmode`, driver options), the connection to port 3306 (MySQL) or 5432 (PostgreSQL) is plaintext even on a private subnet. Private networking is not encryption. The thing to hold onto: TLS to RDS is client-configured by default, you enforce it server-side per engine (`rds.force_ssl=1` for PostgreSQL, `require_secure_transport=ON` for MySQL) via a parameter group, and real protection also requires validating the server cert against the RDS CA bundle, which you must refresh when AWS rotates the certs.

## How it works

- **RDS supports TLS but does not require it by default.** The endpoint accepts both encrypted and plaintext connections, so whether a given session is encrypted depends on the client, not on RDS being "in a VPC."
- **The client must request TLS.** The app enables it in the connection (for example `sslmode=require`/`verify-full` for PostgreSQL, `?useSSL=true`/`sslMode=REQUIRED` for MySQL JDBC). Without it, the driver may connect in plaintext.
- **Server-side enforcement is per engine, via parameter group.** To force TLS regardless of client behavior, set `rds.force_ssl=1` on PostgreSQL or `require_secure_transport=ON` on MySQL in the DB parameter group. This is how you stop a misconfigured client from connecting in cleartext.
- **Certificate validation needs the RDS CA bundle.** `require` encrypts but does not verify the server. To prevent MITM you validate against the AWS RDS CA bundle (`verify-full` / `sslmode=verify-identity`), and because AWS rotates the RDS TLS certs periodically, you must keep the trust store updated or connections break at rotation.
- **Network controls do not cover encryption.** Security groups gate reachability to the port but not the encryption state, and VPC Flow Logs show that a connection happened, not whether it was TLS. There is no account-wide switch to force RDS TLS, it is per instance via parameters.

## RDS TLS enforcement by engine

| Control | PostgreSQL | MySQL |
|---|---|---|
| **Client requests TLS** | `sslmode=require`/`verify-full` | `sslMode=REQUIRED`/`useSSL=true` |
| **Server forces TLS** | `rds.force_ssl=1` (parameter group) | `require_secure_transport=ON` |
| **Server cert validation** | `verify-full` + RDS CA bundle | `sslMode=VERIFY_IDENTITY` + CA bundle |
| **Cert rotation** | Refresh CA bundle on AWS rotation | Refresh CA bundle on AWS rotation |

## What gets tested

- **VPC-internal is not encrypted.** The exam expects you to know that RDS traffic on a private subnet is plaintext unless TLS is configured. "It is internal so it is fine" is the wrong assumption.
- **Force TLS server-side per engine.** Guaranteeing encryption regardless of client is `rds.force_ssl=1` for PostgreSQL and `require_secure_transport=ON` for MySQL, applied via a DB parameter group. Relying on each client to opt in is weaker.
- **Encrypt vs validate.** `require` encrypts but does not authenticate the server. Preventing MITM needs `verify-full`/`verify-identity` with the RDS CA bundle. A scenario about spoofing or MITM points at cert validation, not just enabling SSL.
- **CA rotation breaks connections.** AWS rotating RDS certs means clients using strict verification must update the CA bundle, so a sudden connection failure across an environment can trace to a cert rotation.
- **Security groups and Flow Logs do not enforce or reveal TLS.** SGs control reachability, Flow Logs show connections but not encryption. Neither is the answer for enforcing encryption in transit.
- **At rest vs in transit are separate.** RDS at-rest encryption (KMS, set at creation) does nothing for the wire, so both must be handled for regulated data.

## Limitations

- TLS is not enforced by default, so an unconfigured client connects in plaintext, and there is no account-wide setting to force it, only per-instance parameter groups.
- `require`-style settings encrypt but do not verify the server, leaving a MITM gap unless you use full verification with the RDS CA bundle.
- AWS cert rotation requires you to maintain the client trust store, so strict verification adds an operational task or connections fail at rotation.
- Security groups and network privacy do not provide or indicate encryption, so relying on them for confidentiality in transit is a mistake.
- Forcing TLS server-side can break existing clients that were connecting in plaintext, so enabling `force_ssl`/`require_secure_transport` needs a client-readiness check.
- In-transit TLS says nothing about at-rest protection or authorization, so it must pair with RDS encryption at rest and tight IAM/DB credential management.