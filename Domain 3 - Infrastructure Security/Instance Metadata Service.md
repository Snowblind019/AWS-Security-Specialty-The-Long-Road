# Instance Metadata Service (IMDS)

The Instance Metadata Service is a link-local endpoint at `http://169.254.169.254` reachable from inside every EC2 instance, letting the instance query facts about itself: instance ID, AMI, AZ, network interfaces, user data, tags (if enabled), and, critically, the temporary credentials for its attached IAM role. It is what makes credential-less access work: an app fetches short-lived role credentials at runtime instead of holding long-term keys. The thing to hold onto: IMDS is the instance's credential vending machine, so the entire security question is whether something that can forge an HTTP request from inside the box (an SSRF flaw, malware, a compromised dependency) can reach it and walk off with the role's credentials. IMDSv2 exists to close exactly that path.

## How it works

- **IMDSv1** is a plain unauthenticated GET. Any code that can make an HTTP request from the instance, including an SSRF-vulnerable app tricked into requesting the URL, gets the role credentials. This is the Capital One 2019 pattern.
- **IMDSv2** is session-oriented: a **PUT** first retrieves a token (`X-aws-ec2-metadata-token`), and that token must accompany every subsequent **GET**. Because SSRF flaws typically can only force a GET, not a PUT with custom headers, the token requirement blocks the classic SSRF credential grab.
- **Hop limit** (`http-put-response-hop-limit`) caps how many network hops the token response can traverse. Set to **1** so a container on the instance cannot reach the host's IMDS, which is the container-SSRF defense.
- **Token TTL** is set at request time (up to 6 hours) and the endpoint can be disabled entirely (`http-endpoint disabled`) on instances that need no metadata.
- **Enforcement scope.** Set `http-tokens=required` per instance or in the launch template, set the **account-level IMDS default** (per Region) so new launches are IMDSv2-only, and enforce it org-wide and non-overridable with an Organizations **declarative policy** (`http_tokens_enforced`).
- **Detection.** The `MetadataNoTokenRejected` CloudWatch metric counts rejected IMDSv1 calls, so you can confirm no software still depends on v1 before hard-enforcing. AWS Config and Inspector flag instances still allowing IMDSv1.

## IMDSv1 vs IMDSv2

| | IMDSv1 | IMDSv2 |
|---|---|---|
| Request flow | Single GET | PUT for token, then GET with token |
| Auth | None | Session token required |
| SSRF credential theft | Exposed | Blocked (SSRF can't do the PUT) |
| Hop limit | N/A | Configurable (set 1 to block container access) |
| Enforcement | `http-tokens=optional` | `http-tokens=required` |

## What gets tested

- **IMDSv2 is the SSRF answer, not a network control.** "App was tricked into fetching its own role credentials" or any Capital-One-style SSRF is remediated by requiring IMDSv2 and hop limit 1, not by a security group or NACL. Security groups cannot filter the link-local metadata address meaningfully.
- **Hop limit 1 for containers.** When containers run on an EC2 host and must not reach the node's IMDS, the control is hop limit = 1 (plus IMDSv2). This is the recurring container-on-EC2 nuance.
- **Account default vs declarative policy.** An account-level IMDS default makes new launches IMDSv2-only but is per-instance overridable. Only an Organizations **declarative policy** makes it non-overridable across the org, which is the "stays enforced as new accounts and instances appear" answer.
- **Least privilege limits the damage.** IMDSv2 stops the theft; a tightly scoped instance role limits what stolen credentials could do if theft still occurs. Both appear as complementary correct actions.
- **Detect before enforce.** Use the `MetadataNoTokenRejected` metric, Config, or Inspector to find IMDSv1 usage so enforcement does not break running software.
- **Fargate is different.** On Fargate the credentials come from the ECS task endpoint at `169.254.170.2`, not IMDS at `169.254.169.254`, so IMDSv2 hop-limit hardening is an EC2 answer, not a Fargate one.

## Limitations

- IMDSv2 raises the bar against SSRF but is not absolute. Code running directly on the instance (malware, an RCE with full request control) can perform the PUT and still retrieve credentials; the real containment is the scoped role.
- The account-level default is per-instance overridable; without a declarative policy an operator or launch template can re-enable IMDSv1.
- Hard-requiring IMDSv2 breaks any SDK, agent, or script that still makes IMDSv1 calls, so a detection pass is required first or workloads fail to get credentials.
- Hop-limit and token settings apply to EC2 IMDS only. They have no effect on ECS task credentials, Lambda, or other credential sources.
- Disabling the endpoint entirely is safest where metadata is unused, but breaks role-based credential retrieval, so it only fits instances that carry no role or supply credentials another way.