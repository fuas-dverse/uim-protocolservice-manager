Architectural design record: Chatbot Implementation


Date: 01/12/2025

Writer: Rik Heerholtz



Context:

The UIM catalogue system requires a conversational interface to lower barriers to interaction and enable agents to discover and query services through natural language. The system already uses NATS.io for inter-service communication in the multi-agent architecture, and Pydantic AI has been selected as the AI framework for the project. Two architectural approaches were considered: (1) implementing the chatbot directly in the frontend with HTTP-based API calls, or (2) creating a separate chatbot service that integrates with the existing NATS.io messaging infrastructure.

Decision:

A dedicated chatbot service will be implemented using Pydantic AI for conversational logic and NATS.io for asynchronous message-based communication, rather than embedding chatbot functionality directly in the frontend.

Rationale:


Architectural consistency: The DVerse platform uses message-based communication for agent interactions. Implementing the chatbot as a NATS subscriber/publisher aligns with the existing multi-agent architecture where agents communicate via messaging rather than HTTP.

Service separation: A dedicated chatbot service maintains clear separation of concerns, allowing the conversational interface to be developed, tested, and scaled independently from the frontend and catalogue service.

Multi-agent accessibility: By publishing to NATS topics, the chatbot becomes accessible to any agent or service on the platform, not just the web frontend. This enables programmatic agent-to-agent queries about the UIM catalogue.

Pydantic AI integration: Pydantic AI provides structured response generation and tool calling capabilities that work well with the existing Pydantic-based data models used throughout the system. It enables the chatbot to query the catalogue service and format responses appropriately.

Asynchronous processing: NATS.io's publish-subscribe pattern allows for non-blocking chatbot interactions, preventing the frontend from being tied to synchronous API calls during potentially lengthy LLM processing.

Research positioning: Framing the chatbot as a message-based service demonstrates how conversational interfaces can be integrated into multi-agent platforms and supports the research narrative about lowering barriers to UIM catalogue interaction.


Comparison: Frontend Integration vs NATS Service

Implementation approach:

The chatbot service will subscribe to a NATS topic (e.g., "uim.chatbot.query") for incoming natural language queries.

Pydantic AI will process queries and use tool calling to interact with the UIM catalogue service API for retrieving service and intent information.

Responses will be published to a reply topic or directly to the requesting agent's subscription, maintaining the asynchronous messaging pattern.

The frontend will communicate with the chatbot by publishing messages to NATS via a WebSocket bridge or frontend NATS client, rather than direct HTTP calls.

FastStream will be used to handle NATS connections and message routing, consistent with the project's technology stack.


Consequences:


Positive:

Full alignment with DVerse multi-agent architecture and messaging patterns.

Chatbot functionality available to all platform agents, not just web users.

Clear service boundaries enable independent development and testing.

Asynchronous processing prevents frontend blocking during LLM operations.

Supports research goals of demonstrating conversational UIM catalogue access.

Negative:

Adds complexity of managing another service in the architecture.

Frontend must handle NATS messaging or use a WebSocket bridge, adding implementation overhead.

Debugging message-based interactions can be more complex than HTTP requests.

Mitigation:

Use FastStream's built-in logging and testing capabilities to simplify debugging.

Implement proper error handling and timeout mechanisms for NATS message exchanges.

Document the message schema and topics clearly for future developers.

Consider implementing a simple HTTP-to-NATS bridge for frontend if WebSocket complexity becomes an issue.


Sources:


1. Pydantic AI Documentation - Tool Calling and Agents

   https://ai.pydantic.dev/


2. NATS.io Documentation - Publish-Subscribe Messaging

   https://docs.nats.io/nats-concepts/pubsub


3. FastStream Documentation - NATS Integration

   https://faststream.airt.ai/latest/nats/


4. "Microservices Communication: Request-Driven vs Event-Driven" - Martin Fowler

   https://martinfowler.com/articles/microservices.html


5. "Building Multi-Agent Systems with Message-Based Communication" - ACM Queue

   https://queue.acm.org/detail.cfm?id=3321612



| Aspect | Frontend Integration | NATS Service |
| --- | --- | --- |
| Architecture fit | Requires HTTP endpoints, breaks messaging pattern | Aligns with DVerse messaging architecture |
| Accessibility | Only available through web UI | Accessible to all platform agents and services |
| Scalability | Tied to frontend deployment | Can be scaled independently |
| Communication model | Synchronous HTTP | Asynchronous pub/sub |
| Testing & maintenance | Mixed with UI code | Isolated service with clear boundaries |
| Multi-agent support | Requires separate agent implementation | Native agent communication via NATS |

