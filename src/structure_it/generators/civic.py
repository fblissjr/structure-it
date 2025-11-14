"""Civic document generator for local government meeting materials."""

from typing import Any

from structure_it.generators.base import BaseGenerator


class CivicDocumentGenerator(BaseGenerator):
    """Generate realistic civic/government meeting documents.

    Extends BaseGenerator with civic-specific generation logic
    for meeting agendas, minutes, proposals, and other municipal documents.
    """

    def _get_municipality_type(self, gov_type: str) -> str:
        """Get appropriate municipality description."""
        types = {
            "township": "Township Board",
            "village": "Village Council",
            "city": "City Council",
            "county": "County Board of Supervisors",
        }
        return types.get(gov_type, "Municipal Council")

    async def generate_meeting_document(
        self,
        doc_id: str,
        doc_type: str,
        municipality: str,
        gov_type: str = "township",
        meeting_date: str = "2024-01-15",
        complexity: str = "medium",
        temperature: float | None = None,
    ) -> str:
        """Generate a civic meeting document.

        Args:
            doc_id: Document identifier (e.g., "TWP-2024-001").
            doc_type: Type of document (agenda, minutes, proposal, resolution).
            municipality: Name of municipality (e.g., "Springfield Township").
            gov_type: Type of government (township, village, city, county).
            meeting_date: Date of meeting (YYYY-MM-DD).
            complexity: simple/medium/complex (affects number of items).
            temperature: Optional temperature override.

        Returns:
            Generated document text in markdown format.
        """
        complexity_specs = {
            "simple": {
                "items": "5-8 agenda items",
                "pages": "3-5 pages",
                "detail": "Brief descriptions",
            },
            "medium": {
                "items": "10-15 agenda items",
                "pages": "6-10 pages",
                "detail": "Moderate detail with context",
            },
            "complex": {
                "items": "15-25 agenda items",
                "pages": "12-20 pages",
                "detail": "Comprehensive detail and background",
            },
        }

        spec = complexity_specs.get(complexity, complexity_specs["medium"])
        board_type = self._get_municipality_type(gov_type)

        if doc_type == "agenda":
            return await self._generate_agenda(
                doc_id, municipality, board_type, meeting_date, spec, temperature
            )
        elif doc_type == "minutes":
            return await self._generate_minutes(
                doc_id, municipality, board_type, meeting_date, spec, temperature
            )
        elif doc_type == "proposal":
            return await self._generate_proposal(
                doc_id, municipality, board_type, meeting_date, spec, temperature
            )
        elif doc_type == "resolution":
            return await self._generate_resolution(
                doc_id, municipality, board_type, meeting_date, spec, temperature
            )
        else:
            raise ValueError(f"Unsupported document type: {doc_type}")

    async def _generate_agenda(
        self,
        doc_id: str,
        municipality: str,
        board_type: str,
        meeting_date: str,
        spec: dict,
        temperature: float | None,
    ) -> str:
        """Generate a meeting agenda."""
        prompt = f"""Generate a realistic municipal meeting agenda for {municipality} {board_type}.

MEETING METADATA:
- Meeting ID: {doc_id}
- Date: {meeting_date}
- Time: 7:00 PM
- Location: {municipality} Municipal Building
- Meeting Type: Regular Meeting

COMPLEXITY:
- Agenda Items: {spec['items']}
- Length: {spec['pages']}
- Detail Level: {spec['detail']}

REQUIRED SECTIONS:

1. HEADER
   - {municipality} {board_type}
   - Meeting Date, Time, Location
   - Official seal/letterhead style

2. CALL TO ORDER
   - Time meeting called to order
   - Roll call of board members present/absent

3. PLEDGE OF ALLEGIANCE

4. APPROVAL OF AGENDA
   - Motion to approve agenda with any amendments

5. PUBLIC COMMENT PERIOD
   - Opportunity for public to address the board (5 min per person)

6. CONSENT AGENDA
   Items requiring routine approval (3-5 items):
   - Approval of previous meeting minutes
   - Financial reports and bill payments
   - Standard contracts or agreements
   - Routine permits or licenses

7. OLD BUSINESS
   Follow-up items from previous meetings (2-4 items):
   - Status updates on ongoing projects
   - Continued discussions
   - Second readings of ordinances

8. NEW BUSINESS
   Main agenda items for discussion ({spec['items']} total items including):

   ZONING & PLANNING:
   - Rezoning requests with property addresses
   - Site plan reviews for new developments
   - Variance requests

   INFRASTRUCTURE:
   - Road maintenance and repair projects
   - Water/sewer system updates
   - Park improvements

   BUDGET & FINANCE:
   - Budget amendments
   - Grant applications
   - Financial policy updates

   PUBLIC SAFETY:
   - Fire department equipment
   - Police department matters
   - Emergency services

   ADMINISTRATION:
   - Policy updates
   - Personnel matters
   - Inter-governmental agreements

9. REPORTS
   - Manager's Report
   - Department Reports (Public Works, Planning, etc.)
   - Committee Reports

10. BOARD MEMBER COMMENTS

11. ADJOURNMENT

QUALITY REQUIREMENTS:
- Use proper municipal government format
- Include specific property addresses for zoning items
- Include dollar amounts for financial items
- Use formal, professional language
- Reference specific ordinances, codes, or resolutions
- Make items realistic and plausible for a small municipality

FORMAT: Output as well-structured markdown with:
- Clear heading hierarchy
- Numbered agenda items
- Property addresses in format: "123 Main Street, Parcel #12-345-678-90"
- Dollar amounts: "$45,000"
- Time estimates for each major section
"""

        return await self.generate_text(prompt, temperature=temperature)

    async def _generate_minutes(
        self,
        doc_id: str,
        municipality: str,
        board_type: str,
        meeting_date: str,
        spec: dict,
        temperature: float | None,
    ) -> str:
        """Generate meeting minutes."""
        prompt = f"""Generate realistic meeting minutes for {municipality} {board_type}.

MEETING METADATA:
- Meeting ID: {doc_id}
- Date: {meeting_date}
- Type: Regular Meeting Minutes

Include:
- Attendance (board members, staff, public)
- Summary of discussions
- All motions made, seconded, and vote results
- Specific decisions and action items
- Public comments summarized
- Attachments referenced

Follow proper meeting minutes format with:
- Chronological order
- Objective, factual tone
- Specific vote counts (e.g., "Motion carried 5-2")
- Action items with responsible parties
- Time stamps for major sections
"""

        return await self.generate_text(prompt, temperature=temperature)

    async def _generate_proposal(
        self,
        doc_id: str,
        municipality: str,
        board_type: str,
        meeting_date: str,
        spec: dict,
        temperature: float | None,
    ) -> str:
        """Generate a project proposal."""
        prompt = f"""Generate a realistic municipal project proposal for {municipality}.

PROPOSAL METADATA:
- Proposal ID: {doc_id}
- Submission Date: {meeting_date}
- Type: Infrastructure/Development/Policy Proposal

Include:
- Executive Summary
- Problem Statement/Need
- Proposed Solution
- Budget and Funding Sources
- Timeline and Milestones
- Impact Assessment
- Community Benefit
- Risks and Mitigation
- Recommendation

Use specific numbers, costs, and timelines. Make it realistic for a small municipality.
"""

        return await self.generate_text(prompt, temperature=temperature)

    async def _generate_resolution(
        self,
        doc_id: str,
        municipality: str,
        board_type: str,
        meeting_date: str,
        spec: dict,
        temperature: float | None,
    ) -> str:
        """Generate a resolution document."""
        prompt = f"""Generate a realistic municipal resolution for {municipality} {board_type}.

RESOLUTION METADATA:
- Resolution Number: {doc_id}
- Date: {meeting_date}
- Type: Formal Resolution

Use proper resolution format:
- Title: "RESOLUTION NO. {doc_id}"
- WHEREAS clauses (background and justification)
- NOW THEREFORE BE IT RESOLVED clauses (specific actions)
- Adopted date and signatures
- Formal legal language

Make it about a realistic municipal matter (budget, zoning, policy, etc.).
"""

        return await self.generate_text(prompt, temperature=temperature)
