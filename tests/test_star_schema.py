import json

import pytest

from structure_it.storage.star_schema_storage import StarSchemaStorage
from structure_it.utils.hashing import generate_entity_id


@pytest.fixture
def star_storage(tmp_path):
    db_path = tmp_path / "test_star.duckdb"
    storage = StarSchemaStorage(db_path=db_path)
    yield storage
    storage.close()

@pytest.mark.asyncio
async def test_policy_shredding(star_storage):
    # GIVEN: A Policy object structure (as dict)
    policy_data = {
        "policy_id": "FIN-001",
        "policy_title": "Test Policy",
        "policy_type": "Financial",
        "requirements": [
            {
                "requirement_id": "REQ-01",
                "statement": "Employees must submit receipts.",
                "requirement_type": "mandatory",
                "source_section": "2.1"
            },
            {
                "requirement_id": "REQ-02",
                "statement": "Managers should review expenses.",
                "requirement_type": "recommended",
                "source_section": "2.2"
            }
        ]
    }

    entity_id = generate_entity_id("http://test-policy", "policy")

    # WHEN: We store it
    await star_storage.store_entity(
        entity_id=entity_id,
        source_type="policy",
        source_url="http://test-policy",
        raw_content="Raw policy text...",
        structured_data=policy_data,
        metadata={"model": "test-model"}
    )

    # THEN: 1 row in dim_documents
    docs = star_storage.conn.execute("SELECT * FROM dim_documents").fetchall()
    assert len(docs) == 1
    assert docs[0][0] == entity_id
    assert docs[0][2] == "Test Policy"

    # THEN: 2 rows in fact_items
    facts = star_storage.conn.execute("SELECT * FROM fact_items").fetchall()
    assert len(facts) == 2

    # Verify content of facts
    # item_id, doc_id, domain, item_type, content_text, embedding, properties, location_pointer

    # Check first requirement
    req1 = next(f for f in facts if "receipts" in f[4])
    assert req1[1] == entity_id # doc_id
    assert req1[2] == "Financial" # domain
    assert req1[3] == "requirement" # item_type
    assert req1[7] == "2.1" # location

    props = json.loads(req1[6])
    assert props["requirement_type"] == "mandatory"
    assert props["requirement_id"] == "REQ-01"
    assert "statement" not in props # statement should be in content_text column

@pytest.mark.asyncio
async def test_context_retrieval(star_storage):
    # Setup data
    entity_id = "doc1"
    policy_data = {
        "policy_title": "Security Policy",
        "policy_type": "IT",
        "requirements": [
            {
                "statement": "Passwords must be 12 chars.",
                "requirement_type": "mandatory"
            },
            {
                "statement": "Change password every 90 days.",
                "requirement_type": "recommended"
            }
        ]
    }

    await star_storage.store_entity(
        entity_id=entity_id,
        source_type="policy",
        source_url="http://sec-policy",
        raw_content="...",
        structured_data=policy_data
    )

    # WHEN: Retrieve with filter
    # Note: vector is ignored in current implementation
    results = await star_storage.retrieve_context(
        query_vector=[],
        filters={"requirement_type": "mandatory"}
    )

    # THEN: Should only get the mandatory one
    assert len(results) == 1
    assert "12 chars" in results[0]["content"]
    assert results[0]["properties"]["requirement_type"] == "mandatory"
    assert results[0]["source_title"] == "Security Policy"

