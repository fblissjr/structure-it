"""ArXiv paper generator for creating synthetic AI/ML research papers."""

from typing import Any

from structure_it.generators.base import BaseGenerator


class ArxivGenerator(BaseGenerator):
    """Generate realistic synthetic ArXiv papers for AI/ML research.

    Extends BaseGenerator with ArXiv-specific generation logic
    and formatting for academic papers.
    """

    def _get_arxiv_category(self, focus_area: str) -> str:
        """Get appropriate ArXiv category for focus area."""
        categories = {
            "machine_learning": "cs.LG",
            "computer_vision": "cs.CV",
            "natural_language": "cs.CL",
            "robotics": "cs.RO",
            "artificial_intelligence": "cs.AI",
            "neural_networks": "cs.NE",
        }
        return categories.get(focus_area, "cs.LG")

    async def generate_paper(
        self,
        paper_id: str,
        title: str,
        focus_area: str,
        complexity: str = "medium",
        temperature: float | None = None,
    ) -> str:
        """Generate an ArXiv paper.

        Args:
            paper_id: ArXiv paper identifier (e.g., "2401.12345").
            title: Paper title.
            focus_area: AI/ML focus area (machine_learning, computer_vision, etc.).
            complexity: simple/medium/complex (affects paper length and depth).
            temperature: Optional temperature override.

        Returns:
            Generated paper text in markdown format.
        """
        complexity_specs = {
            "simple": {
                "pages": "5-7 pages",
                "sections": "3-4 main sections",
                "experiments": "1-2 experiments",
                "citations": "10-15 references",
            },
            "medium": {
                "pages": "8-12 pages",
                "sections": "5-6 main sections",
                "experiments": "3-4 experiments",
                "citations": "20-30 references",
            },
            "complex": {
                "pages": "12-20 pages",
                "sections": "7-10 main sections",
                "experiments": "5+ experiments",
                "citations": "40+ references",
            },
        }

        spec = complexity_specs.get(complexity, complexity_specs["medium"])
        category = self._get_arxiv_category(focus_area)

        prompt = f"""Generate a realistic ArXiv research paper in the field of {focus_area.replace('_', ' ')}.

PAPER METADATA:
- Title: {title}
- ArXiv ID: {paper_id}
- Category: {category}
- Authors: 3-5 realistic researcher names with affiliations (universities, research labs)
- Submission Date: 2024-01-15

COMPLEXITY: {complexity.upper()}
- Length: {spec['pages']}
- Structure: {spec['sections']}
- Experiments: {spec['experiments']}
- References: {spec['citations']}

REQUIRED SECTIONS:

1. ABSTRACT (150-250 words)
   - Concise summary of the problem, approach, and key results
   - Clear contribution statement
   - Quantitative results mentioned

2. INTRODUCTION
   - Problem statement and motivation
   - Research gap in current literature
   - Main contributions (numbered list)
   - Paper organization

3. RELATED WORK
   - Survey of relevant prior work
   - Group by themes/approaches
   - Highlight differences from proposed method
   - Include realistic citations like [1], [2], etc.

4. METHODOLOGY/APPROACH
   - Detailed technical description
   - Mathematical formulations where appropriate
   - Architecture diagrams (described in text)
   - Algorithm pseudocode if relevant
   - Clear explanation of novelty

5. EXPERIMENTS
   - Dataset descriptions (use realistic datasets like ImageNet, COCO, etc.)
   - Experimental setup and implementation details
   - Baseline comparisons
   - Ablation studies
   - Quantitative results in tables

6. RESULTS AND DISCUSSION
   - Performance metrics (accuracy, F1, BLEU, etc.)
   - Comparison with state-of-the-art
   - Analysis of what works and why
   - Limitations discussion

7. CONCLUSION
   - Summary of contributions
   - Impact and implications
   - Future work directions

8. REFERENCES
   Create {spec['citations']} realistic academic references:
   - Mix of recent papers (2020-2024) and foundational work
   - Use format: [1] Author et al. "Title." Conference/Journal Year.
   - Include ArXiv papers, top-tier conferences (NeurIPS, ICML, CVPR, ACL, etc.)

QUALITY REQUIREMENTS:
- Use proper academic writing style
- Include specific technical details and metrics
- Make results quantitative (e.g., "achieved 95.3% accuracy")
- Use realistic dataset names and benchmarks
- Include proper mathematical notation in text (e.g., "loss function L(θ)")
- Make contributions clear and concrete
- Ensure technical coherence and plausibility

FOCUS AREA SPECIFICS ({focus_area}):
{self._get_focus_area_guidance(focus_area)}

FORMAT: Output as well-structured markdown with:
- Clear heading hierarchy (# ## ### ####)
- Italics for emphasis and variable names
- Bold for key terms and contributions
- Bullet points and numbered lists
- Tables for experimental results
- Proper academic citations [1], [2], etc.
"""

        return await self.generate_text(prompt, temperature=temperature)

    def _get_focus_area_guidance(self, focus_area: str) -> str:
        """Get focus area-specific guidance."""
        guidance = {
            "machine_learning": """
   - Discuss model architecture, training procedures, optimization
   - Include metrics: accuracy, precision, recall, F1, AUC
   - Reference common datasets: MNIST, CIFAR, ImageNet
   - Mention frameworks: PyTorch, TensorFlow
   - Cover topics: neural networks, deep learning, optimization
""",
            "computer_vision": """
   - Discuss image processing, object detection, segmentation
   - Include metrics: mAP, IoU, pixel accuracy
   - Reference datasets: COCO, Pascal VOC, ImageNet, ADE20K
   - Mention architectures: CNNs, Vision Transformers, ResNet, YOLO
   - Cover topics: image classification, detection, segmentation, tracking
""",
            "natural_language": """
   - Discuss language models, transformers, attention mechanisms
   - Include metrics: BLEU, ROUGE, perplexity, accuracy
   - Reference datasets: GLUE, SQuAD, WMT, CommonCrawl
   - Mention models: BERT, GPT, T5, LLaMA
   - Cover topics: NLP, text generation, translation, question answering
""",
            "robotics": """
   - Discuss control systems, perception, planning
   - Include metrics: success rate, trajectory error, collision rate
   - Reference environments: MuJoCo, Isaac, real robot platforms
   - Mention approaches: reinforcement learning, inverse kinematics, SLAM
   - Cover topics: manipulation, navigation, grasping, learning from demonstration
""",
            "artificial_intelligence": """
   - Discuss reasoning, planning, decision making
   - Include metrics: task success rate, efficiency, generalization
   - Reference benchmarks: ARC, BabyAI, diverse AI challenges
   - Mention approaches: reinforcement learning, search, knowledge representation
   - Cover topics: agents, problem solving, game playing, reasoning
""",
            "neural_networks": """
   - Discuss network architectures, training dynamics, representations
   - Include metrics: loss curves, convergence speed, parameter efficiency
   - Reference theoretical frameworks and empirical studies
   - Mention architectures: MLPs, CNNs, RNNs, Transformers, GNNs
   - Cover topics: architecture search, pruning, quantization, interpretability
""",
        }
        return guidance.get(focus_area, "")
