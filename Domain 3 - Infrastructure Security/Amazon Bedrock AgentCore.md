# Amazon Bedrock AgentCore

A modular, framework-agnostic platform for running AI agents in production on AWS. It is not a model and not a framework: you bring the agent logic (LangGraph, CrewAI, Strands, or your own code) and any foundation model, and AgentCore supplies the runtime, memory, tool connectivity, identity, guardrails, and observability so you don't hand-build that plumbing. It is a separate thing from classic Agents for Amazon Bedrock, which is the declarative, low-code action-group service; AgentCore is the runtime for custom agent code.

For security work, AgentCore matters because it is both an attack surface and a control surface: an autonomous process that holds credentials, calls tools, and touches data. The thing to hold onto is that its security model is scoped IAM plus session isolation plus guardrails enforced outside the agent's own reasoning. Every exam-relevant question reduces to one of those: what can this agent access, can one session see another's data, what tools may it invoke, and can it talk its way around a check.

## How it works

AgentCore is a set of modular services you can use together or independently:

- **Runtime**: serverless, session-isolated execution of your agent code, each session in its own container, with long-running sessions supported. Isolation is the security property: it prevents cross-session and cross-tenant data bleed. No infrastructure to manage.
- **Identity**: authenticates and authorizes each tool call, deciding who is calling and whether they are allowed. Ties agent actions to scoped credentials instead of one blanket role.
- **Gateway**: turns existing APIs, Lambda functions, and OpenAPI specs into MCP-compatible tools the agent can call. Every tool call routes through the gateway, which is where policy and guardrails are enforced.
- **Memory**: managed short-term (within-session) and long-term (cross-session) memory, with extraction strategies such as semantic, summary, and user-preferences. It can hold sensitive conversation content, so encrypt it and scope access.
- **Code Interpreter and Browser**: sandboxed code execution and an isolated cloud browser, so the agent can run code or browse the web without touching your infrastructure directly.
- **Policy**: defines which tools the agent may invoke and under what conditions. Authorization is checked per tool call and verified by automated reasoning, the same policy-proving technology behind IAM and S3.
- **Guardrails integration**: Bedrock Guardrails evaluate agent inputs and outputs at the gateway layer, outside the agent's code, so the agent cannot reason around them. Catches prompt injection attempts, harmful content, and sensitive-data exposure.
- **Observability**: full execution traces (tools called, inputs, results, retries, model decisions) through CloudWatch, with invocation and control-plane activity logged for audit.
- **Harness (managed)**: CreateHarness and InvokeHarness run an agent with no orchestration code and no container to build, wiring identity, memory, gateway, and guardrails together.

Security boundaries around all of this: KMS encrypts memory and data at rest and in transit, VPC integration and PrivateLink keep the agent inside a private network boundary, and each agent runs under a scoped, least-privilege IAM role.

Request flow, showing where the controls sit:

```text
[User goal]
  -> Runtime (isolated session, scoped IAM role)
  -> Gateway  --> Policy check: is this tool allowed, under these conditions?
              --> Guardrails: prompt injection, harmful content, sensitive data
  -> Tool (Lambda / API / Code Interpreter / Browser)  runs under Identity auth
  -> result returned to the model, next step planned
  -> Observability trace written for the whole run
```

## AgentCore vs sibling options

| | AgentCore | Bedrock Agents (classic) | Step Functions | Self-hosted (EKS / Lambda) |
|---|---|---|---|---|
| Infra | Managed, serverless | Managed, serverless | Managed | You run it |
| Agent logic | Your code, any framework | Declarative action groups, low-code | Hand-built state machine | Your code |
| Model | Any (Bedrock or external) | Bedrock models | N/A | Any |
| Built-in security | Identity, Policy, Guardrails, session isolation | IAM plus Guardrails | IAM | You build it |
| Best for | Custom agents to production with security baked in | Fast low-code agent on Bedrock | Deterministic workflows, not reasoning | Full control, willing to own the plumbing |

## What gets tested

- AgentCore is new and moving fast, so treat it as concept-level. What transfers to the exam is the security model, not CLI or component trivia.
- Distinguish AgentCore (framework-agnostic platform for custom agent code, modular services) from classic Agents for Amazon Bedrock (declarative action groups, no custom code). The framing that AgentCore is "the engine inside Bedrock Agents" is wrong and is the trap.
- The security pattern is the point: a scoped least-privilege IAM role per agent, session isolation to prevent cross-tenant access, Identity and Policy to authorize each tool call, Guardrails enforced at the gateway outside the agent's reasoning, KMS for memory and data, and CloudTrail plus Observability for audit.
- Guardrails at the gateway layer beat guardrails written into the prompt, because the agent cannot talk its way around a check that runs outside its own code path. That is the durable, exam-style insight.
- Prompt injection is mitigated, not eliminated, by input validation plus gateway guardrails. Do not claim schema validation removes prompt-injection risk.
- Reacting to a specific security finding or a specific API call is still EventBridge, GuardDuty, and Security Hub territory, not AgentCore.

## Limitations

- New service, changing quickly: feature names and GA status shift, so verify against current docs before relying on specifics.
- Not a framework and not a model. It runs your agent, it does not write the logic or reason for you.
- Not classic Bedrock Agents. If you want declarative, no-code action groups, that is the other service.
- Multi-component billing: many independently billable pieces (Runtime, Gateway, Memory, Policy, and more) plus additive model inference cost, which makes surprise charges easy.
- Guardrails and validation reduce but do not remove prompt-injection and tool-abuse risk. Least-privilege tool scoping still matters.
- Managed but not automatic: you still own IAM scoping, encryption choices, VPC placement, and log review.