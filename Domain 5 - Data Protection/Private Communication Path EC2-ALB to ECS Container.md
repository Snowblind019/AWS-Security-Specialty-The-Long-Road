# Private Communication Path: ALB to ECS Container

This is the common pattern where an Application Load Balancer receives traffic and forwards it to an ECS container (a public site, private API, or internal microservice). The security point that trips people up is that encryption on the back hop, ALB to container, is optional and independent of the front hop. An HTTPS listener secures client-to-ALB, but by default the ALB terminates TLS and forwards plain HTTP to the target unless you also set the target group to HTTPS and run TLS in the container. So "the outside is HTTPS" does not mean the traffic inside the VPC is encrypted. The thing to hold onto: end-to-end encryption requires three things together (HTTPS listener, HTTPS target group protocol, and TLS terminating in the container), it is opt-in and not enforced by AWS, and the default HTTPS-at-the-edge, HTTP-inside setup leaves a plaintext segment between the ALB and ECS.

## How it works

- **The listener secures the front hop.** An HTTPS listener on the ALB establishes TLS from the client to the ALB and, by default, terminates it there, meaning the ALB decrypts and forwards. An HTTP listener means the front hop itself is plaintext.
- **The target group protocol decides the back hop.** A target group set to HTTP sends plaintext from ALB to the container even when the listener was HTTPS. A target group set to HTTPS re-encrypts ALB-to-container, which is what you need for end-to-end.
- **The container must actually terminate TLS.** For an HTTPS target group to work, the ECS container has to listen on TLS with a cert. If the app only speaks HTTP, setting the target group to HTTPS fails the health checks.
- **ALB always terminates, it does not pass through.** The ALB is a Layer 7 load balancer that decrypts to inspect and route, so true TLS passthrough (client cert reaching the container untouched) is not an ALB feature. Passthrough requires an NLB (Layer 4) or a TCP/TLS design, which is the pattern when the container must see the original TLS session.
- **End-to-end needs all three pieces.** HTTPS listener plus HTTPS target group plus TLS in the container gives client-to-ALB and ALB-to-container both encrypted. Miss any one and there is a plaintext hop.
- **Observability sits alongside.** ELB access logs and VPC Flow Logs give you visibility into the traffic, which matters because a misconfigured back hop is otherwise invisible.

## ALB-to-ECS encryption combinations

| Listener | Target group | Result |
|---|---|---|
| **HTTP** | HTTP | No encryption anywhere |
| **HTTPS** | HTTP | Client-to-ALB encrypted, ALB-to-ECS plaintext (default) |
| **HTTPS** | HTTPS | Encrypted both hops (needs TLS in the container) |
| **NLB / TCP passthrough** | Container terminates | End-to-end, container sees original TLS (mTLS possible) |

## What gets tested

- **HTTPS listener alone is not end-to-end.** The default terminates TLS at the ALB and forwards HTTP. If a scenario requires encryption all the way to the container, the answer sets the target group protocol to HTTPS and runs TLS in the container, not just an HTTPS listener.
- **ALB terminates, NLB passes through.** When the requirement is that the container must see the original TLS session or perform client-cert (mTLS) validation itself, that is an NLB with TLS passthrough (or a TCP design), because an ALB always decrypts.
- **Target group protocol is the back-hop control.** The exam tests whether you know the listener and the target group protocol are independent, and that the target group is what encrypts ALB-to-target.
- **Internal does not mean encrypted.** A private ECS service reachable only inside the VPC still receives plaintext over the back hop unless HTTPS is configured. Network privacy is not encryption.
- **Compliance end-to-end.** PCI/HIPAA scenarios that demand encryption in transit throughout require the full three-piece setup, not edge-only TLS.

## Limitations

- The ALB cannot do TLS passthrough. It always terminates at Layer 7, so client-cert-to-container or seeing the raw TLS session needs an NLB or TCP-mode design.
- End-to-end encryption is entirely opt-in and requires coordinated config across the listener, target group, and the container app, so any single default left in place leaves a plaintext hop.
- An HTTPS target group requires the container to terminate TLS with a valid cert, adding cert management inside the container that many teams skip, defaulting back to HTTP internally.
- Terminating at the ALB means the ALB sees plaintext, so a compromised ALB exposes the traffic. End-to-end TLS or mTLS reduces that implicit trust.
- Network-level privacy (private subnets, security groups) is not a substitute for encryption in transit, so relying on "it is internal" leaves the back hop unprotected against in-VPC sniffing.
- Misconfigured back-hop encryption is easy to miss without ELB access logs and Flow Logs, so observability is required to catch a silently plaintext internal segment.