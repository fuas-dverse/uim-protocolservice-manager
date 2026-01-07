Date: 09/12/2025

Writer: Rik Heerholtz

**Context:**

The DVerse platform requires a conversational agent that can discover services from the UIM catalogue and invoke them dynamically to fulfill user requests. The chatbot must understand natural language queries, translate them into service discovery requests, invoke the discovered services with appropriate parameters, and return results in a user-friendly format. Two architectural approaches were considered: (1) building the chatbot into the Backend API, or (2) creating a separate service that integrates with the existing architecture through NATS messaging and HTTP endpoints. Additionally, the choice of LLM provider (commercial API versus local model) significantly impacts cost, performance, and deployment complexity.

**Decision:**

A separate chatbot service was implemented using Pydantic AI framework with Ollama (llama3.2 model) for local LLM inference, communicating with the Backend API via HTTP to discover and invoke services dynamically.

**Rationale:**

- Service separation: A dedicated chatbot service maintains clear separation of concerns, allowing the conversational interface to be developed, tested, and scaled independently from the catalogue service. This aligns with microservices principles and supports the research objectives of the DVerse platform.
- Cost elimination: Ollama provides local LLM inference without ongoing API costs. Commercial LLM APIs (OpenAI, Anthropic) charge per token processed, which would accumulate significant costs during development, testing, and production use. Ollama eliminates this operational expense entirely.
- Data privacy: Local LLM inference ensures that user queries and service invocations never leave the DVerse infrastructure, addressing potential privacy concerns when processing sensitive research queries or organizational data.
- Model selection - llama3.2 for tool calling: After testing multiple Ollama models (qwen2.5, llama3.1, llama3.2), llama3.2 demonstrated superior tool calling capabilities. Models like qwen2.5 produced unreliable outputs including repeated garbage text, while llama3.2 consistently executed tool calls correctly and followed instructions reliably.
- Pydantic AI framework: Pydantic AI provides structured agent creation with tool calling support that integrates naturally with the existing Pydantic-based data models throughout the DVerse stack. It offers a consistent API for multiple LLM providers and simplifies agent development compared to direct LLM API integration.
- Dynamic service invocation: The chatbot uses a generic service invoker that can call any UIM-compliant service by parsing the service metadata (endpoint paths, HTTP methods, input parameters) returned from the catalogue. This enables the chatbot to invoke services that did not exist when the chatbot was developed.

**Comparison: Integrated vs Separate Chatbot**

| **Aspect** | **Integrated (in Backend API)** | **Separate Service** |
| --- | --- | --- |
| Service boundaries | Tightly coupled with catalogue logic | Clear separation, independent evolution |
| Development speed | Faster initial integration | Parallel development possible |
| Testing complexity | Tightly coupled with API tests | Isolated testing, easier mocking |
| Scaling strategy | Scales with entire API | Independent scaling based on load |
| Resource isolation | LLM processing affects API performance | LLM processing isolated from API |
| Research demonstration | Less clear architectural separation | Demonstrates multi-agent patterns clearly |

**Comparison: LLM Provider Options**

| **Aspect** | **OpenAI API** | **Ollama (qwen2.5)** | **Ollama (llama3.2)** |
| --- | --- | --- | --- |
| Cost | \$5-10/month for moderate use | Free (compute only) | Free (compute only) |
| Tool calling quality | Excellent | Poor (repeated garbage output) | Good (reliable function calls) |
| Response time | 1-3 seconds (network latency) | 3-5 seconds (unreliable) | 2-4 seconds (local processing) |
| Data privacy | Data sent to OpenAI servers | Fully local (no external calls) | Fully local (no external calls) |
| Setup complexity | API key only | Install Ollama, pull model | Install Ollama, pull model |
| Hardware requirements | None (cloud-based) | 8GB+ RAM, CPU/GPU | 4GB+ RAM, CPU sufficient |
| Model size | N/A (cloud-hosted) | 7.6GB download | 2GB download |

**Performance Optimization Options:**

- Model selection: llama3.2 provides the best balance of tool calling reliability and resource usage. Larger models (llama3.1 70B, mixtral) would improve response quality but require significantly more memory and processing time.
- GPU acceleration: Running Ollama with GPU support (CUDA for NVIDIA, ROCm for AMD) can reduce inference time from 2-4 seconds to under 1 second, but requires compatible hardware and driver installation.
- Response streaming: Implementing streaming responses would allow the UI to display partial results as they are generated, improving perceived performance even if total processing time remains unchanged.
- Caching layer: Common queries or service discovery patterns could be cached to avoid redundant LLM inference, reducing response time for repeated queries from seconds to milliseconds.
- Hybrid approach: Simple queries could bypass LLM processing entirely using keyword matching (similar to the keyword-based AQS), only invoking the LLM for complex multi-step queries requiring reasoning.
- Quantized models: Using quantized model versions (4-bit or 8-bit instead of 16-bit) reduces memory requirements and increases inference speed with minimal quality loss, particularly beneficial for deployment on resource-constrained hardware.

**Consequences:**

**Positive:**

- Zero ongoing operational costs for LLM inference.
- Complete data privacy with no external API calls.
- Independent scaling and testing of conversational interface.
- Reliable tool calling with llama3.2 model.
- Demonstrates multi-agent communication patterns clearly for research purposes.

**Negative:**

- Local LLM requires adequate hardware (minimum 4GB RAM for llama3.2).
- Response time slower than commercial APIs without GPU acceleration (2-4 seconds vs 1-2 seconds).
- Additional deployment step to install and configure Ollama.
- Model quality inferior to commercial offerings (GPT-4, Claude) for complex reasoning tasks.

**Mitigation:**

- Pydantic AI supports multiple providers through a single interface, allowing switch to OpenAI or other commercial APIs by changing configuration without code changes.
- GPU acceleration can be enabled for production deployments requiring faster response times.
- Response streaming and caching layers can be implemented to improve perceived performance.
- Hybrid approach using keyword matching for simple queries reserves LLM processing for complex requests only.

**Sources:**

1\. Pydantic AI Documentation - Agents and Tool Calling

<https://ai.pydantic.dev/>

2\. Ollama Documentation - Model Library and Tool Use

<https://ollama.com/library>

3\. "Building LLM-Powered Applications" - OpenAI Cookbook

<https://cookbook.openai.com/>

4\. "Local vs Cloud LLM Deployment Considerations" - Hugging Face

<https://huggingface.co/docs/transformers/main/en/llm_deployment>

5\. "Evaluating Tool-Calling Capabilities in Large Language Models" - arXiv

<https://arxiv.org/abs/2310.03688>