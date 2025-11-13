# Acceptable Use Policy (AUP)

## 1. DOCUMENT HEADER

| Field | Detail |
| :--- | :--- |
| **Policy ID** | IT-001 |
| **Version** | 1.2 |
| **Effective Date** | 2024-01-15 |
| **Review Date** | 2025-01-15 |
| **Policy Owner** | Chief Information Security Officer (CISO) |
| **Approver** | Chief Executive Officer (CEO) |
| **Classification** | Internal Confidential |
| **Document Status** | **Approved** |

---

## 2. PURPOSE

This Acceptable Use Policy (AUP) establishes the rules and guidelines for the appropriate use of **TechCorp**’s information technology resources, including all hardware, software, networks, and data. The primary purpose of this policy is to protect the confidentiality, integrity, and availability of **TechCorp**’s critical assets, ensuring compliance with legal and contractual obligations (such as **SOC 2** and **GDPR** requirements).

This policy supports **TechCorp**’s strategic commitment to maintaining a secure and productive work environment. Misuse of company resources can lead to data breaches, operational downtime, financial loss, and reputational damage. Adherence to these standards is mandatory for all individuals utilizing company systems.

---

## 3. SCOPE

This policy applies to **all employees, contractors, vendors, and temporary staff** accessing or using **TechCorp**’s IT infrastructure, regardless of location.

**Covered Systems:** This policy covers all company-owned or leased assets, including, but not limited to: corporate laptops, mobile devices, email systems, internal servers, cloud services (SaaS/IaaS), network access points, and all data classified as **Confidential** or **Restricted**.

**Geographic Scope:** This policy applies globally to all personnel accessing **TechCorp** systems, including those working remotely, unless superseded by a more restrictive local law or specific regional policy.

**Exclusions:** No formal exclusions exist for this policy, though specific system configurations (e.g., specialized testing environments) may have supplementary controls documented elsewhere.

---

## 4. DEFINITIONS

| Term | Definition |
| :--- | :--- |
| **AUP** | Acceptable Use Policy. |
| **Confidential Data** | Internal business data not intended for public release (e.g., internal memos, financial reports). |
| **MFA** | Multi-Factor Authentication; a security process requiring two or more verification factors. |
| **Restricted Data** | Highly sensitive data subject to strict regulatory control (e.g., customer PII, source code, payment card information subject to **PCI-DSS**). |
| **System Administrator** | Personnel within the IT department authorized to manage and configure critical infrastructure. |
| **Phishing** | A social engineering attack, typically via email, designed to trick users into revealing sensitive information. |
| **Workstation** | Any end-user device (laptop, desktop) provided or provisioned by **TechCorp**. |

---

## 5. POLICY STATEMENTS

### A. Access Control and Authentication

*   **MANDATORY:** All remote access to the corporate network **must** utilize company-approved Virtual Private Network (VPN) access enabled with **MFA**.
*   **MANDATORY:** User passwords **shall** meet complexity requirements (minimum 12 characters, mixing case, numbers, and symbols) and **must not** be reused across external services.
*   **MANDATORY:** System Administrators **must** maintain the principle of least privilege; access rights **shall** be reviewed quarterly by the relevant department head.

### B. Data Handling and Classification

*   **MANDATORY:** All **Restricted Data** stored on **Workstations** or removable media **must** be encrypted using approved AES-256 encryption standards.
*   **MANDATORY:** Employees **shall not** upload **Confidential Data** to unauthorized external cloud storage providers (e.g., personal Google Drive or Dropbox accounts).
*   **RECOMMENDED:** Employees **should** limit the transmission of **Confidential Data** via unencrypted channels (e.g., public Wi-Fi) unless utilizing **TechCorp**’s secure communication tools.

### C. System Security and Maintenance

*   **MANDATORY:** Users **must not** attempt to bypass, disable, or uninstall security software, including endpoint protection or DLP agents, installed on **TechCorp** devices.
*   **MANDATORY:** All security patches released by the IT department **must** be installed on **Workstations** within **14 calendar days** of notification, unless an official exception is granted by the Security Operations Center (SOC).
*   **PROHIBITED:** The installation of unauthorized software, including peer-to-peer file-sharing applications, **is strictly forbidden** on any company asset.

### D. Incident Reporting

*   **MANDATORY:** Any suspected security incident, including successful **Phishing** attempts or loss of a company device, **shall** be reported immediately to the IT Helpdesk within **one hour** of discovery.

---

## 6. PROCEDURES

