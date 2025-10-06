# AWS Amplify

## What Is AWS Amplify

AWS Amplify is a *front-to-backend* framework that simplifies the process of building full-stack web and mobile applications on AWS. It abstracts away a lot of the underlying infrastructure pain — letting *frontend* developers spin up and manage powerful *backend* resources like authentication, databases, storage, and APIs **without having to touch CloudFormation, IAM, or write custom backend code.**

Amplify is important because it empowers *frontend* teams (like *Snowy’s* UI squad) to build secure, scalable apps that integrate with AWS-native services (like *Cognito, AppSync*, S3, Lambda, etc.) **in just a few commands or clicks.**

So instead of saying “I need a *backend* team to provision *Cognito* and API Gateway,” a *frontend* dev can just run:

```
amplify add auth  
amplify push
```

And boom — it scaffolds a secure authentication system using AWS *Cognito* and deploys it.

---

## Cybersecurity Analogy

Think of Amplify like giving a junior developer a secure coding kit.

It’s a bit like giving someone a **"build-your-own-vault"** kit — they don’t need to know how the steel is forged or how the *biometric* scanner encrypts access — they just choose a few settings (number of locks, who gets keys, etc.) and the vault is built securely for them using hardened materials.

But if they *don’t know what they’re doing*, they could still leave the door open.

So the security posture of Amplify apps **depends heavily on the developer’s awareness** of:

- How *API keys, environment secrets, and tokens* are handled in CI/CD  

It’s secure *by default*, but only if you follow best practices. That’s why security engineers must **review Amplify apps before production.**

## Real-World Analogy

Imagine **Winterday** is building a mobile app for their winter gear business. They want users to:

- Sign up/login  
- Upload photos of gear  
- Chat with support  
- Track orders  

They don’t have *backend* engineers. Just React Native *frontend devs*.

Instead of waiting months for *backend* infrastructure to be built, they just run:

- `amplify init` – sets up the Amplify project  
- `amplify add auth` – sets up *Cognito* user pools  
- `amplify add storage` – sets up *S3* with *IAM* permissions  
- `amplify add api` – sets up *GraphQL* API using *AppSync*  
- `amplify push` – deploys the whole stack  

Within a week, the app is working with a fully managed *backend*, secure login, and S3 photo upload — all using AWS best practices in the background.

But here’s the kicker: **if they didn’t review the IAM permissions** or check if the API is open to the world, they could be leaking data or **over-permissioning users** — unknowingly creating **privilege escalation paths** or **unauthorized access routes**.

---

## How It Works

Amplify consists of two core pieces:

### 1. Amplify CLI / Admin UI

- Lets devs scaffold *backend* resources like *Cognito, AppSync*, DynamoDB, S3, Lambda, etc.  
- Uses **preconfigured CloudFormation** templates behind the scenes  
- Generates *TypeScript/JavaScript/iOS/Android SDKs* with ready-to-use functions (e.g., `Auth.signIn()`, `Storage.put()`, etc.)

### 2. Amplify Hosting

- CI/CD pipeline for deploying full-stack apps (*React, Vue, Angular, Next.js*)  
- Supports environment branches like *dev/test/prod*  
- Integrates directly with *GitHub, GitLab, Bitbucket*

### 3. Amplify Libraries

- Client-side *SDKs* to interact with AWS services using Amplify *backend* config  
- Handles token refreshes, *Cognito* sessions, file uploads, subscriptions, etc.


### 4. Amplify Studio

- Visual tool to build UI + *backend*  
- Drag-and-drop component building (with *Figma* integration)  

- Binds UI to *backend* data (like Amplify *DataStore* or *GraphQL*)

---

## Pricing Models

Amplify pricing is split across:

| Component            | Pricing                                                                 |
|----------------------|-------------------------------------------------------------------------|
| **Amplify Hosting**  | Based on build & hosting time, bandwidth used                           |
| **Amplify Backend**  | Charged based on underlying AWS services used (*Cognito*, S3, etc.)     |
| **Amplify Studio**   | Free to use, but underlying services are billed normally                |
| **Amplify DataStore**| No extra charge, but syncs with *AppSync/DynamoDB* (which are billed)   |

The Amplify **CLI** itself is free — you only pay when AWS services are deployed and used.

**Pro tip:** *If you leave environments running*, you might be paying for idle DynamoDB tables, *Cognito* users, or S3 buckets.

---

## Other Explanations

- **Environment drift:** If you don’t properly manage branches and environments (*dev, staging, prod*), you can end up with inconsistent *backend* configs. Use Amplify environments (`amplify env`) carefully.

- **Over-permissive IAM roles:** Amplify automatically generates *IAM* roles — if you blindly accept defaults, your app may have more access than it needs. Always review the generated *CloudFormation/IAM* policies.

- **Public APIs:** *AppSync* APIs created by Amplify can be either public or private depending on auth mode. Public unauthenticated *GraphQL* APIs have been exploited in past **misconfigurations**.

- **DataStore caveats:** Amplify’s *DataStore* (for offline sync) works well but may confuse developers who don’t realize it syncs to *AppSync/DynamoDB* behind the scenes. That sync can leak data if not scoped properly.

---

## Real-Life Example: SnowyCorp Internal Dashboard

*SnowyCorp’s* internal engineering team needed a way to let interns submit logs, track bugs, and visualize AWS events — but without giving them access to *CloudTrail* or the AWS Console.

So they built a **React frontend** that:

- Uses `amplify add auth` → *Cognito* login  
- Uses `amplify add api` → *GraphQL* API to DynamoDB with limited fields per user  
- Uses `amplify add function` → Lambda that filters log access based on user identity  
- Uses `amplify add storage` → S3 bucket for image uploads  

**Security added the following:**

- *IAM* role boundaries to ensure no lateral movement  
- *GuardDuty* alerts on any suspicious activity from Amplify apps  
- *CloudWatch* dashboards to track API call volume and data **exfil**

Now interns can:

- Log in securely  
- Submit logs via *GraphQL* mutation  
- Upload screenshots  
- View only their own bug reports  

**All without risking exposure to the core AWS account.**

---

## Final Thoughts

Amplify is amazing — especially for startups, *frontend-heavy* teams, and rapid *MVPs*.

But it’s also dangerous in the hands of someone who doesn’t understand AWS fundamentals. You can build a production-scale app **without ever learning what IAM is**, and that’s both empowering *and* terrifying.

If you're a security engineer, **review every Amplify app like you would review Terraform.** It’s just infrastructure-as-code with training wheels — and if you hit a hill too fast, those wheels come flying off.

Use Amplify to build fast. But **secure what it builds**. Understand what it provisions. Know when to customize, when to audit, and when to say:  
“Let’s hook this into *IAM* boundaries, *Secrets Manager, WAF, GuardDuty,* and monitoring.”

Amplify lowers the bar to entry. Your job is to **raise the bar on security.**

