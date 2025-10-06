# Amazon SQS

## What Is the Service

Amazon SQS (Simple Queue Service) is a fully managed message queuing service that enables asynchronous decoupling between microservices, applications, and distributed components. Instead of calling services directly, producers drop a message into a queue, and consumers pull messages at their own pace.  
This is absolutely crucial in:

- Distributed architectures (like microservices or serverless)  
- High-availability systems that must survive spikes and failures  
- Security-sensitive systems that need message buffering, delivery guarantees, and controlled retries  

There are two types of SQS queues:

| Queue Type   | Use Case                                                   |
|--------------|------------------------------------------------------------|
| Standard Queue | Best-effort ordering, unlimited throughput, at-least-once delivery |
| FIFO Queue     | First-in-first-out ordering, exactly-once processing, limited throughput |

---

## Cybersecurity Analogy

Think of SQS like a secure mailbox between departments.  
Instead of shouting across the office (tight coupling), one team writes messages and drops them into a locked box. The other team checks the box at intervals and processes what’s there.

**Security bonus:**

- Only authorized users can write to the box (`SendMessage`)  
- Only certain systems can read from it (`ReceiveMessage`)  
- Messages can be encrypted, signed, delayed, retried, or dead-lettered  

## Real-World Analogy

Imagine Snowy has a printing service. Customers submit jobs via a form (producer), and the printer (consumer) works through the backlog.  
SQS is the stack of jobs sitting in the queue — Snowy’s printer won’t break if 1000 jobs arrive at once, because it processes one at a time.

You can:

- Set timeouts for how long a job stays hidden while being worked on  
- Retry failed jobs  
- Move “bad jobs” to a Dead-Letter Queue (DLQ)  

---

## How It Works

1. Producer sends a message to a queue via `SendMessage`  
2. The message is stored redundantly across multiple AZs  
3. Consumer calls `ReceiveMessage` to pull a message  
4. A **Visibility Timeout** is triggered — no other consumer sees the message  
5. The consumer processes it and deletes it with `DeleteMessage`  
6. If processing fails, message reappears for redelivery  

### Security & Reliability Features:

| Feature               | Description                                             |
|-----------------------|---------------------------------------------------------|
| At-least-once Delivery | Standard queues may redeliver                          |
| Exactly-once (FIFO)    | FIFO queues enforce deduplication                      |
| Dead Letter Queue (DLQ)| Failed messages are rerouted after `maxReceiveCount`  |
| Server-Side Encryption (SSE) | Uses AWS KMS to encrypt messages at rest          |
| Access Control         | IAM policies + queue policies (fine-grained control)   |
| Auditability           | CloudTrail records all SQS API calls                   |
| Message Delay          | Introduce delays (0–15 min) to throttle behavior       |
| Message Retention      | 1 min to 14 days                                       |

---

## SQS + KMS (Encryption)

You can enable Server-Side Encryption with your own CMK:

- SQS encrypts the body using a data key  
- That data key is encrypted with the CMK  
- Decryption happens automatically when message is read  

**CloudTrail logs include:**

- `SendMessage` with `kmsKeyId`  
- `ReceiveMessage` and `Decrypt` operations (tracked via KMS logs)  

---

## SQS Policy Controls

You can use:

- IAM policies to control who can call SQS actions  
- Queue policies to control which AWS principals can send or receive messages from the queue  

**Example:**

```json
{
  "Effect": "Deny",
  "Principal": "*",
  "Action": "sqs:SendMessage",
  "Condition": {
    "Bool": {
      "aws:SecureTransport": "false"
    }
  }
}
```
This denies unencrypted HTTP calls — enforcing TLS.

---

## SQS + Other Security Services

| Integration     | Purpose                                     |
|-----------------|---------------------------------------------|
| KMS             | Encrypt messages at rest                    |
| CloudTrail      | Audit SQS API calls                         |
| CloudWatch      | Monitor queue depth, processing failures, DLQ activity |
| IAM             | Restrict who can access and send messages   |
| SNS → SQS       | Fan-out messaging for alerting systems      |
| EventBridge     | Route SQS messages based on patterns or events |
| Lambda          | Trigger functions based on new messages     |

---

## Best Practices

- Use FIFO queues for transactional workflows  
- Attach DLQs to catch poison messages  
- Enable KMS encryption with customer-managed keys  
- Use queue policies to restrict access by source VPC or service  
- Monitor with CloudWatch metrics: **`ApproximateNumberOfMessagesVisible`** **`NumberOfMessagesDeleted`** **`NumberOfMessagesReceived`**  
- Don’t forget to delete messages after processing  
- Don't trust the sender — validate message content before acting  

---

## CloudTrail Audit Events

You’ll see API calls like:

- `SendMessage`  
- `ReceiveMessage`  
- `DeleteMessage`  
- `PurgeQueue`  
- `SetQueueAttributes`  

…and KMS events like:

- `Decrypt`  
- `GenerateDataKey`  

Pair this with **CloudTrail Lake** to correlate SQS usage with suspicious patterns.

---

## Real-Life Security Example (Snowy’s Use Case)

**Winterday’s Lambda** analyzes financial reports uploaded to S3 and sends parsing jobs to SQS.

- Only Lambda has `SendMessage` permission  
- Another Lambda — in a secure VPC — is the only consumer  
- Messages are encrypted with a CMK owned by Snowy  
- Messages that fail parsing 5x go to a DLQ  
- CloudTrail + CloudWatch detect spikes in failures and alert the NOC team  
- Lambda pulls messages only over TLS, enforced by queue policy  

---

## Final Thoughts

SQS is more than just a buffer — it’s a security boundary, a reliability shield, and a blast radius reducer.  
It enforces:

- Loose coupling  
- Controlled retry logic  
- Payload encryption  
- Strict access control  

Security in motion isn’t just about encrypted traffic — it’s also about controlled workflows, accountable retries, and dead-letter recovery. That’s what SQS gives you.
