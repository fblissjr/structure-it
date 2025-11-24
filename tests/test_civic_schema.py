from structure_it.schemas.civic import AgendaItem, CivicMeeting, RollCall, Vote


def test_civic_meeting_schema():
    """Test that CivicMeeting schema can be instantiated."""
    meeting = CivicMeeting(
        title="Village Board Meeting",
        government_body="Village Board",
        document_type="Minutes",
        votes=[
            Vote(
                motion="Approve minutes",
                result="Passed",
                details=[
                    RollCall(official="Mayor", vote="Aye")
                ]
            )
        ],
        agenda_items=[
            AgendaItem(title="Public Comment", description="None")
        ]
    )

    data = meeting.to_dict()
    assert data["government_body"] == "Village Board"
    assert len(data["votes"]) == 1
    assert data["votes"][0]["details"][0]["official"] == "Mayor"
