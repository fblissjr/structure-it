# Access Control Policy

| Field | Detail |
| :--- | :--- |
| **Policy ID** | IT-001 |
| **Version** | 1.0 |
| **Effective Date** | 2024-01-15 |
| **Policy Owner** | Chief Information Security Officer (CISO) |
| **Policy Approver** | Chief Technology Officer (CTO) |
| **Next Review Date** | 2025-01-15 |

---

## 2. PURPOSE

This Access Control Policy establishes the mandatory requirements for granting, managing, reviewing, and revoking access rights to the Company’s information systems, data, and physical facilities. Adherence to this policy is crucial to protect the confidentiality, integrity, and availability of Company assets in alignment with business requirements and regulatory obligations (including SOX and GDPR compliance).

## 3. SCOPE

This policy applies to all employees (full-time, part-time, temporary), contractors, vendors, consultants, and any third-party entities requiring access to the Company’s internal networks, applications, databases, cloud environments (e.g., AWS, Azure), endpoints, and physical data centers, regardless of their location or employment status.

## 4. DEFINITIONS

| Term | Definition |
| :--- | :--- |
| **Least Privilege** | The security principle that a user, program, or process should be granted only the minimum access rights necessary to perform its required function. |
| **MFA** | Multi-Factor Authentication. An authentication method that requires the user to provide two or more verification factors (e.g., password plus a token). |
| **Role-Based Access Control (RBAC)** | An access control method where permissions are associated with roles rather than individual users. |
| **Privileged Account** | An account with elevated rights (e.g., Domain Administrator, Root User, Database Owner) capable of making wide-ranging system changes. |
| **Access Review Cycle** | The periodic mandatory verification process where asset owners confirm the necessity of current user access rights. |
| **Separation of Duties (SoD)** | A control designed to prevent fraud or error by requiring two or more distinct individuals to complete a critical transaction or process. |

---

## 5. POLICY STATEMENTS

### 5.1. Access Provisioning and Assignment

**5.1.1. Authorization Requirement:** All access requests to production systems or sensitive data repositories **must** be formally documented, justified by business need, and approved by both the respective System/Data Owner and the user's direct Manager prior to provisioning by IT Operations.

**5.1.2. Principle of Least Privilege:** All user access **shall** adhere strictly to the Principle of Least Privilege. Access rights **must** be scoped only to the specific resources required to perform the assigned job function.

**5.1.3. Role-Based Standardization:** Access **shall** primarily be managed using predefined Role-Based Access Control (RBAC) groups. Custom, ad-hoc access grants **should** be minimized and require CISO approval if the access exceeds 30 days.

**5.1.4. Segregation of Duties (SoD):** For critical financial systems (e.g., ERP, General Ledger) relevant to SOX compliance, access rights **must** be structured to enforce Separation of Duties. For example, the ability to create a vendor record **must not** reside in the same role as the ability to initiate payment transfers.

**5.1.5. Third-Party Access:** Vendors and external consultants **shall** be granted temporary access, utilizing segregated network segments, and this access **must** expire automatically upon completion of the contracted term or after a maximum duration of 90 days, whichever comes first.

### 5.2. Authentication Requirements

**5.2.1. Multi-Factor Authentication (MFA):** MFA **must** be enforced for all remote access (VPN, web portals), access to cloud administration consoles, and access to any system containing PII or Level 1 sensitive data (as defined in the Data Classification Policy).

**5.2.2. Password Complexity:** User passwords for all internal systems **must** meet a minimum complexity standard of 14 characters, include a mix of character types, and **must not** be reused within the last 12 password changes.

**5.2.3. Idle Session Timeout:** System access sessions, particularly on shared workstations or administrative jump servers, **must** automatically terminate after 15 minutes of inactivity.

### 5.3. Privileged Access Management (PAM)

**5.3.1. Privileged Account Identification:** All user accounts with administrative or "root" level access across development, staging, or production environments **must** be cataloged within the designated Privileged Access Management (PAM) solution.

**5.3.2. Shared Privileged Accounts:** The use of shared, generic Privileged Accounts (e.g., "Admin", "Support") is **prohibited**, except where mandated by legacy infrastructure; any necessary exception **must** be documented and re-approved annually by the CISO.

**5.3.3. Session Monitoring:** All actions performed under a Privileged Account **must** be logged and monitored in real-time. Recordings of privileged command sessions **should** be retained for a minimum of 180 days.

**5.3.4. Privileged Credential Rotation:** Passwords for Privileged Accounts **must** be automatically rotated by the PAM system upon session termination, or at minimum, every 24 hours.

### 5.4. Access Review and Modification

**5.4.1. Periodic Access Review Cycle:** All system owners and data custodians **must** participate in mandatory Access Reviews conducted every **90 days** for critical systems (e.g., Financial, HR, Customer Database) and every **180 days** for standard network access. Any access not justified during the review **must** be revoked within 5 business days.

