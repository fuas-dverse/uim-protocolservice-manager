# Architectural design record Database for project UIM-protocol
Date: 09/10/2025 
<br>
Writer: Rik Heerholtz

## Chosen database: MongoDB
### Context:
The system requires a flexible and scalable database to store structured and semi-structured data related to web service metadata. The data model is expected to evolve over time as the discovery service and its AI integration expand. The database must also support fast querying, JSON-like storage, and easy integration with Python.
### Decision:
MongoDB was chosen as the main database for the project.
### Rationale:
Schema flexibility: MongoDB’s document-based model allows dynamic and evolving data structures without rigid schemas.<br>
Native JSON support: Documents are stored in a JSON-like format (BSON), aligning with the data formats used by web APIs and the UIM protocol.<br>
Python compatibility: Strong driver support (via PyMongo and Motor) and good integration with Pydantic models simplify data validation and parsing.<br>
Scalability and availability: MongoDB offers built-in replication and sharding capabilities, supporting future growth without major redesigns.<br>
Developer efficiency: The query language and aggregation framework are intuitive, allowing fast iteration during prototyping.
### Consequences:
Positive: High flexibility, fast development, natural data representation for JSON-based services, easy integration with Python stack.<br>
Negative: Less strict schema enforcement can lead to inconsistent data if not managed properly; joins and complex transactions are less efficient compared to relational databases.<br>
Mitigation: Use Pydantic models for validation and controlled insert/update logic to ensure data consistency

### Sources:
https://www.mongodb.com/resources/basics/unstructured-data/schemaless
https://www.mongodb.com/resources/compare/advantages-of-mongodb
https://www.geeksforgeeks.org/mongodb/mongodb-schema-design-best-practices-and-techniques
https://www.sprinkledata.com/blogs/5-powerful-functionalities-of-mongodb