### 6.1 Procedure for Reporting Security Incidents

This procedure ensures rapid response as required by Policy Statement 5.D.

1.  **Detection:** The user identifies a potential security issue (e.g., receiving a suspicious email, noticing unauthorized access).
2.  **Immediate Action:** The user isolates the affected system (e.g., disconnect from the network if physical loss is suspected, or close the application).
3.  **Reporting:** The user contacts the IT Helpdesk via phone or the dedicated internal security hotline, referencing the **IT-001 Policy**.
4.  **Triage and Documentation:** The Helpdesk logs the incident, assigns a severity level, and immediately escalates all Severity 1 (Critical) incidents to the Security Operations Center (SOC) within **30 minutes**.

### 6.2 Procedure for Requesting New Software Installation

1.  **Submission:** The user submits a formal request detailing the business justification and necessity for the new software via the IT Service Management (ITSM) portal.
2.  **Security Review:** The request is automatically routed to the Security Review Team (SRT). The SRT assesses the software against security benchmarks (e.g., vendor SOC 2 report availability).
3.  **Approval Workflow:** If the software handles **Confidential Data**, the CISO must provide explicit approval. If the software costs exceed **$5,000**, the Department Head must also approve.
4.  **Deployment:** Upon final approval, IT deploys the software, ensuring any necessary configuration changes (e.g., firewall rules) are documented.

---

## 7. ROLES AND RESPONSIBILITIES

| Role/Title | Specific Responsibilities Under IT-001 | Approval Authorities |
| :--- | :--- | :--- |
| **All Employees/Users** | Adhere to all mandatory and recommended statements; report incidents immediately. | N/A |
| **Chief Information Security Officer (CISO)** | Owns, maintains, and enforces this policy; reviews exceptions. | Approves all exceptions to Section 5.C (Patching). |
| **IT Helpdesk** | Initial documentation and triage of reported incidents (6.1). | N/A |
| **System Administrators** | Ensure technical controls (MFA, Encryption) are properly implemented and monitored. | Granting/Revoking system access based on roles. |
| **Chief Executive Officer (CEO)** | Final approval authority for the policy document. | Final Policy Approval. |

---

## 8. COMPLIANCE AND ENFORCEMENT

**Monitoring:** Compliance with this AUP will be monitored through automated system audits (e.g., configuration drift checks, endpoint security reporting) and periodic user access reviews conducted by the Internal Audit team.

**Audits:** The Internal Audit department will conduct a formal review of compliance with this policy at least **annually**.

**Consequences of Violations:** Violations of this policy will be handled according to the **TechCorp** Disciplinary Action Policy. Violations involving unauthorized disclosure of **Restricted Data** or willful circumvention of security controls may result in immediate suspension, termination of employment or contract, and potential legal action.

**Reporting Violations:** All employees are required to report observed or suspected violations of this policy to their manager or the CISO immediately. Anonymous reporting is available via the Ethics Hotline.

---

## 9. EXCEPTIONS

Any request for deviation from a **MANDATORY** requirement in Section 5 must be documented using the **IT Exception Request Form (IT-FORM-001)**.

Exceptions must demonstrate that equivalent compensating controls are in place to mitigate the associated security risk.

**Approval Authority:** Exceptions to this policy **must** be reviewed by the CISO and formally approved by the Department Head sponsoring the activity. Exceptions for **Restricted Data** handling require CEO approval. All approved exceptions **shall** be reviewed and reassessed every **six months**.

---

## 10. RELATED DOCUMENTS

1.  Information Security Incident Response Plan (IT-PLN-003)
2.  Data Classification Standard (IT-STD-002)
3.  Remote Access and Mobile Device Management Policy (IT-005)
4.  Acceptable Software Installation Procedure (IT-PROC-012)

**Relevant Regulations:** This policy directly supports compliance requirements for **SOC 2 Type II** reporting and data protection mandates under **GDPR**.

---

## 11. APPENDICES

*(No appendices are required for this simple policy version.)*

---

## 12. VERSION HISTORY

| Version | Date | Changes | Approved By |
| :--- | :--- | :--- | :--- |
| 1.0 | 2022-06-01 | Initial release based on pre-merger security baseline. | J. Smith (CEO) |
| 1.1 | 2023-03-15 | Updated approval thresholds for new software purchases (Section 6.2). | A. Chen (CEO) |
| 1.2 | 2024-01-15 | Added remote work provisions and strengthened MFA requirements; added SOC 2 compliance note. | M. Davies (CEO) |