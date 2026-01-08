# Backlog

Cross-session TODO tracking. Update as work progresses.

---

## High Priority

### Documentation (Current)
- [ ] Complete docs/ directory migration
- [ ] Split IMPLEMENTATION.md into focused files
- [ ] Validate all internal links after migration

### Phase 3: Modeling
- [ ] Extract 5-10 examples per domain
  - Web articles from different sources
  - Academic papers from different fields
  - Code documentation (Python, JavaScript)
  - Meeting transcripts
  - Media transcripts (YouTube, podcasts)
- [ ] Query DuckDB to find patterns in JSON structures
- [ ] Document findings in explorations/json-patterns-analysis.md

---

## Medium Priority

### Civic Domain Expansion
- [ ] RSS Spider for CivicNotice extraction (Public Notices)
- [ ] Deep PDF table extraction for Budget documents
- [ ] Meeting minutes content extraction (beyond metadata)

### UI (Structure Studio)
- [ ] Complete DataSources app workflow
- [ ] Add history grid showing past extractions
- [ ] Knowledge graph visualization improvements

### Storage Evolution
- [ ] Identify fields to normalize from JSON columns
- [ ] Create typed columns for frequently-queried fields
- [ ] Benchmark JSON vs typed column query performance

---

## Low Priority / Future

- [ ] Graph database evaluation for relationship-heavy domains
- [ ] Multi-LLM provider support (beyond Gemini)
- [ ] Media transcript extraction integration
- [ ] Chunking strategy for long documents

---

## Completed

- [x] CivicPlus Scrapy spiders with CDC
- [x] Star Schema POC implementation
- [x] Structure Studio UI foundation (React + FastAPI)
- [x] BaseGenerator + 3 domain generators
- [x] Documentation reorganization started
- [x] AGENTS.md created as entry point
