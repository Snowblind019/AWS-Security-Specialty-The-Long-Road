# IAM Policy Simulator  

## What Is the Service

The IAM Policy Simulator is a tool provided by AWS that allows you to test and validate what an identity can or cannot do, before or after permissions are applied.  
It lets you simulate real-world API calls (like `s3:GetObject`, `ec2:DescribeInstances`, `kms:Decrypt`, etc.) for any IAM user, group, or role — and tells you whether that action would be allowed or denied given the current policies attached.

It doesn’t actually perform the action — it just evaluates the logic and conditions of:

- Identity-based policies (AWS Managed, Customer-Managed, Inline)  
- Resource-based policies (like S3 bucket policies)  
- SCPs (Service Control Policies from AWS Organizations)  
- Permission boundaries  
- Session policies  

In short, it’s like a policy debugger for IAM, and it can help pinpoint why something is broken, why it’s over-permissive, or how to tighten things down safely without breaking apps or people.

---

## Cybersecurity Analogy

Think of the IAM Policy Simulator like a sandboxed attack simulation — but instead of simulating malware or lateral movement, you’re simulating permissions boundaries and API access.  

It's your security lab test bench:

- What would happen if Blizzard assumes this role and tries to call `kms:Decrypt` on key XYZ?  
- Will Winterday’s Lambda be able to put logs in this S3 bucket if SCPs are applied?  
- Would this deny statement actually block that API if it’s called via an STS session?

## Real-World Analogy

Imagine your physical data center:  
Someone asks, “Can Nathan swipe his badge and get into the NOC?”  

Instead of testing it in real life and triggering an alarm, you check the building access simulator, where it runs through:

- His badge permissions  
- The door’s rules  
- Whether the access control override from yesterday still applies  
- The visitor policy his badge was inherited from  

Now replace the badge with an IAM role and the door with `s3:PutObject` — that’s what the simulator does.

---

## How It Works

When you run a simulation, it does a full logical evaluation of all the applicable policies, scoped to:

- The IAM entity (user, group, or role)  
- The action(s) you’re simulating (e.g., `ec2:StartInstances`, `s3:GetObject`)  
- The resource(s) you’re targeting (e.g., an S3 bucket ARN)  
- Optional condition keys, tags, or contexts  

It will evaluate:

- All attached identity policies  
- Any inline policies on that identity  
- SCPs from your organization (if applicable)  
- Permission boundaries (if any)  
- Resource-based policies (if included)  
- Session policies (if applicable)  

Then it gives you a simple Allowed / Denied verdict — and if denied, why (e.g., due to boundary or SCP).

---

## Where to Use It

### AWS Console UI  
- Navigate to the **IAM → Policy Simulator**  
- Choose an identity or paste in a policy, choose actions/services, and run simulations.

### AWS CLI / API  
- Useful for automation or testing in CI/CD pipelines. Example:

```bash
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::111122223333:role/SnowySecurityAnalyst \
  --action-names s3:ListBucket \
  --resource-arns arn:aws:s3:::snowy-logs-bucket
```

---

## Policy Simulator Does Not Do

This is critical — the simulator is not perfect. It does not simulate real-time external conditions:

- It does not check if the resource exists  
- It does not validate conditions that depend on live external context (e.g., IP restrictions unless provided manually)  
- It does not simulate MFA requirements unless explicitly passed in  
- It does not simulate session duration or federated identities unless you pass those session details  

You still need real-world testing in staging for high-trust environments — but this gets you 90% of the way there.

---

## Use Cases in a Detection/Architecture Context

- **Why was this action denied?**  
  Simulate and find out whether SCPs, permission boundaries, or resource policies caused it.

- **Will this new policy allow unintended access?**  
  Before deploying a new CustomerManagedPolicy, test it across sensitive actions like `kms:Decrypt` or `iam:PassRole`.

- **Testing ABAC setups**  
  Simulate conditions like `aws:ResourceTag` or `aws:RequestTag` to verify that only tagged resources are accessible.

- **Audit Least Privilege**  
  Pair this with Access Analyzer to simulate what actions are actually possible vs. what is defined on paper.

- **Break Glass Testing**  
  Validate that emergency roles (e.g., `SecurityIncidentResponder`) don’t have access to billing or RDS in normal operations.

---

## Limitations Table

| Capability                            | Supported in Simulator?          |
|---------------------------------------|----------------------------------|
| Identity-based policies               | Yes                              |
| Resource-based policies (S3, etc.)    | Yes                              |
| SCPs                                  | Yes                              |
| Permission Boundaries                 | Yes                              |
| Session Policies                      | Yes                              |
| MFA Context Simulation                | Only if manually added           |
| Dynamic Conditions (e.g. external IP) | Only with manual context         |
| Checks resource existence             | No                               |
| Simulates real API response           | No (only policy logic)           |

---

## Real-Life Snowy Scenario

Blizzard’s team rolls out a new `DataExportLambda` that reads from S3 and writes to a Redshift cluster.  
But when it runs, it fails on `s3:GetObject`. Logs say **AccessDenied**.

Instead of poking in the dark:

- Snowy uses the IAM Policy Simulator  
- Loads the Lambda execution role ARN  
- Simulates `s3:GetObject` on the specific bucket ARN  
- Finds that a **permission boundary** is denying access  

Boom — problem solved before it goes to Prod.

---

## Final Thoughts

In AWS, access logic is layered and complex. You can have permissions that look valid but fail because of SCPs, session policies, or missing tags.  

The IAM Policy Simulator is your best friend for:

- Debugging access failures  
- Validating least privilege before rollout  
- Verifying assumptions before red teaming or incident response  

It’s not a silver bullet — but it’s the first place you should check when someone says  
**“I don’t have access”** or **“This policy should work.”**  

> You can’t fix what you can’t see — and this lets you see the exact decision path.

