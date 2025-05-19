# System Architecture Overview

## Architectural Style
**Layered Architecture**

## Layers
- **Presentation Layer**: HTML/CSS frontend that presents the interface to users.
- **Application Layer**: Node.js backend that handles business logic, APIs, and data processing.
- **Data Layer**: PostgreSQL for persistent storage of structured data like user info, careers, institutions, and glossary terms.


## Alternative Options Considered

- **Monolithic Architecture**  
  - **Pros**: Simple to deploy; fast initial development.  
  - **Cons**: Difficult to scale; tightly coupled logic.

- **Microservices Architecture**  
  - **Pros**: Highly scalable, easier to isolate services.  
  - **Cons**: Too complex for a small team and MVP.


## Trade-offs

- We chose **Layered Architecture** because it provides a good balance of **simplicity**, **separation of concerns**, and **scalability**.
- The codebase remains modular and easy to test.
- While it doesn't scale as flexibly as microservices, the trade-off is acceptable for the MVP and academic project scope.


## Potential Architectural Issues

- **Tight coupling** between the application and data layer if queries are not abstracted properly.
- **Performance bottlenecks** during scraping operations if handled synchronously.
- Potential **deployment issues** if hosting pipelines (e.g., Railway integrations) are not correctly configured.


## High-Level Architecture Diagram


+----------------------------+
| Presentation Layer         |
| (HTML/CSS Frontend)        |
+----------------------------+
            |
            v
+-------------------------------+
| Application Layer             |
| Node.js Backend               |
| - API Logic                   |
| - Scraping via Python         |
+-------------------------------+
              |
              v
+----------------------------+
| Data Layer                 |
| (PostgreSQL Database)      |
+----------------------------+
              |
              v
+----------------------------+
| Hosting                    |
| (Railway + GitHub)         |
+----------------------------+


## Explanation of Diagram

- **Presentation Layer**: Manages the UI.
- **Application Layer**: Contains the backend logic, including user data management, search functionality, and scraping protocols.
- **Data Layer**: Handles operations made on the data.
- **Hosting**: Railway is used for deployment and GitHub for version control and continuous integration.

