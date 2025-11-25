Architectural design record Input validation for Project UIM-protocol

Date: 19/11/2025

Writer: Rik Heerholtz

**Input Validation via Regular Expressions and Pydantic Validation**

**Context:**  
The catalogue service accepts user-provided and agent-provided inputs such as service names, URLs, metadata fields, and identifiers. To ensure system integrity, prevent malformed entries, and block potentially harmful payloads, all incoming data must be validated. Since the system already uses Pydantic for data modeling, combining native Pydantic validation with targeted regular expressions provides strong, layered protection.

**Decision:**  
Input validation is implemented using Pydantic's built-in validation features supplemented with regular expressions for fields requiring strict format constraints.

**Rationale:**

- **Strong typing with Pydantic:** Pydantic ensures that incoming data matches defined types (strings, integers, booleans, lists), preventing accidental misuse of the API.
- **Declarative constraints:** Pydantic allows field rules such as minimum/maximum length, enums, numeric ranges, and default values without additional manual checks.
- **Regex enforcement:** For fields that require specific patterns (URLs, service identifiers, protocol names), regex ensures precise structural validation.
- **Security benefits:** Regex patterns help block suspicious or malformed input, reducing risks like injection attacks, malicious filenames, or unexpected characters.
- **Developer productivity:** Having validation defined directly inside the data models keeps the logic centralized, reducing boilerplate and ensuring consistency across endpoints.

**Consequences:**

- **Positive:**
  - Ensures consistent, reliable input validation across the whole API.
  - Reduces risk of malicious or malformed data being stored in MongoDB.
  - Keeps validation logic close to the model definitions, improving maintainability.
- **Negative:**
  - Overly strict regex patterns can cause false negatives if not carefully designed.
  - Complex regexes may be harder to maintain or understand.
- **Mitigation:**
  - Use tested and documented regex patterns.
  - Keep Pydantic models modular and clearly separated.
  - Validate complex patterns with unit tests to prevent unintended blocks.

**Sources:**

- Pydantic Data Validation - Official Docs  
    <https://docs.pydantic.dev/latest/usage/validators/>
- Pydantic Field Types & Regex Support  
    <https://docs.pydantic.dev/latest/api/fields/#pydantic.fields.Field>
- "Python Regular Expressions (Regex)" - Real Python  
    <https://realpython.com/regex-python/>
- "Input Validation Best Practices" - OWASP  
    <https://owasp.org/www-community/controls/Input_Validation>