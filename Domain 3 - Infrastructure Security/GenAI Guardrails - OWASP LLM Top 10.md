# GenAI Guardrails and the OWASP LLM Top 10

Generative-AI guardrails are the runtime safety layer between users and a foundation model: policies that inspect prompts before the model sees them and responses before the user sees them, blocking harmful content, prompt attacks, denied topics, and PII leakage. In AWS this is **Amazon Bedrock Guardrails**, and the exam (Task 3.2.7) frames it against the **OWASP Top 10 for LLM Applications (2025)**, the standard catalog of LLM risks. The thing to hold onto: guardrails are input-and-output filtering decoupled from the model, applied at inference time (and portable to any model via the ApplyGuardrail API), so the exam tests which OWASP risk a given Guardrails policy addresses and where guardrails stop and other AWS controls (IAM, KMS, VPC, logging) take over.

## How it works

- **Bedrock Guardrails policy types.** Six core safeguards: **Content filters** (hate, insults, sexual, violence, misconduct, and prompt-attack, each with adjustable strength, text and image), **Denied topics** (up to 30 subject-matter themes to block, evaluated contextually), **Word filters** (exact-match blocklists, profanity, competitor names), **Sensitive information filters** (PII detection with block or redact, plus custom regex), and **Contextual grounding checks** (grounding and relevance, to catch hallucinations against source material). Since Aug 2025, **Automated Reasoning checks** add formal mathematical verification of responses against a policy document.
- **Two evaluation points.** Guardrails run on the **input prompt** (topic blocking, prompt-injection/jailbreak detection, content filtering) and on the **output response** (PII redaction, harmful-content blocking, contextual grounding). A blocked check returns a configured blocked message.
- **Tiers.** A **Standard tier** improves detection of typo/obfuscation variants, distinguishes jailbreak from prompt injection, and supports up to 60 languages (requires opting into cross-Region inference).
- **ApplyGuardrail API.** Applies a guardrail to any model, Bedrock-hosted, self-hosted, or third-party outside Bedrock, giving one consistent policy across models. Guardrails are also referenced in `Converse`/`InvokeModel` calls.
- **IAM enforcement.** IAM policy-based enforcement can require that inference calls carry a specific guardrail, so responsible-AI policy is enforced org-wide, not left to each developer.
- **Deployment and monitoring.** Configured via console, CLI, CloudFormation (`AWS::Bedrock::Guardrail`), or Terraform; CloudWatch and CloudTrail provide monitoring and audit of guardrail actions.

## OWASP LLM Top 10 (2025) mapped to AWS controls

| OWASP risk | Primary control |
|---|---|
| LLM01 Prompt Injection | Guardrails prompt-attack filter + denied topics; treat retrieved content as untrusted |
| LLM02 Sensitive Information Disclosure | Guardrails PII filters (redact/block); scoped RAG access; KMS; least-privilege data sources |
| LLM03 Supply Chain | Vet models/datasets; Inspector/SCA on app deps; provenance of fine-tune sources |
| LLM04 Data and Model Poisoning | Curate and sign training data; access-control the pipeline; validate datasets |
| LLM05 Improper Output Handling | Output filters + downstream encoding/validation (never trust model output as safe) |
| LLM06 Excessive Agency | Least-privilege agent roles, scoped tool permissions, human-in-loop for consequential actions |
| LLM07 System Prompt Leakage | Keep secrets out of the system prompt; Guardrails output filtering; treat prompt as exposed |
| LLM08 Vector and Embedding Weaknesses | Tenant-isolate the vector store; access-control RAG retrieval; encrypt embeddings |
| LLM09 Misinformation | Contextual grounding checks; Automated Reasoning; retrieval grounding |
| LLM10 Unbounded Consumption | Rate limiting, token/quota caps, cost and concurrency controls |

## What gets tested

- **Guardrails is the Bedrock safety layer.** "Stop the model from returning harmful content, leaking PII, or answering off-limits topics" is Bedrock Guardrails, applied at input and output. Match the concern to the policy type: PII leak to sensitive-information filters, off-limits subject to denied topics, jailbreak to the prompt-attack content filter.
- **Prompt injection (LLM01) is the top risk.** Prompt-attack content filters plus denied topics reduce it, but the deeper mitigation is treating retrieved/user content as untrusted and not granting the model authority it can be tricked into misusing. Guardrails mitigate, they do not eliminate.
- **Sensitive information disclosure (LLM02).** Jumped to second in 2025. Combine Guardrails PII redaction with scoped RAG retrieval (so the model cannot surface another tenant's or unauthorized user's data), KMS, and least-privilege data-source access. Output filtering alone is not enough.
- **Contextual grounding and Automated Reasoning for hallucination/misinformation (LLM09).** Grounding checks score relevance/support against source material; Automated Reasoning formally verifies claims against a policy document, the answer for regulated domains needing a provable factual basis.
- **ApplyGuardrail portability.** When guardrails must cover a self-hosted or third-party model, the answer is the **ApplyGuardrail API**, giving one policy across models rather than per-model code.
- **Enforce guardrails via IAM.** To guarantee every inference call uses a guardrail (not optional per developer), use IAM policy-based enforcement, the org-scale responsible-AI control.
- **Excessive agency (LLM06).** For agents that call tools, the control is least-privilege agent identity and scoped tool permissions plus human approval for consequential actions, an IAM/agent-design answer, not a Guardrails filter.

## Limitations

- Guardrails filter content and topics; they do not fix an over-privileged agent, a poisoned dataset, an exposed vector store, or a leaky RAG access model. Those are IAM, data-pipeline, and retrieval-access problems.
- Content filters and denied topics are probabilistic and can be bypassed (obfuscation, novel jailbreaks) or false-positive; the Standard tier helps but does not guarantee coverage, so guardrails are one layer, not the whole defense.
- System-prompt restrictions on what to reveal can be overridden by prompt injection, so secrets must never live in the prompt; treat the system prompt as potentially exposed (LLM07).
- Automated Reasoning verifies only against the policy document you define and in supported Regions; it is powerful in constrained domains but not a general truth oracle.
- Guardrails add per-request cost and latency and are Region- and model-scoped; enforcing them everywhere is a deliberate IAM and deployment step, not a default.
- Guardrails do not cover LLM10 (unbounded consumption/cost) or LLM03 (supply chain); rate limiting, quotas, and dependency/model vetting are separate controls.