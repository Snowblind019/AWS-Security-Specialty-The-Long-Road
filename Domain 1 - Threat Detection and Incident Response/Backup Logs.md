# Backup Logs

AWS Backup has no log stream of its own. Visibility comes from three places: CloudTrail (the API calls — who started, copied, restored, or deleted), CloudWatch metrics and EventBridge (job status and alerting), and Backup Audit Manager (compliance frameworks and coverage reports). For security, the questions that matter are whether backups are actually happening, whether someone is restoring or deleting them without authorization, and whether the backups themselves are protected from tampering.

The shift in thinking for the exam: "backup logging" is less about a feed to read and more about two things — detecting destructive actions against recovery points, and protecting the backups so they cannot be destroyed in the first place. The detection lives in CloudTrail and EventBridge; the protection lives in vault policies and Vault Lock.

## Where the signal comes from

- **CloudTrail** — management events for `StartBackupJob`, `StartRestoreJob`, `DeleteRecoveryPoint`, `CreateBackupVault`, `DeleteBackupVault`, and copy jobs. Source `backup.amazonaws.com`. This is the who/what/when.
- **CloudWatch metrics + EventBridge** — job state (completed / failed / expired). EventBridge rules fire on these for alerting and automated response.
- **Backup Audit Manager** — evaluates resources against controls and frameworks (HIPAA, PCI, SOC 2), flags un-backed-up resources, and exports daily conformance reports to S3.

## Protecting the backups themselves

- **Vault Lock** enforces a WORM retention policy on a backup vault:
  - **Governance mode** — privileged IAM principals can still alter or remove the lock.
  - **Compliance mode** — immutable once the grace period passes; no one, including root, can shorten retention or delete recovery points. This is the ransomware / insider-deletion answer.
- **Vault access policies** (resource policies on the vault), plus IAM, control who can restore or delete.
- Recovery points are **KMS-encrypted**; cross-account and cross-Region copies let you keep an isolated, logically air-gapped copy.

## What gets tested

- AWS Backup has no native log. You assemble visibility from CloudTrail (API actions), CloudWatch/EventBridge (job status and alerting), and Backup Audit Manager (compliance).
- `DeleteRecoveryPoint` and `DeleteBackupVault` in CloudTrail are the signals for detecting destruction of backups — alert on them.
- Vault Lock compliance mode is the control for making recovery points undeletable (ransomware resilience, regulatory retention). Governance mode is bypassable by privileged users; compliance mode is not, even by root.
- Cross-account backup copy into an isolated account limits blast radius if the source account is compromised.
- Backup Audit Manager is how you prove coverage to auditors and catch resources that were never backed up.
- EventBridge is the path for automated alerting on failed or expired jobs.
- Recovery points are encrypted with KMS; vault access policies gate restore and delete.

## Limitations

- No single backup log feed — visibility is stitched together from three services.
- Vault Lock compliance mode is irreversible after the grace/cooling-off window; misconfiguration can lock you out for the full retention period.
- CloudWatch metrics/logs and Backup Audit Manager carry their own costs.
- Compliance reporting depth depends on enabling Audit Manager and selecting the right frameworks.