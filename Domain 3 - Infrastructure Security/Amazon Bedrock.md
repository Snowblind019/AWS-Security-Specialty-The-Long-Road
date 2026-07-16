# Amazon Bedrock

AWS's managed, serverless platform for calling foundation models (Anthropic Claude, Amazon Titan and Nova, Meta Llama, Cohere, AI21, Mistral, Stability, and others) through a single API, with no GPUs, weights, or model hosting to manage. On top of raw inference it adds customization (fine-tuning and continued pre-training), Knowledge Bases for RAG, Agents and AgentCore for tool-using workflows, and Guardrails for content control.

For security work the framing that matters is that Bedrock makes a model look like just another AWS API: bedrock:InvokeModel behaves like s3:GetObject, so the same IAM, KMS, VPC, and logging patterns apply. Two twists break the analogy. The request and response payloads are natural language that IAM cannot inspect, and almost every security control is opt-in rather than on by default. The thing to hold onto: your data stays in your account and is not used to train the base models, but private networking, guardrail enforcement, and content logging are all things you switch on and enforce, not defaults you inherit.

## How it works

- **Model access**: call bedrock:InvokeModel (or the streaming variant) over HTTPS. Access is deny-by-default and should be scoped per foundation-model ARN. Resource: * grants every model in the Region, including ones you never reviewed.
- **Customization**: fine-tuning and continued pre-training produce a private copy of the model in your account, encrypted with your KMS key. The training data and the custom model never flow to the provider or to other customers.
- **Knowledge Bases (RAG)**: embed your documents, store the vectors (OpenSearch Serverless and others), retrieve at query time, and inject into the prompt. No retraining. Encrypt the vector store and the source data with KMS.
- **Agents and AgentCore**: turn a model plus tools (Lambda, APIs) into a workflow that can act. Agents is the higher-level managed abstraction; AgentCore is the framework-agnostic runtime platform. Actions widen the blast radius, so scope the tool roles tightly.
- **Guardrails**: filter prompts and completions for harmful content, denied topics, and PII (redact or block). Attached per invocation via guardrailIdentifier.
- **Data privacy**: prompts, completions, and embeddings stay in your account and Region, are not used to train base models, and are not shared with providers.

The enforcement layer, which is the opt-in part and the part the exam probes:

- **IAM**: scope bedrock:InvokeModel per model ARN and gate admin actions separately. Use the bedrock:GuardrailIdentifier condition key to deny any invocation that omits the approved guardrail, or set the account-level enforced-guardrail configuration. A guardrail a code path can skip is not a control.
- **VPC and PrivateLink**: the public Bedrock endpoint is reachable from anywhere the principal is valid. Keep traffic private with interface VPC endpoints for both the control and runtime planes.
- **KMS**: encrypt custom models, Knowledge Bases, agents, and invocation logs with customer-managed keys.
- **Two separate logs**: CloudTrail records the invocation metadata (who called which API, when, from where) but never the prompt or completion. Model invocation logging is the separate feature that captures the actual prompt and completion bodies, to CloudWatch Logs, S3, or Firehose. You need both, and they record different things.

## Amazon Bedrock vs sibling options

| | Bedrock | SageMaker (JumpStart / self-host) | Self-hosted (EC2 / EKS) | Direct third-party API |
|---|---|---|---|---|
| Infra | None, serverless | You manage endpoints | You manage everything | None |
| Models | Managed catalog, many providers | Bring or deploy your own | Whatever you host | Vendor's only |
| Data boundary | Stays in your account / Region | Your account | Your account | Leaves to the vendor |
| Native IAM / KMS / VPC | Yes, but opt-in | Yes | You build it | No |
| Best for | Fast, secure managed GenAI | Full control of the model, ML teams | Total control, heavy ops | Quick prototypes, weak governance |

## What gets tested

- CloudTrail vs model invocation logging is the canonical distinction: CloudTrail logs the API call metadata and never the prompt or completion. Enabling model invocation logging is what captures the actual content, to CloudWatch, S3, or Firehose. Treat those logs as sensitive and lock them down.
- Scope bedrock:InvokeModel per model ARN. Resource: * silently grants every model in the Region. Deny-by-default, least privilege.
- Guardrails are only a control when enforced. Use the bedrock:GuardrailIdentifier IAM condition key, or the account-level enforced guardrail, so no code path can skip it. Guardrails filter harmful content, denied topics, and PII.
- Data privacy: customer prompts, completions, and fine-tuning data are not used to train base models and are not shared with providers. A custom model is a private, KMS-encrypted copy.
- Private access is not the default. The public endpoint is reachable from anywhere the IAM principal is valid. Interface VPC endpoints (PrivateLink) keep runtime and control-plane traffic off the internet.
- The model is an untrusted component. A correctly authenticated principal can still send an adversarial prompt, and IAM cannot inspect the natural-language payload. Prompt injection is a data-layer problem, addressed by Guardrails and tight tool scoping, not by authentication.

## Limitations

- Almost every control is opt-in: private networking, guardrail enforcement, and content logging are off until you configure them.
- IAM cannot see inside prompts or completions, so it cannot stop prompt injection or data exfiltration through the payload. That is Guardrails plus least-privilege tool design.
- CloudTrail alone gives you no prompt or completion content. Without invocation logging you cannot reconstruct what was actually sent or returned.
- The model roster and versions change constantly. Pin approved models by ARN rather than assuming the catalog is static.
- Cost is per token (input and output), per agent step, and per Knowledge Base storage and retrieval. Heavy RAG or agent loops add up, and invocation logging adds storage cost.
- Managed does not mean governed. Multi-account rollouts need SCPs, endpoint policies, and StackSets to keep every account consistent.