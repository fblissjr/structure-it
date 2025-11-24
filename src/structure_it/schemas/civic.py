"""Schema for civic/government document extraction."""

from datetime import datetime
from typing import Literal

from structure_it.schemas.base import BaseSchema
from structure_it.schemas.meetings import MeetingNote


class RollCall(BaseSchema):
    """Roll call vote record."""
    official: str
    vote: str  # "Aye", "Nay", "Abstain", "Absent"

class Vote(BaseSchema):
    """Vote on a motion."""
    motion: str
    moved_by: str | None = None
    seconded_by: str | None = None
    result: str  # "Passed", "Failed"
    ayes: list[str] = []
    nays: list[str] = []
    abstentions: list[str] = []
    details: list[RollCall] = []

class AgendaItem(BaseSchema):
    """Item on a meeting agenda."""
    number: str | None = None
    title: str
    description: str | None = None
    presenters: list[str] = []
    action_requested: str | None = None  # "Approval", "Discussion", "Information"
    outcome: str | None = None # For minutes

class CivicMeeting(MeetingNote):
    """Structured data from a civic meeting (Agenda or Minutes)."""

    government_body: str # e.g., "Village Board", "Plan Commission"
    meeting_type: str | None = None # "Regular", "Special", "Committee of the Whole"

    # Enhanced agenda/minutes structure
    agenda_items: list[AgendaItem] = []

    # Voting record (specific to civic meetings)
    votes: list[Vote] = []

    # Public participation
    public_comments: list[str] = []

    document_type: Literal["Agenda", "Minutes", "Packet", "AgendaPacket", "Audio", "Video", "Captions", "Other"]
    source_url: str | None = None
    
    # Extended fields for full artifact set
    documents: list[str] = []
    media_urls: list[str] = []


class BuildingPermit(BaseSchema):
    """Structured data from a building permit."""
    permit_number: str
    issue_date: str | None = None
    address: str
    applicant: str | None = None
    contractor: str | None = None
    description: str
    valuation: float | None = None
    fees_charged: float | None = None
    status: str | None = None  # e.g., "Issued", "Finaled", "Under Review"
    source_url: str | None = None


class CivicBid(BaseSchema):
    """Structured data from a bid or RFP."""
    bid_id: str
    title: str
    status: str  # Open, Closed, Awarded
    publication_date: datetime | None = None
    due_date: datetime | None = None
    department: str | None = None
    scope_of_work: str | None = None  # Extracted from Description HTML
    documents: list[str] = []  # S3/Local Paths to PDFs
    source_url: str | None = None


class CivicServiceRequest(BaseSchema):
    """Structured data from a service request (311)."""
    request_id: str
    category: str  # e.g. "Pothole"
    status: str
    location: str | None = None
    description: str | None = None
    submit_date: datetime | None = None
    source_url: str | None = None


class CivicFinancialReport(BaseSchema):
    """Structured data from a financial report."""
    year: int | None = None
    report_type: str  # e.g. "Budget", "CAFR", "Treasurer's Report"
    period_ending: datetime | None = None
    summary: str | None = None
    source_url: str | None = None


class CivicNotice(BaseSchema):
    """Structured data from a public notice (RSS)."""
    title: str
    link: str
    description: str | None = None
    publication_date: datetime | None = None
    guid: str
