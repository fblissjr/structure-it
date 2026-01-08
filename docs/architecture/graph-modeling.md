# Graph Modeling

Graph-based storage patterns for relationship-heavy data using DuckDB.

**Status**: Design pattern documented; implementation available as reference.

## Overview

For domains with complex relationships (citations, dependencies, hierarchies), a graph model can be more natural than star schema. This uses DuckDB with nodes/edges tables.

## Use Cases

- **Academic Papers**: Citation networks, author collaborations
- **Code Documentation**: Function calls, class hierarchies, dependencies
- **Meeting Notes**: Action items to people to projects
- **Policy Documents**: Requirements to regulations to compliance

## Schema Design

### Nodes Table

```sql
CREATE TABLE graph_nodes (
    node_id VARCHAR PRIMARY KEY,
    node_type VARCHAR NOT NULL,      -- 'paper', 'author', 'topic', etc.
    label VARCHAR,                   -- human-readable label
    properties JSON,                 -- flexible properties per node type
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Edges Table

```sql
CREATE TABLE graph_edges (
    edge_id VARCHAR PRIMARY KEY,
    source_node_id VARCHAR NOT NULL,
    target_node_id VARCHAR NOT NULL,
    edge_type VARCHAR NOT NULL,      -- 'cites', 'authored_by', 'references', etc.
    properties JSON,                 -- edge metadata (strength, date, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_node_id) REFERENCES graph_nodes(node_id),
    FOREIGN KEY (target_node_id) REFERENCES graph_nodes(node_id)
);
```

### Indexes for Traversal

```sql
CREATE INDEX idx_edges_source ON graph_edges(source_node_id);
CREATE INDEX idx_edges_target ON graph_edges(target_node_id);
CREATE INDEX idx_edges_type ON graph_edges(edge_type);
CREATE INDEX idx_nodes_type ON graph_nodes(node_type);
```

### Bidirectional View

```sql
CREATE VIEW bidirectional_edges AS
SELECT edge_id, source_node_id as node_a, target_node_id as node_b, edge_type, properties
FROM graph_edges
UNION ALL
SELECT edge_id, target_node_id as node_a, source_node_id as node_b, edge_type, properties
FROM graph_edges;
```

## Implementation Pattern

```python
class GraphStorage:
    """Graph-based storage for relationship-heavy data."""

    def add_node(self, node_id: str, node_type: str, label: str, properties: dict) -> str:
        """Add or update a node."""
        self.conn.execute("""
            INSERT INTO graph_nodes (node_id, node_type, label, properties)
            VALUES (?, ?, ?, ?)
            ON CONFLICT (node_id) DO UPDATE SET
                label = EXCLUDED.label,
                properties = EXCLUDED.properties,
                updated_at = CURRENT_TIMESTAMP
        """, [node_id, node_type, label, properties])
        return node_id

    def add_edge(self, source_id: str, target_id: str, edge_type: str, properties: dict = None) -> str:
        """Add an edge between nodes."""
        edge_id = generate_entity_id(f"{source_id}:{target_id}:{edge_type}", "edge")
        self.conn.execute("""
            INSERT INTO graph_edges (edge_id, source_node_id, target_node_id, edge_type, properties)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT (edge_id) DO UPDATE SET properties = EXCLUDED.properties
        """, [edge_id, source_id, target_id, edge_type, properties or {}])
        return edge_id

    def get_neighbors(self, node_id: str, edge_type: str = None, direction: str = "both") -> list[dict]:
        """Get neighboring nodes with optional filtering."""
        # Uses bidirectional_edges view for "both" direction
        ...

    def find_path(self, start_id: str, end_id: str, max_depth: int = 5) -> list[str] | None:
        """Find shortest path between nodes using recursive CTE."""
        ...

    def get_subgraph(self, node_id: str, depth: int = 2) -> dict:
        """Get subgraph around a node up to specified depth."""
        ...
```

## Path Finding with Recursive CTE

DuckDB supports recursive CTEs for graph traversal:

```sql
WITH RECURSIVE paths AS (
    -- Base case: start node
    SELECT
        source_node_id,
        target_node_id,
        [source_node_id] as path,
        1 as depth
    FROM graph_edges
    WHERE source_node_id = ?

    UNION ALL

    -- Recursive case: extend path
    SELECT
        e.source_node_id,
        e.target_node_id,
        list_append(p.path, e.target_node_id) as path,
        p.depth + 1
    FROM graph_edges e
    JOIN paths p ON e.source_node_id = p.target_node_id
    WHERE e.target_node_id NOT IN p.path  -- avoid cycles
        AND p.depth < ?
)
SELECT path FROM paths WHERE target_node_id = ? ORDER BY depth LIMIT 1
```

## Example: Citation Network

```python
async def build_citation_network():
    """Build citation graph from academic papers."""
    graph = GraphStorage()
    papers = await duckdb.query_entities(source_type="academic_paper")

    for paper in papers:
        data = paper['structured_data']

        # Add paper node
        graph.add_node(
            node_id=paper['entity_id'],
            node_type="paper",
            label=data.get('title', 'Untitled'),
            properties={'abstract': data.get('abstract'), 'year': data.get('year')}
        )

        # Add author nodes and edges
        for author in data.get('authors', []):
            author_id = generate_entity_id(author, "author")
            graph.add_node(author_id, "author", author, {})
            graph.add_edge(author_id, paper['entity_id'], "authored")

        # Add citation edges
        for citation in data.get('citations', []):
            citation_id = generate_entity_id(citation, "paper")
            graph.add_edge(paper['entity_id'], citation_id, "cites")
```

## Trade-offs vs Star Schema

| Aspect | Graph Model | Star Schema |
|--------|-------------|-------------|
| Relationships | Natural fit | Requires joins |
| Traversal | Efficient | Requires CTEs |
| Aggregations | Slower | Optimized |
| Schema | Flexible | More structured |
| Query Complexity | Path queries easy | Analytical queries easy |

## When to Use

- Many-to-many relationships are core to the domain
- Path/traversal queries are common
- Relationship properties matter (weighted edges)
- Data is naturally network-shaped

## Related

- [Star Schema](star-schema.md) - Better for analytical queries
- [Storage Architecture](storage.md) - Overall storage design
