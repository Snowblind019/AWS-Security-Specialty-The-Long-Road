# Amazon Bedrock

## What Is Amazon Bedrock
Amazon Bedrock is AWS’s fully managed foundation model (FM) platform that lets you build and scale generative AI applications using models from top providers (like Anthropic, Cohere, Meta, Stability AI, and Amazon’s own Titan models) — without managing infrastructure, GPUs, or model weights.

With Bedrock, you can:
- Access large language models (LLMs) via API
- Customize FMs using your own data
- Create agents that can invoke tools, make decisions, or call APIs
- Stay inside your secure VPC, with IAM, KMS, and CloudTrail
- Avoid the pain of fine-tuning or model deployment

Unlike open-source models that require a ton of compute setup, Bedrock gives you serverless, pay-as-you-go access to production-grade models — instantly.

It’s especially useful for:
- Enterprises that want LLM capabilities without managing AI infra
- Teams building chatbots, summarizers, copilots, content generation, or decision-making agents
- Security-conscious orgs that want compliance-ready GenAI

---

## Cybersecurity Analogy
Think of Bedrock like an air-gapped AI supercomputer you can query securely. You don’t install anything. You don’t download weights. You don’t train GPUs. But you get instant access to models that can understand, write, generate, or reason — all inside your VPC, wrapped in IAM, KMS, and audit logs.

It’s like having OpenAI + Anthropic + Meta behind a firewall — with zero risk of data leakage to public endpoints.

## Real-World Analogy
Let’s say Snowy wants to build a support chatbot for a telecom provider. He needs a powerful LLM to:
- Understand user questions
- Retrieve info from internal docs
- Summarize the answer
- Maybe even place a ticket

He could:
- Download LLaMA 2, set up GPUs, host a Flask API, worry about compliance…
**Or just call Bedrock**:
`InvokeModel(claude-v2)` → Bedrock runs it, bills the token usage, and returns the answer.
No provisioning. No risk of leaking prompts. No GPUs to tune. Just results.

---

## Bedrock Architecture: Core Concepts

Bedrock’s architecture is modular — you mix and match models, data, and workflows.

### 1. Foundation Models (FMs)

You get access to multiple third-party and AWS-owned models via API:

| Provider      | Models                                  |
|---------------|------------------------------------------|
| Anthropic     | Claude v1, v2, v3                        |
| AI21 Labs     | Jurassic-2                               |
| Meta          | LLaMA 2                                  |
| Cohere        | Command R                                |
| Stability AI  | Stable Diffusion XL                      |
| Amazon        | Titan Text, Titan Embeddings, Titan Image (coming soon) |

Each has a different:
- Token limit
- Latency
- Specialization (code, image, summarization, chat)

You pick the model based on your use case.

### 2. Model Invocation

You invoke a model with simple JSON over HTTPS (like calling a REST API). Example:

```json
{
  "modelId": "anthropic.claude-v2",
  "content": "Summarize this telecom outage log...",
  "parameters": {
    "temperature": 0.5,
    "top_k": 100
  }
}
```

The result comes back with:
- Response text
- Token count
- Cost (you’re billed per 1K tokens)

### 3. Agents for Bedrock

Bedrock now supports “agents” — dynamic AI workflows that can:
- Use tools (like APIs, Lambda functions)
- Interact with knowledge bases
- Make decisions mid-conversation

You define:
- Agent prompt ("You're a billing assistant...")
- Tools (Lambda functions, APIs, etc.)
- Knowledge base (RAG via vector DB)

Then the agent:
- Interprets user input
- Chooses what to do (e.g. retrieve data, call a tool, answer)
- Continues the convo using new info

This is how you go from just chatting → real automation.

### 4. Retrieval-Augmented Generation (RAG)

Bedrock supports knowledge bases to enrich models with your own data, using:
- Vector embeddings via Titan Embeddings
- Vector stores like OpenSearch, Pinecone, Redis, Knowledge Base for Bedrock
- Document ingestion (PDF, DOCX, HTML, etc.)

Bedrock enables RAG securely:
**Embed → Store → Retrieve → Inject into prompt**
No model retraining needed.

### 5. Customization (Fine-Tuning vs Prompt Engineering)

| Option              | Description                                      |
|---------------------|--------------------------------------------------|
| Prompt Engineering  | Use structured prompts/templates. No model changes. |
| Knowledge Base (RAG)| Attach external knowledge, retrieved per query     |
| Model Customization | Fine-tune Amazon Titan models with your data       |

You can custom fine-tune Titan models for domain-specific behavior.


## Snowy’s Architecture Flow Example

Let’s say Snowy builds a telecom support AI:

```text
[User Input: “Why is my BGP circuit down?”]
↓
[Agent → Claude v3]
↓
[Knowledge Base (OpenSearch)]
↓
[Fetch last 24h outage logs from Zayo]
↓
[Call Lambda Function → Get ticket status]
↓
[Generate Summary → “Outage in Spokane region, ETA: 4:45PM”]
↓
[Return structured response to frontend]
```

Bedrock orchestrates:
- Model
- Data retrieval
- Business logic
- Agent memory + context

No need to stitch together 6 AWS services manually.

---

## Security and Compliance

| Feature        | Detail                                                              |
|----------------|----------------------------------------------------------------------|
| Data Isolation | Your prompts, completions, and embeddings are never used to train models |
| VPC Support    | Private link access — no internet-exposed calls                     |
| IAM            | Granular access to specific model IDs, agents, knowledge bases      |
| CloudTrail     | Logs all Bedrock API calls                                          |
| KMS Integration| Encrypt data at rest (embeddings, knowledge base)                  |

- Zero data leakage to public models
- All inference is secure, auditable, and policy-bound

---

## Pricing (Simplified)


| Item             | Billing                                                       |
|------------------|---------------------------------------------------------------|
| Model Invocation | Per 1K input/output tokens (differs by model)                 |
| Agents           | Billed per step (each tool call + model call = 1 step)        |
| Knowledge Base   | Based on vector storage + retrieval count                     |
| Customization    | Billed for training + storage (Titan only)                    |

No cost for provisioning or idle time — you only pay when you invoke.

---

## Real-Life Example: Snowy’s Bot

Snowy builds a CloudSec AI Assistant:
- Uses Claude v3 via Bedrock
- RAG using S3 docs + Titan Embeddings
- Agent calls a Lambda that pulls IAM policy JSON
- Uses prompt engineering to compare policies
- Returns: “This role allows wildcard IAM actions. Rotate and reduce scope.”

He deploys it as an internal tool, running serverless, secure, and audited.

---

## Final Thoughts

Amazon Bedrock is AWS’s bet on secure, enterprise-scale GenAI.

✔️ No GPU clusters
✔️ No model management
✔️ No compliance risk of public LLMs
✔️ Pay-as-you-go
✔️ Your data. Your models. Your logic.

It’s especially powerful for:
- Security-focused orgs
- RAG-based assistants
- Internal copilots
- API-enhanced automation


You’re not locked into one LLM. You can hot-swap between Claude, Titan, LLaMA, Cohere, etc., while keeping your IAM/KMS posture.
