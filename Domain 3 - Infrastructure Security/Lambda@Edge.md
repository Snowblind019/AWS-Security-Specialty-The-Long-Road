# AWS Lambda@Edge

Lambda@Edge is an extension of AWS Lambda that runs functions at CloudFront edge/regional-edge locations in response to CloudFront events, so request and response logic executes close to the user and often before traffic reaches the origin. Typical work: request rewriting and redirects, header and cookie manipulation, device and geo targeting, and security enforcement like token/JWT validation and bot filtering. The thing to hold onto: Lambda@Edge turns CloudFront into a programmable policy-enforcement layer at the perimeter, and for the exam the sharpest decision is Lambda@Edge versus CloudFront Functions, heavier and more capable (four trigger points, network access, AWS SDK) versus lighter, faster, cheaper, and viewer-only.

## How it works

- **Deployment.** Author the function in **us-east-1**, publish a numbered version (no `$LATEST`), and associate that version with a CloudFront distribution and event. CloudFront replicates it to edge locations; a change takes several minutes to propagate globally and rollback means re-associating a prior version.
- **Four trigger points.** **Viewer request** (before cache lookup), **origin request** (on cache miss, before the origin fetch), **origin response** (after the origin replies, before caching), **viewer response** (before returning to the client). Auth and geo redirects usually run at viewer request; header injection and rewrites at origin request; security-header stamping at origin/viewer response.
- **Runtime and limits.** Node.js and Python. Viewer-triggered functions are capped tighter (about 5 seconds, 1 MB package); origin-triggered functions allow more (about 30 seconds, up to 50 MB and higher memory). No traditional environment variables, so config is hardcoded or fetched from a shared store at runtime. It can make network calls, use the AWS SDK, read the request body, and use `/tmp`.
- **Security uses.** JWT/token validation before the origin is hit, geo-fencing and IP-range blocking, bot detection via header/user-agent parsing, stripping tracking or sensitive headers, and adding response security headers (`Content-Security-Policy`, `Strict-Transport-Security`). Doing this at the edge shrinks origin attack surface and drops wasteful origin hits.
- **Logging.** CloudWatch Logs are written in the Region nearest the executing edge location, not only us-east-1, which matters when hunting for edge-function logs.

## Lambda@Edge vs CloudFront Functions

| | Lambda@Edge | CloudFront Functions |
|---|---|---|
| Runtime | Node.js / Python, full Lambda env | Constrained JavaScript (edge runtime) |
| Trigger points | All four | Viewer request and viewer response only |
| Network / AWS SDK / body | Yes | No |
| Execution budget | ~5 s viewer, ~30 s origin | Sub-millisecond |
| Location | Regional edge caches | Edge points of presence (closer) |
| Cost | Higher (per-request + duration) | ~6x cheaper, no duration billing |
| Best for | Auth with lookups, origin logic, transforms needing network/SDK | URL rewrites, header tweaks, cache-key normalization, simple redirects/authz |

## What gets tested

- **Which edge compute to pick.** Simple, high-volume viewer-side header/URL/redirect work is **CloudFront Functions** (cheaper, faster, viewer-only). Anything needing an **origin trigger**, network/AWS SDK access, the request body, or heavier logic (JWT validation with an external lookup, fetching a key) is **Lambda@Edge**. Picking wrong means overpaying or hitting a hard constraint.
- **Trigger-point selection.** Auth and geo decisions belong at **viewer request** (before cache) so unauthorized traffic never reaches cache or origin. URL rewrites and origin header injection go at **origin request**. Security response headers go at **origin/viewer response**. Scenarios test whether you place the logic before or after the cache.
- **us-east-1 authoring.** Lambda@Edge functions must be created in us-east-1 and associated by published version. "Why won't my edge function deploy from eu-west-1" is answered by the Region requirement.
- **Edge auth reduces origin exposure.** Validating tokens or blocking bots at the edge before the origin is the pattern for cutting origin load and attack surface; it complements WAF on the distribution rather than replacing it.
- **Data-residency caveat.** Because functions run globally, request payload (headers, cookies, query, body) may be processed outside the primary Region. A strict data-residency scenario is a reason to validate in-Region instead, or to use a control that does not move data across geographies.
- **No environment variables.** Neither edge option supports traditional env vars, so "inject config via environment variable at the edge" is wrong; config is baked in or pulled from a store.

## Limitations

- Propagation takes minutes and rollback is a re-association, so it suits stable production logic, not high-churn iteration.
- Tighter limits than regional Lambda: viewer functions especially are constrained on time and package size, and there are no environment variables, so heavy or long-running computation does not belong at the edge.
- Global execution means potential cross-Region data processing, which can violate residency requirements if sensitive payload is inspected at the edge.
- Cost scales with invocations and duration and can exceed CloudFront Functions substantially at high request volumes, so viewer-side simple tasks are usually the wrong fit for Lambda@Edge.
- Errors in an edge function break the request (for example a viewer-request exception returns a 502, an origin-request failure a 504), so functions must catch errors and return safe defaults.
- It is bound to CloudFront events only; it is not a general-purpose compute layer and cannot run outside the CloudFront request lifecycle.