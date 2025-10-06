# Disabling Plaintext Protocols (FTP, Telnet, HTTP)

## What Are Plaintext Protocols

Plaintext protocols are network protocols that transmit data without encryption, making them:

- Readable by anyone in the traffic path (ISPs, proxies, compromised routers)  
- Vulnerable to man-in-the-middle (MITM) attacks  
- Non-compliant with modern standards  

**Common offenders:**

| **Protocol** | **Port** | **Danger**                       | **Secure Alternative**  |
|--------------|----------|----------------------------------|--------------------------|
| FTP          | 21       | Sends creds + data in plaintext  | SFTP, FTPS               |
| Telnet       | 23       | Remote shell with no encryption  | SSH                      |
| HTTP         | 80       | Plaintext web/API traffic        | HTTPS (TLS 1.2+)         |
| SMTP (unsecured) | 25   | Plaintext email transport        | SMTP with STARTTLS       |

---

## Cybersecurity Analogy

Using plaintext protocols is like sending confidential letters written on **postcards**.  
Anyone in the post office — or along the route — can:

- Read your message  
- Modify it  
- Forward it to someone else  

**Encryption (TLS/SSH) turns that postcard into a tamper-proof, sealed envelope.**

## Real-World Analogy

Let’s say your company warehouse logs employee check-ins using **walkie-talkies (plaintext)**.

- Anyone nearby can listen in  
- Someone can impersonate an employee  
- There’s no record of what was said  

Switching to secure, encrypted comms (SSH/SFTP/HTTPS) is like moving to **encrypted headsets with identity authentication**.

---

## Where These Protocols Might Appear in AWS

| **Use Case / Location**          | **Risk Protocol** | **Secure Alternative**           |
|----------------------------------|-------------------|----------------------------------|
| Admin access to EC2              | Telnet            | SSH / SSM Session Manager        |
| Web server default config        | HTTP              | HTTPS (TLS 1.2+)                 |
| File uploads/downloads to EC2    | FTP               | SFTP / HTTPS / SCP               |
| Third-party integrations         | HTTP endpoints    | HTTPS APIs                       |
| User uploads to S3 via script    | HTTP PUT          | HTTPS + Signed URL               |
| Custom-built internal tools      | HTTP/Telnet       | HTTPS + mTLS / SSH               |

---

## How to Disable Plaintext Protocols in AWS (Step by Step)

### 1. Block Known Ports in Security Groups & NACLs

| **Protocol** | **Port** | **Action**              |
|--------------|----------|--------------------------|
| FTP          | 21       | ❌ Deny Inbound + Outbound |
| Telnet       | 23       | ❌ Deny All               |
| HTTP         | 80       | ❌ Deny or redirect via ALB |
| SMTP         | 25       | ❌ Block or force STARTTLS  |

- Use **Security Groups** to deny inbound and outbound traffic on these ports  
- Use **Network ACLs** for broader enforcement at the subnet level  

### 2. Use S3 Bucket Policies to Deny Non-HTTPS Access

```json
"Condition": {
  "Bool": {
    "aws:SecureTransport": "false"
  }
}
```

- Blocks HTTP API calls to S3  
- Works globally — CLI, SDK, tools, users

### 3. Disable HTTP on ALBs / CloudFront

- Set **ALB Listener on port 80** to redirect to HTTPS  
- Set **CloudFront Viewer Protocol Policy** to:  
  - HTTPS Only  
  - or Redirect HTTP to HTTPS  

- Prevents clients from ever connecting over plaintext

### 4. Use SSM Instead of Telnet/SSH Where Possible

- Block **port 23 (Telnet)** and **port 22 (SSH)**  
- Use **SSM Session Manager**  
- Enforce:  
  - IAM-based access  
  - Command logging  
  - CloudTrail session logs  

### 5. Detect and Replace FTP

- If you see **port 21** open on any EC2:  
  - Replace with **SFTP (SSH-based)** or **HTTPS-based uploads**  
  - Remove old **`vsftpd`** or **`proftpd`** packages  

### 6. Use IAM Policies to Enforce Secure API Use

You can conditionally deny actions unless certain secure headers/protocols are used:

```json
"Condition": {
  "BoolIfExists": {
    "aws:ViaAWSService": "false"
  }
}
```

### 7. Monitor with VPC Flow Logs + GuardDuty

- Use **VPC Flow Logs** to detect connections on ports **21**, **23**, **80**  
- Use **GuardDuty** to catch:  
  - Unusual ports  
  - Communications with known malware hosts over plaintext  
  - Unencrypted credentials (via packet inspection in some cases)  

---

## Best Practices Summary

| **Action**                      | **Why It Matters**                               |
|----------------------------------|---------------------------------------------------|
| Block FTP, Telnet, HTTP ports    | Prevents entry points for sniffing & replay      |
| Redirect HTTP to HTTPS           | Helps users/devs follow secure defaults          |
| Use `aws:SecureTransport` in S3  | Forces clients to encrypt data in transit        |
| Use SFTP/SCP for file transfer   | Secure file transport without exposing FTP       |
| Use IAM + TLS for API calls      | Ensures identity + encryption                    |
| Log and alert on legacy ports    | Detect any backdoors, misconfigs, or drift       |
| Document & audit protocol usage  | Helps during compliance (PCI, HIPAA, etc.)       |

---

## Real-Life Example (Snowy’s Secure VPC Cleanup)

Snowy inherits an old VPC with:

- EC2s running FTP + Telnet for remote support  
- A custom PHP app exposed on **port 80 only**  
- S3 buckets that allowed `http://` requests from scripts  

### Actions Taken:

- **FTP/Telnet packages removed**  
- **Ports 21 and 23 blocked** in security groups  
- **HTTP → HTTPS redirects** enabled in ALB  
- **S3 buckets enforced `aws:SecureTransport`**  
- **CloudWatch alarms** set on ports 21, 23, 80 via VPC Flow Logs  
- **All file uploads migrated** to signed S3 HTTPS PUTs  
- **Partner integrations updated** to use HTTPS only  

### Result:

✔️ Zero plaintext protocols remain  
✔️ All data-in-transit is encrypted  
✔️ Satisfies compliance checks  
✔️ Attack surface reduced significantly

---

## Final Thoughts

Plaintext protocols like **FTP**, **Telnet**, and **HTTP** are dinosaurs in the cloud — and they bring serious security baggage:

- No encryption  
- No authentication integrity  
- No audit trail  
- Total exposure  

In AWS, you have **full control** over which ports, protocols, and headers get in — so use that power:

- Block the bad  
- Enforce the encrypted  
- Monitor for violations  
- Stay compliant and cloud-native
