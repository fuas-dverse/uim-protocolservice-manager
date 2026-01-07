Architectural design record for Project UIM-protocol

Date: 04/12/2025

Writer: Rik Heerholtz

**Context:**

The DVerse platform initially consisted of two separate services: the Backend API (providing REST endpoints for services, intents, and UIM protocol) and the Agent Query Service (AQS, handling natural language queries via NATS messaging). This separation was established during early development when the requirements for agent communication patterns were still being explored. However, after reviewing the architecture with project leadership, it became clear that the AQS functionality was conceptually part of the catalogue API's responsibilities rather than a separate service concern. The AQS was making HTTP calls back to the Backend API to retrieve catalogue data, creating an unnecessary network hop and architectural complexity.

**Decision:**

The Agent Query Service was merged into the Backend API as a new query endpoint, creating a unified catalogue service that provides both traditional REST endpoints and natural language query capabilities through a single codebase and deployment unit.

**Rationale:**

- Organizational directive: Project leadership identified that the query functionality belongs within the catalogue API's scope of responsibilities, not as a separate microservice. The AQS was originally conceived as another function of the API.
- Eliminated circular dependency: The AQS was making HTTP calls to the Backend API to retrieve catalogue data. Merging the services allows direct access to the business logic and data access layers without network overhead.
- Simplified deployment: A single service reduces operational complexity, requiring only one Docker container, one health check endpoint, and one set of environment variables to manage.
- Consistent architecture: Both REST endpoints and NATS message handlers now follow the same three-layer pattern (Controller → Logic → DAL), maintaining architectural consistency across the codebase.
- Shared logic layer: The keyword and AI query processing logic can be accessed by both HTTP endpoints and NATS handlers, eliminating code duplication and ensuring consistent behavior regardless of access method.
- Reduced latency: Direct function calls replace HTTP requests when handling queries, reducing response time by eliminating network serialization and deserialization overhead.

**Comparison: Separate Services vs Unified Service**

| **Aspect** | **Separate Services** | **Unified Service** |
| --- | --- | --- |
| Deployment complexity | Two services to deploy, monitor, and scale | Single service deployment |
| Data access | AQS calls Backend API via HTTP | Direct access to logic and DAL layers |
| Query latency | Network overhead for internal calls | Direct function calls (faster) |
| Code organization | Two separate codebases to maintain | Single codebase with consistent patterns |
| Architectural pattern | Different patterns (FastAPI + FastStream) | Consistent three-layer architecture |
| Testing complexity | Integration tests span two services | Tests contained within single service |
| Scaling strategy | Can scale independently (flexibility) | Scale as single unit (simpler) |
| Resource usage | Two Python runtimes, two NATS connections | Single runtime, shared connections |
| Organizational alignment | Unclear service boundaries | Clear: query is part of catalogue API |

**Consequences:**

**Positive:**

- Operational simplicity with single service deployment, monitoring, and scaling.
- Improved performance through direct function calls instead of HTTP requests.
- Architectural consistency with the three-layer pattern applied uniformly.
- Shared business logic between HTTP and NATS interfaces reduces duplication.
- Aligns with organizational understanding of service boundaries and responsibilities.

**Negative:**

- Loss of independent scaling capability for query functionality versus REST endpoints.
- Increased complexity of the unified service with both FastAPI and NATS handling.
- Query processing failures could potentially impact REST API availability if not properly isolated.

**Mitigation:**

- NATS integration is implemented as an optional component that can be disabled without affecting REST endpoints.
- Query logic layer is isolated with clear interfaces, allowing future extraction if scaling demands require it.
- Proper error handling and logging ensure query processing issues don't cascade to other endpoints.
- Both keyword-based and AI-powered query implementations are preserved, providing fallback options.

**Sources:**

1\. "Monolith First" - Martin Fowler

<https://martinfowler.com/bliki/MonolithFirst.html>

2\. "Building Microservices" - Sam Newman (O'Reilly)

<https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/>

3\. FastAPI Documentation - Background Tasks and Dependencies

<https://fastapi.tiangolo.com/tutorial/background-tasks/>

4\. "The Distributed Monolith Anti-Pattern" - Microservices.io

<https://microservices.io/patterns/monolithic-architecture.html>

5\. FastStream Documentation - Integration with FastAPI

<https://faststream.airt.ai/latest/getting-started/integrations/fastapi/>