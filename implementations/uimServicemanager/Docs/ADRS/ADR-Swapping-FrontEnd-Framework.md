Architectural design record Swapping to Solid for the FEI

Date: 25/11/2025

Writer: Rik Heerholtz

**Context:**  
The project originally selected ReactJS as the primary framework for building the front-end interface. However, during setup, the React installation process encountered persistent technical issues on the development machine, blocking further progress. However Installing SolidJS succeeded without errors, offering a practical alternative. Since both frameworks serve similar purposes but differ in performance, structure, and tooling, their suitability for the project was evaluated before making a final decision.

**Decision:**  
The front-end framework was switched from ReactJS to SolidJS due to the React installation errors and SolidJS's compatibility with the project's requirements.

**Rationale:**

- **Installation success and reliability:** React's setup repeatedly failed on the development machine, consuming time and blocking progress. SolidJS installed cleanly without errors, enabling immediate development.
- **Performance benefits:** SolidJS offers fine-grained reactivity and avoids virtual DOM diffing, resulting in faster UI updates and lower runtime overhead-useful if the frontend becomes data-heavy.
- **Developer experience:** SolidJS uses JSX and a component-based structure similar to React, reducing friction when switching. Its learning curve is manageable while still offering modern reactivity patterns.
- **Lightweight and efficient:** SolidJS bundles are significantly smaller, improving load times and making it suitable for dashboards or agent UIs.
- **API compatibility:** SolidJS integrates well with REST APIs and TypeScript, supporting the existing FastAPI backend.

**Comparison: ReactJS vs SolidJS**

| **Aspect** | **ReactJS** | **SolidJS** |
| --- | --- | --- |
| **Rendering model** | Virtual DOM with reconciliation | Fine-grained reactivity (no virtual DOM) |
| **Performance** | Good, but diffing adds overhead | Faster updates, minimal runtime overhead |
| **Bundle size** | Larger (~40-45 KB+) | Much smaller (~6-8 KB) |
| **Learning curve** | Wide community, lots of resources | Similar syntax but new reactivity model |
| **Ecosystem** | Huge, long-established | Smaller but rapidly growing |
| **Tooling** | Mature (React Router, Next.js, CRA/Vite templates) | Vite templates, Solid Router, ecosystem still maturing |
| **Installation reliability** | Failed repeatedly in this environment | Installed cleanly with no issues |
| **Best for** | Large apps, broad ecosystem needs | Fast, lightweight interfaces, performance-sensitive UIs |

**Consequences:**

- **Positive:**
  - Development can continue immediately thanks to SolidJS installing successfully.
  - Better runtime performance and smaller bundles improve user experience.
  - Reusing JSX and component patterns reduces switching cost.
- **Negative:**
  - Smaller ecosystem compared to React may require more manual solutions.
  - Some React-only libraries may not be available or fully compatible.
- **Mitigation:**
  - Leverage SolidJS community packages and Vite-based tooling.
  - Keep UI modular to allow migration back to React or another framework if required in the future.

**Sources:**

- SolidJS Official Documentation  
    <https://www.solidjs.com/docs>
- "SolidJS vs React - A Detailed Comparison" - LogRocket  
    <https://blog.logrocket.com/solidjs-vs-react-comparison/>
- "Why SolidJS is Faster Than React" - SolidJS Blog  
    <https://www.solidjs.com/blog>
- "Understanding React's Virtual DOM" - React Docs  
    <https://react.dev/reference/react-dom>