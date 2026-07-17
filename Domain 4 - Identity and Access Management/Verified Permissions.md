# Amazon Verified Permissions

Amazon Verified Permissions is a managed service for fine-grained authorization inside your own applications, using the Cedar policy language. It answers "is this user allowed to take this action on this resource in my app," which is a different question from the one IAM answers. Instead of scattering `if user.role == admin` checks through application code, you externalize authorization into a managed policy store, define a schema of principals, actions, and resources, write Cedar policies, and call the service at runtime for an allow or deny decision. It is built to consume identity tokens, so a Cognito or OIDC JWT can feed the decision directly. On the SCS exam the whole point is the boundary: Verified Permissions authorizes actions within your application, IAM authorizes AWS API calls, and Cognito authenticates the user. The thing to hold onto: this is app-level authorization as a managed service, Cedar is the policy language, and it complements IAM and Cognito rather than replacing either.

## How it works

- **A policy store holds the schema and policies.** The schema defines entity types (principals and resources), the actions they can take, and the attributes each carries. Cedar policies are validated against it.
- **Cedar policies are `permit` and `forbid` statements.** Each names a principal, action, and resource, with optional `when` and `unless` conditions on attributes. This supports both RBAC (by role/group) and ABAC (by attribute), and a `forbid` always overrides a `permit`.
- **The app asks for a decision at runtime.** It calls `IsAuthorized` with the principal, action, resource, context, and relevant entities, and gets back `ALLOW` or `DENY` plus the determining policies. `BatchIsAuthorized` evaluates many decisions at once.
- **`IsAuthorizedWithToken` consumes identity tokens.** Pass a Cognito or OIDC JWT and the service derives the principal and attributes from the token claims, tying authentication output directly to the authorization decision.
- **Policy templates parameterize grants.** A template plus per-user parameters expresses things like "this user may view this specific document" without writing a policy per grant.

## Where it sits vs IAM and Cognito

| Concern | Cognito | IAM | Verified Permissions |
|---|---|---|---|
| Question answered | Who are you | Can you call this AWS API | Can you do this action in my app |
| Scope | Authentication, token issuance | AWS resource/control-plane authorization | Application-level authorization |
| Policy language | n/a | IAM JSON policies | Cedar |
| Governs your app's own resources (documents, photos, tenants) | No | No | Yes |
| Typical caller | End user logging in | AWS principal calling AWS | Your app or a Lambda authorizer at a decision point |

## What gets tested

- **Verified Permissions is application authorization, not AWS authorization.** If the question is about controlling what a user can do to your app's own resources (view a document, edit a record, access a tenant), this is the answer. Controlling AWS API access is still IAM.
- **It pairs with Cognito via `IsAuthorizedWithToken`.** Cognito authenticates and issues the JWT; Verified Permissions authorizes the in-app action using that token's claims. This is the clean division between the two.
- **Cedar semantics mirror IAM's deny-wins.** Default is deny, and an explicit `forbid` overrides any `permit`, so the evaluation model is familiar even though the language differs.
- **It centralizes and externalizes authorization logic.** Moving policy out of code makes it auditable, testable, and consistent, which is the governance argument the exam favors for multi-tenant SaaS RBAC/ABAC.
- **It can back a Lambda authorizer.** API Gateway can call a Lambda that asks Verified Permissions for the decision, putting fine-grained authorization in front of an API.
- **It complements, not replaces.** You still need authentication (Cognito or an IdP) and still need IAM for AWS access. Verified Permissions only decides application-level actions.

## Limitations

- **App-level only.** It does not govern AWS resource or API access, so it is never the answer for restricting what an AWS principal can do to AWS services.
- **You must wire in the decision point.** It does not intercept requests automatically; the application or an authorizer has to call `IsAuthorized` wherever a decision is needed. A path that never calls it is never checked.
- **Runtime dependency.** Each decision is a call to the service, so latency, availability, and quotas matter; batch evaluation and caching are the mitigations for high-volume paths.
- **Authentication is separate.** It consumes tokens but does not issue them; you still need Cognito or an OIDC IdP in front of it.
- **Cedar is a learning curve.** The policy language and schema modeling are new surface area, and a poorly modeled schema undermines the policies written on top of it.
- **Regional with quotas.** Policy stores are per Region and bounded by limits on policies and related objects, which large deployments must plan around.