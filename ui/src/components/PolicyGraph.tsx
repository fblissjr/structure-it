import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface Props {
  data: any;
  onBack: () => void;
}

interface Node extends d3.SimulationNodeDatum {
  id: string;
  group: 'policy' | 'requirement' | 'role' | 'root' | 'section' | 'item';
  label: string;
  radius: number;
  details?: any;
}

interface Link extends d3.SimulationLinkDatum<Node> {
  source: string | Node;
  target: string | Node;
}

export const PolicyGraph: React.FC<Props> = ({ data, onBack }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  useEffect(() => {
    if (!data || !svgRef.current) return;

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    const nodes: Node[] = [];
    const links: Link[] = [];

    // --- LOGIC SELECTION ---
    if (data.requirements && Array.isArray(data.requirements)) {
        // A. POLICY SPECIFIC LOGIC
        const roleSet = new Set<string>();
        const policyId = data.policy_id || 'POLICY';
        
        nodes.push({
          id: policyId,
          group: 'policy',
          label: data.policy_title || 'Policy Document',
          radius: 30,
          x: width / 2,
          y: height / 2,
          details: data
        });

        data.requirements.forEach((req: any) => {
          nodes.push({
            id: req.requirement_id,
            group: 'requirement',
            label: req.requirement_id,
            radius: 20,
            details: req
          });
          links.push({ source: policyId, target: req.requirement_id });

          req.applies_to?.forEach((role: string) => {
            if (!roleSet.has(role)) {
              roleSet.add(role);
              nodes.push({
                id: role,
                group: 'role',
                label: role,
                radius: 15
              });
            }
            links.push({ source: req.requirement_id, target: role });
          });
        });

    } else {
        // B. GENERIC LOGIC (Root -> Sections -> Items)
        const rootId = 'ROOT';
        nodes.push({
            id: rootId,
            group: 'root',
            label: 'Document',
            radius: 30,
            x: width / 2,
            y: height / 2,
            details: data
        });

        // Naive traversal of top-level lists
        Object.entries(data).forEach(([key, value]) => {
            if (Array.isArray(value) && value.length > 0) {
                // Create a Section Node
                const sectionId = `SEC-${key}`;
                nodes.push({
                    id: sectionId,
                    group: 'section',
                    label: key,
                    radius: 25
                });
                links.push({ source: rootId, target: sectionId });

                // Create Item Nodes (limit to first 10 to avoid explosion)
                value.slice(0, 10).forEach((item: any, idx: number) => {
                    const itemId = `${sectionId}-${idx}`;
                    let label = typeof item === 'string' ? item : (item.name || item.title || item.id || `#${idx}`);
                    if (label.length > 15) label = label.slice(0, 15) + '...';

                    nodes.push({
                        id: itemId,
                        group: 'item',
                        label: label,
                        radius: 15,
                        details: item
                    });
                    links.push({ source: sectionId, target: itemId });
                });
            }
        });
    }

    // 2. Clear Previous SVG
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // 3. Setup Simulation
    const simulation = d3.forceSimulation<Node>(nodes)
      .force('link', d3.forceLink<Node, Link>(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collide', d3.forceCollide().radius(d => (d as Node).radius + 10));

    // 4. Draw Elements
    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', 'var(--color-neon-blue)')
      .attr('stroke-opacity', 0.3)
      .attr('stroke-width', 1.5);

    const node = svg.append('g')
      .selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('r', d => d.radius)
      .attr('fill', d => {
        if (d.group === 'policy' || d.group === 'root') return '#ffffff';
        if (d.group === 'requirement' || d.group === 'section') return 'var(--color-neon-purple)'; 
        return 'var(--color-neon-green)'; 
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .style('filter', d => {
          if (d.group === 'requirement') return 'drop-shadow(0 0 5px var(--color-neon-purple))';
          if (d.group === 'role') return 'drop-shadow(0 0 5px var(--color-neon-green))';
          return 'none';
      })
      .call(d3.drag<SVGCircleElement, Node>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended));

    const labels = svg.append('g')
      .selectAll('text')
      .data(nodes)
      .enter().append('text')
      .text(d => d.label)
      .attr('font-size', '12px')
      .attr('font-family', 'Orbitron, sans-serif') // Use Orbitron font
      .attr('fill', '#cbd5e1') 
      .attr('text-anchor', 'middle')
      .attr('dy', d => d.radius + 20);

    // 5. Interaction
    node.on('click', (_event, d) => {
      setSelectedNode(d);
    });

    // 6. Update Loop
    simulation.on('tick', () => {
      link
        .attr('x1', d => (d.source as Node).x!)
        .attr('y1', d => (d.source as Node).y!)
        .attr('x2', d => (d.target as Node).x!)
        .attr('y2', d => (d.target as Node).y!);

      node
        .attr('cx', d => d.x!)
        .attr('cy', d => d.y!);

      labels
        .attr('x', d => d.x!)
        .attr('y', d => d.y!);
    });

    function dragstarted(event: any, d: Node) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: Node) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: Node) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

  }, [data]);

  return (
    <div className="relative h-[calc(100vh-64px)] bg-slate-950">
      {/* Cyber Grid Background Overlay */}
      <div className="absolute inset-0 bg-cyber-grid bg-[length:40px_40px] opacity-20 pointer-events-none" />
      
      <svg ref={svgRef} className="w-full h-full relative z-10" />
      
      {/* Overlay Controls */}
      <div className="absolute top-4 left-4 z-20">
        <button 
          onClick={onBack}
          className="px-4 py-2 bg-slate-900/80 text-neon-blue rounded-lg hover:bg-neon-blue/10 transition-colors border border-neon-blue/30 backdrop-blur font-display uppercase tracking-wider text-sm"
        >
          ← Back to Workbench
        </button>
      </div>

      {/* Node Metadata Panel */}
      {selectedNode && (
        <div className="absolute top-4 right-4 w-80 glass-panel-glow p-6 rounded-xl z-20">
          <div className="flex justify-between items-start mb-4">
            <div>
              <h3 className="text-xs font-display text-neon-blue tracking-widest uppercase mb-1">Node Type</h3>
              <p className="text-xl font-bold text-white capitalize font-display">{selectedNode.group}</p>
            </div>
            <button onClick={() => setSelectedNode(null)} className="text-slate-500 hover:text-white transition-colors">×</button>
          </div>
          
          <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar">
            <div>
              <h4 className="text-xs font-bold text-slate-500 uppercase mb-1 font-mono">ID / Label</h4>
              <p className="text-neon-blue font-mono text-sm break-all">{selectedNode.label}</p>
            </div>
            
            {selectedNode.details && (
                <div>
                    <h4 className="text-xs font-bold text-slate-500 uppercase mb-1 font-mono">Details</h4>
                    <pre className="text-[10px] bg-slate-950/80 p-3 rounded border border-white/5 text-neon-green overflow-x-auto font-mono">
                        {JSON.stringify(selectedNode.details, null, 2)}
                    </pre>
                </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};