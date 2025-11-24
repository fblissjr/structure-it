# Structure Studio

Structure Studio is the **Operating System for your Structured Data**. It acts as a "Single Pane of Glass" UI for the `structure-it` research sandbox.

Unlike traditional dashboards, Structure Studio is designed as a **Workspace Shell** that hosts multiple specialized "Apps" that share the same underlying data engine (Search, Graph, Inspector).

## Architecture

The UI is built with **React 19**, **Vite**, **Tailwind CSS**, and **D3.js**. It follows a modular architecture where the "Shell" (`App.tsx`) manages global state (active app, search query, selected item) and "Apps" are injected into the main stage.

### The Shell

*   **Sidebar (Global Nav)**: Switches between apps (Citizen Explorer, Compliance Monitor, Data Sources).
*   **Global Search**: A "Spotlight-style" search bar that adapts its context based on the active app.
*   **Atomic Inspector**: A global slide-over panel that provides a "Under the Hood" view (Raw JSON, Vector Embeddings) for *any* selected entity across *any* app.

### The Apps

#### 1. Citizen Explorer (`src/apps/CitizenExplorer`)
*   **Focus**: Civic Data (Agendas, Minutes, Votes).
*   **Core View**: **Topic Timeline**. A vertical stream of events and discussions, grouped by time.
*   **Use Case**: "Show me the history of discussions about 'Zoning Variances' in 2024."

#### 2. Compliance Monitor (`src/apps/ComplianceMonitor`)
*   **Focus**: Governance & Policy (Requirements, Regulations).
*   **Core View**: **Extraction Workbench**. A split-screen view showing the source document alongside extracted structured data.
*   **Secondary View**: **Constellation Graph**. A D3.js force-directed graph visualizing relationships between Policies, Requirements, and Roles.
*   **Use Case**: "Extract all mandatory requirements from this PDF and visualize who they apply to."

#### 3. Data Sources (`src/apps/DataSources`)
*   **Focus**: Ingestion & Management.
*   **Core View**: **Ingest Dropzone**. A drag-and-drop interface for uploading files (PDF, MD, TXT) and selecting the target schema.

## Development

### Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

### Building

```bash
# Build for production
npm run build
```

### Project Structure

```
ui/src/
├── apps/                       # Distinct functional applications
│   ├── CitizenExplorer/       # Civic data visualization
│   ├── ComplianceMonitor/     # Policy extraction & analysis
│   └── DataSources/           # Ingestion workflow
├── components/
│   ├── Layout/                # Shell components (Sidebar)
│   ├── Shared/                # Reusable widgets (Inspector)
│   ├── DocumentIngest.tsx     # Upload component
│   ├── ExtractionWorkbench.tsx # Split-screen extraction view
│   ├── PolicyGraph.tsx        # D3.js Graph visualization
│   └── TopicTimeline.tsx      # Timeline visualization
├── App.tsx                     # Main Shell & State Management
└── main.tsx                    # Entry point
```

## Styling

The UI uses a custom **Cyberpunk / Glassmorphism** theme defined in `tailwind.config.js`.

*   **Colors**: `neon-blue`, `neon-purple`, `neon-pink`, `neon-green`.
*   **Effects**: `glass-panel` (backdrop blur), `shadow-glow` (colored glows).
*   **Fonts**: `Rajdhani` (UI), `Orbitron` (Headers), `Fira Code` (Data).