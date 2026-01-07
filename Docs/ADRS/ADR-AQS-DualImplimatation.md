Architectural design record for Project UIM-protocol

Date: 28/11/2025

Writer: Rik Heerholtz

**Context:**

The Agent Query Service (AQS) was designed to enable natural language queries against the UIM catalogue through NATS messaging. During development, it became clear that implementing the AI-powered version required external dependencies (OpenAI API key or local Ollama installation) that could block immediate development and testing. Additionally, for demonstration purposes and development environments, the full AI capability might be unnecessary overhead. Two implementation approaches were evaluated: building a single AI-powered version with fallback logic, or creating two distinct versions optimized for different use cases.

**Decision:**

Two separate implementations of the AQS were created: a keyword-based version (main_keyword.py) requiring no external dependencies, and an AI-powered version (main_ai.py) using Pydantic AI for natural language understanding.

**Rationale:**

- Immediate development capability: The keyword-based version allows development, testing, and demonstration of the complete AQS architecture without waiting for AI API access or setting up local LLM infrastructure.
- Deployment flexibility: Different deployment scenarios have different requirements. Development and CI/CD environments benefit from the lightweight keyword version, while production environments can use the AI-powered version when advanced query understanding is needed.
- Cost control: The keyword-based version eliminates ongoing API costs for OpenAI or computational overhead for local LLM inference, making it suitable for high-volume testing or environments where cost is a primary concern.
- Clear architectural separation: Having two distinct files makes the implementation choice explicit and prevents conditional logic sprawl within a single codebase. Each version can be optimized for its specific use case without compromise.
- Educational value: The dual implementation demonstrates the architectural principle that interfaces can remain consistent while internal implementations vary, supporting the research objectives of the DVerse platform project.
- Predictability: The keyword-based version provides fast, deterministic responses that are easier to test and debug, while the AI-powered version handles complex natural language queries at the cost of some unpredictability in processing time and results.

**Comparison: Keyword-Based vs AI-Powered**

| **Aspect** | **Keyword-Based (main_keyword.py)** | **AI-Powered (main_ai.py)** |
| --- | --- | --- |
| External dependencies | None (only FastStream, NATS) | Pydantic AI + OpenAI API or Ollama |
| Setup complexity | Runs immediately | Requires API key or Ollama setup |
| Response time | Fast and predictable (~100ms) | Slower, variable (1-5s depending on LLM) |
| Query handling | Simple keyword extraction and matching | Natural language understanding with context |
| Complex queries | Limited (extracts keywords only) | Excellent (understands intent and context) |
| Operating cost | Free (only infrastructure) | API costs (~\$5-10/month) or compute overhead |
| Testability | Deterministic, easy to unit test | Non-deterministic, requires integration tests |
| Best for | Development, testing, demos, cost-sensitive deployments | Production, complex agent queries, user-facing interfaces |

**Consequences:**

**Positive:**

- Development can proceed immediately without blocking on AI infrastructure setup.
- Both versions share the same architecture and message interfaces, allowing seamless switching.
- Each implementation can be optimized independently for its specific use case.
- Demonstrates separation of interface from implementation, supporting research objectives.

**Negative:**

- Maintaining two codebases requires ensuring feature parity and consistent behavior where appropriate.
- Documentation must clearly explain when to use each version to avoid confusion.
- Bug fixes or architectural changes may need to be applied to both implementations.

**Mitigation:**

- Shared components (catalogue_client.py, models.py) are extracted into common modules to prevent duplication.
- A VERSIONS.md document clearly explains the differences and use cases for each implementation.
- The same test suite (test_agent.py) works with both versions, ensuring consistent behavior.
- File naming convention (main_keyword.py vs main_ai.py) makes the choice explicit and self-documenting.

**Sources:**

1\. "Pattern: Backend for Frontend" - Sam Newman

<https://samnewman.io/patterns/architectural/bff/>

2\. Pydantic AI Documentation - Agent Architecture

<https://ai.pydantic.dev/agents/>

3\. "Strategy Pattern" - Gang of Four Design Patterns

<https://refactoring.guru/design-patterns/strategy>

4\. "Building Microservices: Designing Fine-Grained Systems" - Sam Newman

<https://www.oreilly.com/library/view/building-microservices/9781491950340/>

5\. FastStream Documentation - Message Handlers

<https://faststream.airt.ai/latest/>