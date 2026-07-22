# Enforcing HTTPS on Amazon CloudFront

CloudFront is AWS's global CDN and usually the first thing a client touches, which makes it the place to enforce TLS end to end. Left at defaults it is permissive: it accepts both HTTP and HTTPS from viewers, allows whatever TLS versions the chosen security policy permits, and can talk to the origin over plaintext HTTP unless told otherwise. Enforcing HTTPS is therefore a three-setting job at two hops, viewer-to-CloudFront and CloudFront-to-origin, plus the TLS policy that sets the floor. The thing to hold onto: the viewer protocol policy controls the client hop (redirect-to-HTTPS or HTTPS-only, and it is per cache behavior so `/api/*` can differ from `/`), the origin protocol policy controls the back hop, and both must be locked down or you have a plaintext segment even with a valid cert.

## How it works

- **Viewer protocol policy governs client to CloudFront.** Allow-all accepts HTTP, redirect-to-HTTPS bounces HTTP to HTTPS (typical for websites), and HTTPS-only rejects HTTP outright with a 403 (typical for APIs). It is set per cache behavior, so each path pattern can enforce its own rule, and a forgotten behavior is where plaintext slips in.
- **TLS security policy sets the version and cipher floor.** Choosing a policy like TLSv1.2_2021 enforces TLS 1.2 minimum and modern ciphers, removing weak protocols and downgrade vectors. Older policies (TLSv1_2016) permit TLS 1.0 and are non-compliant for PCI DSS.
- **Origin protocol policy governs CloudFront to origin.** HTTP-only is plaintext to the backend, match-viewer inherits whatever the client used (so a client on HTTP means HTTP to origin), and HTTPS-only forces encryption on the back hop. HTTPS-only is the secure choice.
- **ACM cert for the viewer side, in `us-east-1`.** CloudFront reads its viewer certificate from `us-east-1` regardless of where the origin lives, attached via the distribution's viewer certificate with SNI. ACM auto-renews it.
- **S3 origins use OAC plus the REST endpoint.** Origin Access Control locks the bucket so it is reachable only through CloudFront, and the S3 REST endpoint supports HTTPS to origin. Note the S3 static website endpoint only speaks HTTP, so if you need HTTPS on the back hop you must use the REST endpoint with OAC, not the website endpoint.
- **Lambda@Edge for ultra-strict or signed-URL cases.** A viewer-request function can inspect `cloudfront-forwarded-proto` and 403 any non-HTTPS request, useful for enforcing HTTPS on signed URLs beyond the built-in policy.

## The two hops and their controls

| Hop | Control | Secure setting |
|---|---|---|
| **Viewer to CloudFront** | Viewer protocol policy (per behavior) | Redirect-to-HTTPS or HTTPS-only |
| **TLS floor** | TLS security policy | TLSv1.2_2021 or newer |
| **CloudFront to origin** | Origin protocol policy | HTTPS-only (not match-viewer) |
| **Viewer cert** | ACM cert in `us-east-1` | SNI, auto-renewing ACM cert |
| **S3 origin lock** | Origin Access Control | OAC + S3 REST endpoint (HTTPS) |

## What gets tested

- **Redirect-to-HTTPS vs HTTPS-only.** Websites usually redirect (so a user typing `http://` still lands securely), APIs usually reject with HTTPS-only. The viewer protocol policy is per cache behavior, so partial enforcement (only some paths) is a real misconfiguration.
- **Origin protocol policy is the back-hop gap.** Encrypting only the viewer side leaves CloudFront-to-origin plaintext unless origin protocol is HTTPS-only. Match-viewer is a trap because a client on HTTP produces HTTP to origin.
- **CloudFront cert must be in `us-east-1`.** A cert in any other Region will not attach to the distribution. This is a frequent distractor.
- **TLS policy for compliance.** PCI DSS and modern baselines require TLS 1.2 minimum, so the answer is a TLSv1.2_2021-or-newer security policy, not a legacy one.
- **OAC for S3 origins.** Locking the origin so it is only reachable via CloudFront is OAC (the successor to OAI), and the REST endpoint gives you HTTPS to origin while the website endpoint does not.
- **Lambda@Edge for signed-URL HTTPS enforcement.** When the built-in policy is not enough (per-request protocol checks on signed URLs), a viewer-request Lambda@Edge does it.

## Limitations

- Enforcement is per cache behavior, so a single behavior left at allow-all reopens plaintext even if the default behavior is locked down.
- Match-viewer origin policy silently allows HTTP to the origin whenever a client connects over HTTP, so it is not a safe "secure" setting.
- The S3 static website endpoint cannot do HTTPS on the origin hop, so HTTPS-to-origin for S3 requires the REST endpoint with OAC.
- The viewer certificate must live in `us-east-1`, which trips up teams whose origin and other certs are in another Region.
- HTTPS enforcement protects the transport, not authorization or content. It does not stop an authenticated-but-malicious request, and it must pair with WAF, signed URLs/cookies, and origin access controls.
- Redirect-to-HTTPS still exposes the initial HTTP request before the redirect, so the strictest APIs prefer HTTPS-only (reject) over redirect.