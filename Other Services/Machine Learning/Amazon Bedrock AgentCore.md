# Amazon Bedrock AgentCore

## What Is AgentCore

Amazon Bedrock AgentCore is the serverless orchestration engine that powers Agents in Amazon Bedrock. It’s the thing behind the curtain — the logic brain — that lets generative AI agents:

- Interpret goals from user input
- Select tools (APIs) to invoke
- Call those tools with structured input
- Use the response to plan the next step
- Keep the conversation going contextually

While Amazon Bedrock exposes the Agent concept at a high level, AgentCore is the low-level runtime and reasoning framework behind it — like the game engine behind the RPG.
It turns a static LLM into a goal-oriented decision-making engine, securely embedded in your AWS stack.

---

## Real-World Analogy

Imagine you're building a digital assistant named **Snowbot**.
You say:

> "Hey Snowbot, check if my NoaNet ticket is resolved, and summarize the incident."

Snowbot:
- Figures out that it needs to query a database
- Then needs to invoke a Lambda
- Then needs to ask an LLM to summarize JSON
- Then responds:
  _"Your BGP circuit outage (INC-02333) was resolved at 3:45 PM. Root cause: Zayo fiber cut."_

AgentCore is what made those decisions, tool calls, context handling, and language generation all come together — without human-built workflows.

---

## What AgentCore Actually Does

AgentCore enables LLMs to become autonomous, tool-using, context-aware agents.

### AgentCore’s Responsibilities

| Capability | Description                          |
|------------|--------------------------------------|
| Plan       | Parse user intent into a goal        |
| Decide     | Select the right action (tool or LLM)|
| Invoke     | Format the tool input, execute it    |
| Reflect    | Take the tool result, feed it back into reasoning |
| Continue   | Decide whether to loop again or finish |
| Respond    | Format and return the final answer to the user |

This cycle is often referred to as **ReAct** (Reasoning + Acting) — and AgentCore implements it behind the scenes.

---

## Snowy’s AgentCore Execution Flow

```text
[User Input: "Why is my circuit down?"]
↓
[LLM plans → “Need to call GetIncidentStatus()”]
↓
[AgentCore invokes Lambda function]
↓
[LLM plans → “Summarize for user”]
↓
[AgentCore invokes Claude-v3 for summarization]
↓
[Returns: "Your Spokane circuit is down due to fiber cut. ETA: 4:45PM."]
```

Each step is tracked and auditable, with security boundaries.

---

## Key AgentCore Components

| Component                | What It Does                                      |
|--------------------------|---------------------------------------------------|
| Orchestrator             | Core control flow engine. Runs the ReAct loop.    |
| Action Executor          | Calls your tools (Lambda, API Gateway, etc.)      |
| Prompt Template Manager  | Injects data, tools, and context into LLM prompts |
| Memory Manager (Optional)| Holds long-term or session state                  |
| Knowledge Retrieval Engine (Optional) | Pulls from Knowledge Bases (RAG)   |
| LLM Executor             | Makes final decisions and responses via Claude/Titan |
| Security Layer           | IAM, CloudWatch, CloudTrail auditing, KMS         |
| Error Handler            | Recovers from tool/API failure mid-execution      |

Think of AgentCore like a **Lambda Step Function** for LLM workflows, but with automatic planning and reasoning baked in.

---

## Security, Guardrails, and Auditing

| Layer           | Security Feature                                                |
|------------------|-----------------------------------------------------------------|
| IAM Isolation    | Agents run with scoped roles that limit what tools/resources they can access |
| KMS              | Encrypts any memory or knowledge base content                  |
| CloudTrail       | Logs every agent invocation, tool call, and LLM decision       |
| Parameter Validation | All tool inputs go through schema validation (JSONSchema-style) |
| Observability    | Full execution trace: tools used, results, retry logic, LLM outputs |
| Guardrails (Coming Soon) | Define what the agent is not allowed to say/do (to restrict hallucination or toxicity) |

- AgentCore never sends your tool outputs to third-party LLMs unless you configured it
- Tool responses are treated as internal — not shared or logged by model vendors

---

## Supported Tool Types

You can register tools that your agent can use:

| Tool Type          | Description                                  |
|--------------------|----------------------------------------------|
| Lambda Function    | Most common — your business logic in Python, Node, etc. |
| API Gateway Endpoint | Call 3rd-party APIs with auth headers      |
| Knowledge Base     | RAG over Titan Embeddings or vector DBs      |
| Chainable Tools    | One tool’s output can become the next tool’s input |

Each tool has a **JSON input/output schema** to help the LLM plan how to use it.

---

## Developer Workflow

Here’s what **Snowy** would do to create an agent:

1. **Define the goal**: “Help users check ticket status and summarize issues.”
2. **Register tools**:

   - `GetTicketStatus()` → Lambda
   - `SummarizeJson()` → Lambda or call LLM
3. **Set up Agent** in Bedrock Console or via SDK
4. **Provide prompt template**:
   _“You are a telecom support agent. Use tools to retrieve incident data. Be concise and clear.”_
5. **Assign IAM role** for access control
6. **Test the agent** — track execution via CloudWatch Logs + trace views

The agent can now autonomously:
- Interpret user input
- Choose the correct tools
- Format their input/output
- Call the LLM only when needed
- Return a complete answer

---

## Real-World Example

**Scenario**: Winterday wants to let NOC engineers ask a GenAI assistant:
> “Which PSAP circuits failed today and what's the root cause?”

The AgentCore logic:
- Uses Claude to interpret intent
- Selects a Lambda tool: `QueryPSAPFailures(date)`
- Parses response: JSON list of alarms, BGP paths
- Sends JSON to `SummarizeFailure()` tool
- LLM returns:
  _“2 PSAP circuits in Spokane failed due to a DWDM line card error. Root cause: Zayo power loss at hub site.”_

→ All orchestrated invisibly by AgentCore — no Step Functions or hardcoded logic trees.

---

## Final Thoughts

AgentCore is the **execution brain** behind Amazon Bedrock’s GenAI agents.
It’s not a separate product — it’s the invisible middleware that:

- Turns models into autonomous workers
- Lets models use real tools, not just text
- Supports multi-step workflows
- Makes it secure, traceable, and IAM-bound

For **Snowy-style workflows**:
- No need to handwrite chains or logic trees
- No need to fine-tune models
- No prompt injection vulnerabilities if tools are validated

If you’re serious about secure AI agents in production, **AgentCore is how you scale that**.
