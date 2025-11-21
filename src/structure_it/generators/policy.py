"""Policy document generator for creating synthetic policy content."""

from typing import Any

from google.genai import types

from structure_it.generators.base import BaseGenerator


class PolicyGenerator(BaseGenerator):
    """Generate realistic synthetic policy documents.

    Extends BaseGenerator with policy-specific generation logic
    and formatting.
    """

    def _get_policy_owner(self, policy_type: str) -> str:
        """Get appropriate policy owner for policy type.

        Args:
            policy_type: Type of policy.

        Returns:
            Title of the policy owner.
        """
        owners = {
            "Financial": "Chief Financial Officer (CFO)",
            "IT Security": "Chief Information Security Officer (CISO)",
            "HR": "Chief Human Resources Officer (CHRO)",
            "Legal": "General Counsel",
            "Compliance": "Chief Compliance Officer (CCO)",
        }
        return owners.get(policy_type, "Chief Operating Officer (COO)")

    def _get_approver(self, policy_type: str) -> str:
        """Get appropriate approver for policy type.

        Args:
            policy_type: Type of policy.

        Returns:
            Title of the approver.
        """
        approvers = {
            "Financial": "Audit Committee",
            "IT Security": "Chief Executive Officer (CEO)",
            "HR": "Chief Executive Officer (CEO)",
            "Legal": "Board of Directors",
            "Compliance": "Board of Directors",
        }
        return approvers.get(policy_type, "Chief Executive Officer (CEO)")

    def _get_domain_specific_guidance(self, policy_type: str) -> str:
        """Get domain-specific requirement guidance.

        Args:
            policy_type: Type of policy.

        Returns:
            Guidance string for the generator prompt.
        """
        guidance = {
            "Financial": """
   FINANCIAL SPECIFIC REQUIREMENTS:
   - Approval thresholds at multiple levels ($1K, $10K, $50K, $100K, $500K+)
   - Segregation of duties (who requests vs. who approves vs. who processes)
   - Budget controls and variance reporting
   - Financial reporting deadlines
   - Audit trail requirements
   - SOX 404 compliance where relevant
   - Vendor payment terms and approvals
   - Capital vs. operational expense classification
""",
            "IT Security": """
   IT SECURITY SPECIFIC REQUIREMENTS:
   - Access control levels (read, write, admin)
   - Authentication requirements (MFA, password complexity)
   - Data classification (public, internal, confidential, restricted)
   - Encryption requirements (at rest, in transit)
   - Logging and monitoring requirements
   - Incident response timeframes (detect, contain, remediate)
   - Patch management schedules
   - Third-party security assessments
   - GDPR, SOC2, ISO 27001 compliance
""",
            "HR": """
   HR SPECIFIC REQUIREMENTS:
   - Employee conduct expectations
   - Performance review cycles and criteria
   - Leave accrual and approval requirements
   - Training and certification requirements
   - Disciplinary procedures and escalation
   - Equal opportunity and anti-discrimination
   - Workplace safety obligations
   - Confidentiality and non-compete
""",
            "Legal": """
   LEGAL SPECIFIC REQUIREMENTS:
   - Regulatory compliance obligations
   - Disclosure and reporting requirements
   - Contract approval thresholds
   - Intellectual property protection
   - Litigation holds and document retention
   - Whistleblower protections
   - Regulatory citations (specific laws, regulations)
   - Risk assessment and mitigation
""",
            "Compliance": """
   COMPLIANCE SPECIFIC REQUIREMENTS:
   - Regulatory framework references (specific regulations)
   - Monitoring and reporting schedules
   - Audit and verification procedures
   - Certification and attestation requirements
   - Regulatory training requirements
   - Compliance committee oversight
   - Risk assessments and controls testing
   - Regulatory change management
""",
        }
        return guidance.get(policy_type, "")

    async def generate_policy(
        self,
        policy_id: str,
        policy_title: str,
        policy_type: str,
        complexity: str = "medium",
        version: str = "1.2",
        effective_date: str = "2024-01-15",
        temperature: float | None = None,
    ) -> str:
        """Generate a policy document.

        Args:
            policy_id: Policy identifier.
            policy_title: Policy name.
            policy_type: Type (Financial, IT Security, HR, Legal, Compliance).
            complexity: simple/medium/complex.
            version: Policy version number.
            effective_date: Effective date string.
            temperature: Optional temperature override.

        Returns:
            Generated policy text in markdown format.
        """
        complexity_specs = {
            "simple": {
                "requirements": "5-10 clear, straightforward requirements",
                "pages": "2-3 pages",
                "language": "Simple, accessible language",
                "conditions": "Minimal conditions or exceptions",
            },
            "medium": {
                "requirements": "10-15 requirements with some conditions",
                "pages": "5-7 pages",
                "language": "Professional business language",
                "conditions": "Some conditional requirements and exceptions",
            },
            "complex": {
                "requirements": "20-30 requirements with nested conditions",
                "pages": "10-15 pages",
                "language": "Technical and legal language",
                "conditions": "Multiple conditions, exceptions, and cross-references",
            },
        }

        spec = complexity_specs.get(complexity, complexity_specs["medium"])

        prompt = f"""Generate a realistic {policy_type} policy document for a mid-sized technology company (500-1000 employees, $100M-500M revenue).

POLICY METADATA:
- Title: {policy_title}
- Policy ID: {policy_id}
- Version: {version}
- Effective Date: {effective_date}
- Policy Owner: {self._get_policy_owner(policy_type)}
- Approver: {self._get_approver(policy_type)}

COMPLEXITY: {complexity.upper()}
- Requirements: {spec['requirements']}
- Length: {spec['pages']}
- Language: {spec['language']}
- Conditions: {spec['conditions']}

REQUIRED SECTIONS:

1. DOCUMENT HEADER
   - Policy ID, Version, Effective Date, Review Date
   - Policy Owner, Approver, Classification
   - Document Status: Approved

2. PURPOSE (2-3 paragraphs)
   - Why this policy exists
   - What business problem it solves
   - Link to company values/strategy

3. SCOPE
   - Who this applies to (specific roles, departments)
   - What systems/processes are covered
   - Geographic scope if relevant
   - Any exclusions

4. DEFINITIONS (5-10 terms)
   - Define key terms used in policy
   - Use realistic business terminology

5. POLICY STATEMENTS ({spec['requirements']})
   Create realistic, specific requirements using:

   MANDATORY (use "must", "shall", "will", "required to"):
   - Include specific thresholds, amounts, timeframes
   - Name specific roles/departments
   - Add conditions: "when X exceeds $Y", "if Z occurs"
   - Note exceptions: "except for emergency", "unless approved by"

   RECOMMENDED (use "should", "recommended", "encouraged"):
   - Best practices
   - Optional improvements

   PROHIBITED (use "must not", "shall not", "prohibited", "forbidden"):
   - Clear prohibitions
   - Consequences stated

   {self._get_domain_specific_guidance(policy_type)}

6. PROCEDURES (2-4 detailed procedures)
   - Step-by-step processes
   - Clear numbering (1.1, 1.2, etc.)
   - Reference requirements
   - Include approval workflows where relevant

7. ROLES AND RESPONSIBILITIES
   - Create a table or list showing:
     * Role/Title
     * Specific responsibilities under this policy
     * Approval authorities

8. COMPLIANCE AND ENFORCEMENT
   - How compliance is monitored
   - Audit procedures
   - Consequences of violations (warnings, termination, legal action)
   - Reporting violations

9. EXCEPTIONS
   - Process for requesting exceptions
   - Who can approve exceptions
   - Documentation requirements

10. RELATED DOCUMENTS
    - List 3-5 related policies (make up realistic policy names)
    - Reference relevant regulations if applicable

11. APPENDICES (if complex)
    - Forms, templates, examples
    - Approval matrices
    - Thresholds tables

12. VERSION HISTORY
    Create realistic version history table:
    | Version | Date | Changes | Approved By |
    |---------|------|---------|-------------|
    | 1.0 | 2022-06-01 | Initial release | [Name] |
    | 1.1 | 2023-03-15 | Updated approval thresholds | [Name] |
    | {version} | {effective_date} | Added remote work provisions | [Name] |

QUALITY REQUIREMENTS:
- Use realistic company examples (TechCorp, Acme Solutions, etc.)
- Include specific dollar amounts, percentages, timeframes
- Make requirements testable/measurable
- Use consistent formatting and numbering
- Professional business writing style
- Include regulatory references where appropriate (SOX, GDPR, PCI-DSS, HIPAA, etc.)

FORMAT: Output as well-structured markdown with:
- Clear heading hierarchy (# ## ### ####)
- Tables where appropriate
- Numbered lists for procedures
- Bullet points for requirements
- Bold for key terms
"""

        return await self.generate_text(prompt, temperature=temperature)
