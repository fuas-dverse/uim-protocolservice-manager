---
title: Architectural design record for Project UIM-protocol
---

Date: 09/10/2025

Writer: Rik Heerholtz

**Context:**\
The project requires a modern, lightweight framework to build a RESTful
API for managing and exposing data from the databank. The framework must
support asynchronous operations, type validation, and easy integration
with Pydantic models and external services. Performance,
maintainability, and developer productivity are also important
considerations.

**Decision:**\
FastAPI was chosen as the main web framework for implementing the API
layer.

**Rationale:**

-   **Type-driven development:** Built-in support for Python type hints
    enables automatic data validation, serialization, and documentation
    generation through Pydantic and OpenAPI.

-   **High performance:** Based on Starlette and Uvicorn, FastAPI
    provides asynchronous request handling and near Node.js-level
    performance.

-   **Developer experience:** The framework offers clear syntax,
    automatic interactive docs (Swagger UI and ReDoc), and rapid
    development cycles.

-   **Compatibility:** FastAPI integrates seamlessly with MongoDB
    clients, async libraries, and modern Python tooling.

-   **Scalability:** The async design allows efficient handling of
    concurrent requests, suitable for the project's discovery and
    querying functionality.

**Consequences:**

-   **Positive:** Strong typing and validation reduce errors, built-in
    docs simplify API testing, and async support enhances performance.

-   **Negative:** Slight learning curve for async programming; less
    mature ecosystem compared to older frameworks like Flask or Django.

-   **Mitigation:** Follow established async patterns and rely on the
    active FastAPI community for support and best practices.

**Sources:\
<https://fastapi.tiangolo.com>**

[**https://fastapi.tiangolo.com/async**](https://fastapi.tiangolo.com/async)

[**https://www.geeksforgeeks.org/python/fastapi-introduction**](https://www.geeksforgeeks.org/python/fastapi-introduction)

[**https://dev.to/shariqahmed525/fastapi-advantages-and-disadvantages-197o**](https://dev.to/shariqahmed525/fastapi-advantages-and-disadvantages-197o)

[**https://dorian599.medium.com/fastapi-exploring-the-framework-and-its-benefits-aff924e87e07**](https://dorian599.medium.com/fastapi-exploring-the-framework-and-its-benefits-aff924e87e07)
