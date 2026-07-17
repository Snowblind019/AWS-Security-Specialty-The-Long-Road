# IAM Access Advisor

IAM Access Advisor is a visibility tool that answers one question: which AWS services has this IAM identity actually used, and when did it last use them. It compares the permissions granted to an identity against the ones it has actually exercised, for users, roles, and groups, using service last accessed data that AWS collects from your account activity. It is not a simulator, not Access Analyzer, and not a policy generator; it is a usage record you read to find dead permissions. Its whole reason to exist on the SCS exam is least privilege: it is the evidence source you use to trim access that was granted "just in case" and never touched. The thing to hold onto: Access Advisor tells you what an identity has and does not use, so you can cut the unused paths before an attacker finds them.

## How it works

- **It lives in IAM and covers users, roles, and groups.** For a given identity it lists each service, the last-accessed timestamp, whether the identity is permitted to use that service, and how that permission is granted (inline policy, managed policy, or inherited from a group).
- **It reads from service last accessed data.** AWS records the trailing history of service activity, and Access Advisor surfaces it. There is a collection delay, so recent activity takes a few hours to appear.
- **Granularity is service-level.** It shows "has access to S3" and when S3 was last touched, not whether the call was `s3:GetObject` or `s3:DeleteBucket`. Action-level last-accessed data exists for only a limited set of services; for full API-level detail you go to CloudTrail.
- **It is available programmatically.** `GenerateServiceLastAccessedDetails` and `GetServiceLastAccessedDetails` return the same data for automation and org-wide reviews.
- **You act on the gaps.** Services showing "not accessed" against a broad policy are the candidates to remove when you rewrite the policy to least privilege.

## Access Advisor vs the tools it gets confused with

| Tool | Question it answers | Nature |
|---|---|---|
| **Access Advisor** | What services has this identity used, and when | Descriptive, usage history for least-privilege cleanup |
| **IAM Access Analyzer** | Does a resource policy grant access outside my account/org, and which permissions are unused | Findings on unintended external access and unused access |
| **IAM Policy Simulator** | Would this policy allow or deny a given action | Hypothetical evaluation, no actual usage involved |
| **CloudTrail** | Which exact API calls happened, by whom, when | Granular event record for forensics and audit |

## What gets tested

- **Access Advisor is the least-privilege cleanup tool.** When a scenario asks how to identify permissions an identity has but never uses, in order to right-size a policy, this is the answer.
- **Do not confuse it with its neighbors.** "Would this action be allowed" is Policy Simulator. "Is anything granting external or unintended access, or which permissions are unused" is Access Analyzer. "What exact API calls were made" is CloudTrail. The exam plants all four and tests whether you pick the right one.
- **It is service-level, not action-level.** Any question needing per-API detail (which specific call, from which source IP, at what time) is CloudTrail, not Access Advisor.
- **It shows how access is granted.** Because it names the policy path (inline, managed, or group-inherited), it helps you find where an unused permission actually comes from before removing it.
- **It is descriptive, not preventive.** It reports on the past; it does not block anything. If a scenario needs prevention, the answer is SCPs, permission boundaries, or policy design, not Access Advisor.

## Limitations

- **Service-level by default.** Per-API granularity is available for only a small set of services; otherwise use CloudTrail for action-level detail.
- **Collection delay.** Recent activity can take up to about four hours to appear, so it is not real-time.
- **Bounded reporting window.** It reflects only the trailing activity window (up to roughly the last 400 days in most regions), not all history. Note: the source's "90 days / 400,000 minutes" figure is outdated; the window is now much longer and varies by region.
- **No SCP block visibility.** It shows what was allowed and used, not what an SCP or RCP prevented.
- **No usage context.** It does not surface tags, condition keys, or the calling context (console session versus assumed-role STS session), so it cannot tell you how or why access was used.
- **It only flags dead weight.** It points at unused permissions; deciding and enforcing the trim is still on you.