**5.4.2. Job Role Change Procedure:** When an employee’s role changes (department transfer or promotion), their existing access **must** be reviewed. Access rights associated with the previous role **must** be suspended or removed immediately, and the new role's access profile **must** be granted only after documented approval.

**5.4.3. Termination Procedures:** Upon notification of employee or contractor separation (voluntary or involuntary), Human Resources **shall** immediately notify IT Security. All access credentials, including physical badges and remote access mechanisms, **must** be disabled within **one hour** of the notification timestamp.

### 5.5. Physical Access Control

**5.5.1. Data Center Access:** Access to server rooms and primary data centers **must** be restricted via dual-factor authentication (e.g., badge plus biometric scan). Unaccompanied entry by non-authorized personnel is **prohibited**.

**5.5.2. Visitor Logging:** All visitors to secure areas **must** be escorted at all times by an authorized employee and **must** sign in/out, recording name, company, destination, and purpose of visit. Logs **must** be retained for 12 months.

---

## 6. PROCEDURES

### 6.1. Procedure for Onboarding New Employee Access Request

This procedure outlines the steps required to grant initial access to an employee upon joining the company.

1. **Hiring Initiation:** Human Resources submits the official hiring request to IT Operations, specifying the employee’s start date, department, job title, and manager.
2. **Role Mapping:** IT Security reviews the submitted job title against the established RBAC matrix to determine the baseline set of required system roles.
3. **Management Approval:** The Hiring Manager verifies the required roles align with the Least Privilege principle and formally approves the baseline access profile.
4. **Provisioning:** IT Operations provisions the approved access roles to the necessary platforms (e.g., AD, SaaS applications) no earlier than 24 hours before the official start date.
5. **Security Verification:** Prior to the employee’s first login, IT Security verifies that MFA is properly enabled and that the user account is appropriately segregated from any administrative groups.

### 6.2. Procedure for Emergency Revocation (Suspension of Access)

This procedure must be followed when an employee poses an immediate security risk or upon confirmed breach activity.

1. **Incident Declaration:** Security Operations Center (SOC) or CISO declares an immediate access revocation incident.
2. **Instant Blackout:** IT Operations **must** immediately disable the user’s primary network/AD account (Active Directory account) and revoke all associated session tokens.
3. **Escalation:** IT Operations notifies the CISO and the user’s direct manager that the account has been disabled due to security risk.
4. **Forensic Preservation:** The disabled account’s profile and associated logs **must** be flagged for immediate preservation as part of the potential forensic investigation (referencing the Incident Response Plan).
5. **Follow-up Review:** Within 48 hours, the CISO initiates a formal review to determine if permanent termination of employment/contract is necessary and approves permanent revocation status.

---

## 7. ROLES AND RESPONSIBILITIES

| Role | Responsibility under this Policy |
| :--- | :--- |
| **CISO (Policy Owner)** | Final approval authority for policy exceptions; overall ownership and enforcement; chairing the Access Review process. |
| **IT Operations/System Admins** | The technical execution of granting, modifying, and revoking access according to approved requests; managing PAM vault; ensuring MFA enforcement. |
| **Data/System Owners** | Accountability for determining and approving who requires access to the data or systems they own; responsible for participating in the 90-day Access Reviews. |
| **Human Resources (HR)** | Providing timely notification (within 2 hours) of all terminations, departmental transfers, or status changes. |
| **All Employees/Users** | Protecting their credentials, complying with MFA requirements, and immediately reporting any suspected unauthorized access activity. |

## 8. COMPLIANCE AND ENFORCEMENT

**8.1. Verification:** Compliance with this policy will be verified through scheduled internal audits conducted by the Internal Audit team, regular log monitoring by the SOC team, and mandatory annual testing of access controls against established SOX requirements.

**8.2. Reporting Deficiencies:** Any employee who identifies a potential violation of this policy **must** report it immediately to the CISO or via the confidential Whistleblower Hotline.

**8.3. Consequences of Non-Compliance:** Any employee found to be in violation of this Access Control Policy **may** be subject to disciplinary action, up to and including immediate termination of employment or contract, depending on the severity and intent of the violation. Access privileges incorrectly granted or maintained outside the defined review cycles **will** be automatically reversed by IT Operations, regardless of managerial instruction.

---

## 9. RELATED DOCUMENTS

*   IT-003: Password Management Standard
*   IT-005: Incident Response Plan
*   IT-010: Data Classification Policy
*   HR-002: Employee Termination and Offboarding Procedures

---

## 10. VERSION HISTORY

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 1.0 | 2024-01-15 | CISO Office | Initial baseline release of the Access Control Policy. |