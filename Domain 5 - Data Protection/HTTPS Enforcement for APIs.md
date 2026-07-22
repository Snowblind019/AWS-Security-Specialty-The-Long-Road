# HTTPS Enforcement for APIs

Any API, internet-facing or internal, has to encrypt traffic in transit or it leaks credentials, tokens, query parameters, PII, and responses to anyone sniffing, and it opens the door to MITM modification and replay. In AWS the enforcement point depends on the fronting pattern: API Gateway is HTTPS-only by default, an ALB in front of ECS/EC2 needs an HTTPS listener plus an HTTP-to-HTTPS redirect, CloudFront needs both viewer and origin protocol policies locked down, and raw EC2 forces you to manage certs yourself. The recurring gap is the origin hop and the redirect: encrypting only the client side while leaving CloudFront-to-origin or ALB-to-target on plaintext is the classic mistake. The thing to hold onto: match the enforcement to the entry point, always cover both hops (viewer and origin), and reach for mTLS when the requirement is authenticating the calling service, not just encrypting the channel.

## How it works

- **API Gateway is HTTPS-only by default.** It listens only on 443, so the work is securing custom domain names with an ACM cert and a TLS 1.2+ minimum, and never fronting it with something that terminates TLS and forwards plaintext.
- **ALB-backed APIs need a listener plus a redirect.** Create an HTTPS listener on 443 with an ACM cert and a strong security policy, then add an HTTP listener on 80 whose default action redirects to HTTPS (301). Without the redirect, clients can still reach the API over plaintext.
- **CloudFront covers two hops.** Set the viewer protocol policy to redirect-to-HTTPS or HTTPS-only, set a TLS 1.2+ viewer security policy, and set the origin protocol policy to HTTPS-only so the edge-to-origin hop is encrypted too. Leaving origin at match-viewer or HTTP-only leaves a plaintext segment.
- **Raw EC2 makes it all manual.** You install and manage certs (via a web server, or terminate at an ALB with ACM), listen only on HTTPS, and redirect HTTP with a 301. Direct EC2 exposure is discouraged precisely because you own the whole TLS lifecycle.
- **mTLS authenticates the caller.** For internal service-to-service APIs, mutual TLS (via App Mesh/Envoy or NGINX sidecars, with client certs from ACM Private CA or SPIFFE/SPIRE) verifies both ends, giving zero-trust identity on the call rather than just an encrypted pipe.

## Enforcement by API pattern

| Pattern | Enforcement | Watch for |
|---|---|---|
| **API Gateway (REST/HTTP)** | HTTPS by default, ACM on custom domain | Don't front it with plaintext-forwarding TLS termination |
| **ALB (ECS/EC2)** | HTTPS listener + 80-to-443 redirect | Missing redirect leaves HTTP open |
| **CloudFront to API** | Viewer + origin protocol policies | Origin match-viewer/HTTP is a plaintext hop |
| **Raw EC2** | Self-managed certs, HTTPS-only, 301 | Whole TLS lifecycle is on you |
| **Internal microservices** | mTLS via sidecar / App Mesh | Cert rotation and trust store management |

## What gets tested

- **API Gateway is already HTTPS-only.** The exam expects you to know it does not accept plaintext, so the enforcement work is on custom domains, TLS minimum, and not undermining it upstream.
- **ALB needs the redirect, not just the HTTPS listener.** Forcing all traffic to HTTPS requires both the 443 listener and an 80-to-443 redirect action. An HTTPS listener alone still leaves port 80 reachable.
- **CloudFront origin protocol is the trap.** Encrypting the viewer hop but leaving origin at match-viewer or HTTP-only means CloudFront-to-origin can be plaintext. HTTPS-only origin protocol is required for edge-to-origin encryption.
- **mTLS for caller identity.** When the requirement is authenticating which service is calling (not just encrypting), that is mutual TLS, typically via a service mesh, with certs from ACM Private CA.
- **TLS 1.2+ security policy.** Compliance-driven scenarios want a modern security policy on the ALB or CloudFront, not a legacy one that permits TLS 1.0.
- **ACM for cert lifecycle.** Auto-renewing certs from ACM (server side) beat self-managed certs, and the CloudFront cert must be in `us-east-1`.

## Limitations

- Encrypting the viewer hop alone is insufficient. The origin hop (CloudFront-to-origin, ALB-to-target) must also be secured or a plaintext segment remains.
- An HTTPS listener without an HTTP-to-HTTPS redirect still exposes port 80, so enforcement needs both pieces on an ALB.
- HTTPS encrypts and integrity-protects the channel but does not authenticate the caller. Verifying who is calling an internal API requires mTLS on top.
- Raw EC2 exposure shifts the entire TLS burden (issuance, rotation, redirect, cipher policy) to you, which is error-prone compared with API Gateway, ALB, or CloudFront.
- Self-signed or unpinned certs break the trust model and are vulnerable to spoofing, so managed certs (ACM) or a proper private CA are required for real assurance.
- Transit encryption does nothing for authorization or at-rest protection, so it must pair with token/IAM auth, WAF, and encrypted storage rather than standing alone.