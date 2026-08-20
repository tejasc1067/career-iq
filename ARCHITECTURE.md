# CareerIQ — Architecture Specification

**Document Status:** Initial Architecture Specification
**Product:** CareerIQ
**Version:** 1.0
**Purpose:** Define the technical architecture, system boundaries, data flow, security model, and engineering principles for CareerIQ.

---

## 1. Architecture Overview

CareerIQ will initially use a **modular monolith architecture**.

The system will have:

* A Next.js frontend
* A Python/FastAPI backend
* PostgreSQL as the primary database
* pgvector for vector storage and semantic search
* Ollama for local LLM inference
* Local embedding models
* Docker for reproducible development infrastructure

The architecture should remain modular so individual capabilities can be separated into services in the future if there is a genuine need.

The initial architecture must not introduce microservices unnecessarily.

---

## 2. High-Level Architecture

```text
                         ┌─────────────────────┐
                         │      Browser        │
                         │                     │
                         │      Next.js        │
                         │   TypeScript / UI   │
                         └──────────┬──────────┘
                                    │
                              HTTPS / REST
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │       Backend       │
                         └──────────┬──────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
   ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
   │    Auth     │          │   Resume    │          │    Career   │
   │   Module    │          │   Module    │          │   Module    │
   └─────────────┘          └─────────────┘          └─────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
   ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
   │     AI      │          │     Jobs    │          │   Matching  │
   │   Module    │          │   Module    │          │   Module    │
   └──────┬──────┘          └──────┬──────┘          └─────────────┘
          │                         │
          ▼                         ▼
   ┌─────────────┐          ┌─────────────┐
   │   Ollama    │          │ Job Sources │
   │ Local LLM   │          │ / Adapters  │
   └─────────────┘          └─────────────┘

                    ┌─────────────────────┐
                    │     PostgreSQL      │
                    │      + pgvector     │
                    └─────────────────────┘
```

---

# 3. Architectural Principles

CareerIQ should follow these principles.

## 3.1 Modular by Domain

Backend functionality should be organized around business capabilities rather than technical layers alone.

Primary modules:

* Authentication
* Users
* Resumes
* Career Profiles
* Resume Analysis
* Career Transition
* Resume Improvement
* Jobs
* Job Matching
* Career Roadmap
* AI

Modules should have clear responsibilities and boundaries.

---

## 3.2 Modular Monolith First

The initial application should run as a single backend application.

Do not introduce:

* Kubernetes
* Service mesh
* Message brokers
* Multiple independently deployed backend services
* Distributed tracing infrastructure

unless a future requirement genuinely justifies them.

The architecture should make future extraction possible without requiring it now.

---

## 3.3 Deterministic Logic Before AI

CareerIQ should use conventional application logic whenever a problem can be solved reliably without an LLM.

Examples:

```text
File validation
Authentication
Authorization
Database operations
Resume versioning
User permissions
Job filtering
Score calculations
Data validation
Diff generation
```

AI should be used where interpretation, generation, semantic reasoning, or natural-language understanding provides meaningful value.

---

# 4. Frontend Architecture

The frontend will use:

* Next.js
* TypeScript
* Tailwind CSS
* shadcn/ui

The frontend is responsible for:

* User interface
* Client-side interaction
* Form handling
* Authentication state
* Resume viewing
* Progress states
* AI suggestion review
* Dashboard visualization
* API communication

The frontend must not contain business-critical AI logic.

---

# 5. Frontend Application Structure

The exact framework structure can evolve during implementation, but the application should conceptually follow:

```text
web/
├── app/
│   ├── (auth)/
│   ├── (dashboard)/
│   ├── api/
│   └── ...
│
├── components/
│   ├── ui/
│   ├── resume/
│   ├── career/
│   ├── jobs/
│   ├── analysis/
│   └── navigation/
│
├── lib/
│   ├── api/
│   ├── auth/
│   ├── utils/
│   └── ...
│
├── hooks/
│
├── types/
│
└── ...
```

The final structure should follow current Next.js conventions and should not introduce unnecessary abstractions.

---

# 6. Backend Architecture

The backend will use:

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Alembic

The backend is responsible for:

* Authentication
* Authorization
* Business logic
* Resume processing
* Career profile generation
* AI orchestration
* Job processing
* Matching
* Persistence
* Validation
* Security

---

# 7. Backend Module Structure

The backend should be organized by domain.

Conceptually:

```text
api/
└── app/
    ├── auth/
    ├── users/
    ├── resumes/
    ├── career/
    ├── analysis/
    ├── transition/
    ├── improvement/
    ├── jobs/
    ├── matching/
    ├── roadmap/
    ├── ai/
    ├── database/
    ├── common/
    └── main.py
```

Each domain module should contain only the code required for that domain.

Avoid creating a large generic `utils` module containing unrelated business logic.

---

# 8. API Architecture

The frontend and backend will communicate through REST APIs.

API endpoints should be organized by domain.

Conceptual examples:

```text
/api/auth/*
/api/users/*
/api/resumes/*
/api/career-profile/*
/api/analysis/*
/api/career-transition/*
/api/resume-improvements/*
/api/jobs/*
/api/job-matches/*
/api/roadmap/*
```

The exact endpoint naming and request/response contracts should be defined during implementation and documented separately.

---

# 9. Authentication Architecture

Authentication is part of V1.

The backend will own authentication and authorization.

The frontend must never be trusted to determine the authenticated user's identity.

Conceptual flow:

```text
Browser
   │
   │ Login
   ▼
FastAPI Auth
   │
   ├── Validate credentials
   ├── Verify password hash
   └── Create authenticated session
   │
   ▼
Browser
   │
   │ Authenticated requests
   ▼
FastAPI
   │
   ├── Validate authentication
   ├── Identify current user
   └── Authorize resource
```

---

# 10. Password Security

Passwords must never be stored in plaintext.

Passwords must be stored using a strong password hashing algorithm appropriate for modern applications.

Authentication implementation must:

* Hash passwords securely
* Never log passwords
* Never return password hashes to the frontend
* Validate credentials server-side
* Provide appropriate authentication error responses
* Protect authenticated endpoints

---

# 11. Token / Session Architecture

The initial implementation may use JWT-based authentication.

The architecture should distinguish:

* Short-lived access credentials
* Longer-lived refresh credentials where required

Tokens must not contain unnecessary personal information.

Secrets used for signing tokens must come from environment configuration.

The exact token storage strategy must prioritize protection against common browser attacks.

---

# 12. Authorization and User Isolation

Every protected resource must belong to an authenticated user.

The backend should determine the current user from the authenticated session.

Avoid trusting client-provided user identifiers for authorization.

Bad pattern:

```text
GET /api/resumes?user_id=123
```

where the server blindly trusts `user_id`.

Preferred conceptual pattern:

```text
GET /api/resumes

Authenticated user
        ↓
Backend identifies user
        ↓
Return only that user's resumes
```

Every database query involving user-owned data must enforce ownership.

---

# 13. Resume Processing Architecture

Resume processing is a multi-stage pipeline.

```text
PDF / DOCX
    ↓
File Validation
    ↓
Text Extraction
    ↓
Document Structure Detection
    ↓
Section Extraction
    ↓
Structured Resume
    ↓
Career Profile
    ↓
AI Analysis
```

Supported initial formats:

* PDF
* DOCX

---

# 14. Resume File Validation

Before processing:

* Validate file type
* Validate file size
* Validate file content where practical
* Reject unsupported formats
* Generate safe internal filenames
* Never trust user-provided filenames for filesystem paths

Uploaded files must not be executable.

---

# 15. Document Parsing

Initial technologies:

### PDF

PyMuPDF or an equivalent maintained Python PDF processing library.

### DOCX

python-docx or an equivalent maintained library.

The parser should produce normalized text and document structure.

The application should preserve enough information to associate extracted information with the original resume content where possible.

---

# 16. Structured Resume Model

Extracted resume information should be represented as structured data.

Conceptual model:

```text
Resume
├── Contact Information
├── Summary
├── Experience
│   ├── Company
│   ├── Role
│   ├── Dates
│   ├── Responsibilities
│   └── Achievements
├── Skills
├── Projects
├── Education
└── Certifications
```

The structured representation becomes the source for downstream analysis.

---

# 17. Career Profile Architecture

The Career Profile is a normalized representation of the user's career.

Conceptual structure:

```text
Career Profile
├── Current Role
├── Career Level
├── Experience
├── Skills
├── Technologies
├── Domains
├── Education
├── Certifications
├── Projects
├── Transferable Skills
└── Profile Confidence
```

The Career Profile should be reusable across:

* Resume Analysis
* Career Transition
* Resume Improvement
* Job Matching
* Career Roadmap

---

# 18. AI Architecture

AI functionality must be isolated behind an AI abstraction layer.

Conceptually:

```text
Application
     │
     ▼
AI Service / AI Interface
     │
     ▼
Provider Adapter
     │
     ▼
Ollama
     │
     ▼
Local LLM
```

The rest of the application should not directly depend on Ollama-specific implementation details.

---

# 19. AI Provider Abstraction

The AI layer should allow future providers to be added.

Conceptually:

```text
AIProvider
├── OllamaProvider
├── FutureOpenAIProvider
├── FutureBedrockProvider
└── FutureAnthropicProvider
```

Only Ollama is required for the initial implementation.

The application must work without a paid AI provider.

---

# 20. AI Responsibilities

AI should be used for tasks such as:

* Resume interpretation
* Career profile inference
* Resume quality analysis
* Role requirement interpretation
* Career transition reasoning
* Resume improvement suggestions
* Natural-language explanations
* Career roadmap recommendations

AI should not be the sole source of truth for:

* Authentication
* Authorization
* User ownership
* File validation
* Data integrity
* Resume versioning
* Permission checks

---

# 21. Structured AI Outputs

AI responses should use structured schemas whenever the result is consumed programmatically.

Examples:

```text
CareerProfile
ResumeAnalysis
SkillGap
CareerTransitionAnalysis
ResumeSuggestion
CareerRoadmap
JobMatchExplanation
```

The backend should validate AI-generated structured output before using it.

Invalid AI output should be handled gracefully.

---

# 22. AI Hallucination Controls

CareerIQ must enforce the resume integrity rules defined in PRODUCT.md.

The AI should receive only relevant user-provided context when generating resume content.

When possible, generated resume suggestions should contain evidence references to the original information supporting the suggestion.

The AI must not invent:

* Skills
* Experience
* Projects
* Certifications
* Education
* Achievements
* Employment history

---

# 23. Embeddings and Vector Search

pgvector will be used for semantic search where useful.

Potential embedded entities include:

* Resume sections
* Skills
* Job descriptions
* Role requirements
* Career knowledge
* Project descriptions

Conceptual flow:

```text
Document / Job
      ↓
Chunking
      ↓
Embedding Model
      ↓
Vector
      ↓
PostgreSQL + pgvector
```

---

# 24. RAG Architecture

RAG should be introduced where retrieval improves the quality of AI responses.

Conceptual flow:

```text
User Action
    ↓
Determine Context
    ↓
Retrieve Relevant Information
    ↓
Vector Search
    ↓
Build AI Context
    ↓
Ollama
    ↓
Structured Response
    ↓
Validation
    ↓
UI
```

CareerIQ should avoid retrieving unnecessary personal information.

Only relevant context should be supplied to the model.

---

# 25. AI Prompt Architecture

Prompts should not be scattered throughout application code.

AI tasks should have clearly defined prompt templates or prompt modules.

Conceptually:

```text
ai/
├── providers/
├── prompts/
│   ├── career_profile/
│   ├── resume_analysis/
│   ├── career_transition/
│   ├── resume_improvement/
│   └── roadmap/
├── schemas/
└── services/
```

Prompts should be version-controlled.

---

# 26. Resume Improvement Architecture

Resume improvement should be implemented as a suggestion system.

```text
Existing Resume
      ↓
AI Analysis
      ↓
Suggestion
      ↓
Evidence / Rationale
      ↓
User Review
      ↓
Accept / Reject / Edit
      ↓
Resume Version
```

The original content must remain recoverable.

---

# 27. Resume Versioning

Resume changes should create versions rather than overwrite the original.

Conceptually:

```text
Resume
├── Version 1 — Original
├── Version 2 — Java Developer
├── Version 3 — AWS Developer
└── Version 4 — GenAI Engineer
```

Each version should retain enough information to reconstruct the resume at that point in time.

---

# 28. Resume Diff Architecture

Resume comparison should operate on structured resume content where practical rather than relying only on raw document comparison.

The system should identify:

* Added content
* Removed content
* Modified content

The UI will present these differences according to DESIGN.md.

---

# 29. Career Transition Architecture

Career transition analysis should combine deterministic comparison with AI reasoning.

```text
Current Career Profile
          +
Target Role Requirements
          ↓
Deterministic Skill Comparison
          ↓
Transferable Skill Detection
          ↓
Gap Identification
          ↓
AI Reasoning
          ↓
Transition Recommendations
```

The system should distinguish between:

* Already demonstrated
* Mentioned but weakly demonstrated
* Transferable
* Missing
* Recommended to learn

---

# 30. Role Requirement Architecture

Role requirements should eventually come from multiple sources:

* Job descriptions
* Curated role definitions
* Structured skill knowledge
* User-selected target roles

Role requirements should be normalized into structured data.

Example:

```text
Role
├── Title
├── Required Skills
├── Preferred Skills
├── Experience
├── Domain
└── Related Roles
```

---

# 31. Job Ingestion Architecture

Job sources must be accessed through permitted methods.

The application should use an adapter architecture:

```text
JobSource
├── Source A Adapter
├── Source B Adapter
└── Future Source Adapters
```

Each adapter converts source-specific job data into CareerIQ's normalized job model.

---

# 32. Normalized Job Model

Conceptual structure:

```text
Job
├── Title
├── Company
├── Location
├── Work Arrangement
├── Experience Requirement
├── Skills
├── Description
├── Salary
├── Source
├── Source URL
└── Posted Date
```

Optional fields should be nullable when the source does not provide them.

---

# 33. Job Matching Architecture

Job matching should combine deterministic scoring with semantic similarity.

Conceptual flow:

```text
Career Profile
      +
Job
      ↓
Structured Feature Extraction
      ↓
Deterministic Matching
      ↓
Semantic Similarity
      ↓
Combined Score
      ↓
Match Explanation
```

The exact weighting should remain configurable.

---

# 34. Job Match Score

The match score represents **profile-to-job alignment**.

It must not be presented as:

* Probability of hiring
* Probability of interview
* Probability of offer

Potential dimensions:

```text
Skills
Experience
Role
Domain
Location
Work Preference
Education
```

The scoring model should be versioned so future changes can be evaluated.

---

# 35. Career Roadmap Architecture

Career roadmaps should be generated from the gap between:

```text
Current Career Profile
          ↓
Target Role
          ↓
Skill Gaps
```

The roadmap may contain:

```text
Learn
  ↓
Practice
  ↓
Build
  ↓
Demonstrate
  ↓
Prepare
  ↓
Apply
```

AI recommendations should be grounded in the identified skill gaps.

---

# 36. Database Architecture

PostgreSQL is the primary database.

pgvector will extend PostgreSQL for vector operations.

The database should contain conceptually:

```text
users
resumes
resume_versions
resume_sections
career_profiles
skills
experiences
projects
certifications
education
resume_analyses
career_transitions
resume_suggestions
jobs
job_matches
job_preferences
career_roadmaps
embeddings
```

The exact schema should be designed before implementation of each module.

---

# 37. Database Ownership

User-owned entities must contain an appropriate ownership relationship.

Example:

```text
users
  │
  ├── resumes
  │     └── resume_versions
  │
  ├── career_profiles
  │
  ├── job_preferences
  │
  └── career_roadmaps
```

Queries must enforce ownership.

---

# 38. Database Migrations

Alembic will manage database schema changes.

Developers must not manually modify production database schemas outside the migration process.

Each schema change should have a migration.

Migrations must be reviewable and reversible where practical.

---

# 39. API Validation

Pydantic schemas should validate:

* Request payloads
* Response payloads where appropriate
* AI outputs
* User input
* Job data
* Resume metadata

The backend must not trust client-provided data.

---

# 40. Error Handling

The backend should provide consistent API errors.

Errors should contain safe, useful information.

Internal stack traces must not be exposed to users.

Errors should be categorized where appropriate:

```text
Authentication Error
Authorization Error
Validation Error
File Processing Error
AI Processing Error
External Source Error
Database Error
Unexpected Error
```

---

# 41. Configuration

Environment-specific configuration must be stored outside source code.

Use environment variables for:

```text
Database URL
JWT configuration
Authentication secrets
Ollama configuration
Embedding model configuration
Application configuration
External job source credentials
```

Provide:

```text
.env.example
```

with safe placeholder values.

Never commit real secrets.

---

# 42. Local Development

CareerIQ should be runnable locally.

The intended development environment should use Docker where appropriate.

Conceptually:

```text
Docker Compose
│
├── PostgreSQL
│   └── pgvector
│
└── Optional supporting services
```

Ollama may run directly on the host machine when that provides better local model performance.

The frontend and backend may run directly during development for faster iteration.

---

# 43. Docker Architecture

Production-like containerization should be possible.

Conceptually:

```text
┌───────────────┐
│   Next.js     │
└───────┬───────┘
        │
┌───────▼───────┐
│   FastAPI     │
└───────┬───────┘
        │
┌───────▼──────────────┐
│ PostgreSQL + pgvector│
└──────────────────────┘
```

The initial system should not require a complex container orchestration platform.

---

# 44. Testing Architecture

Testing is required at multiple levels.

## 44.1 Backend Unit Tests

Use pytest for:

* Business logic
* Matching calculations
* Validation
* Resume transformations
* Versioning
* Authorization logic

## 44.2 API Tests

Test:

* Authentication
* Authorization
* Resume endpoints
* Career endpoints
* Job endpoints
* Error behavior

## 44.3 Frontend Tests

Test important user interactions and components.

## 44.4 AI Evaluation

AI behavior must have deterministic evaluation cases where practical.

Examples:

```text
Resume → Expected Role
Resume → Expected Skills
Resume + Target Role → Expected Gap
Resume + Job → Expected Match Characteristics
```

AI evaluation should measure quality rather than requiring exact text equality.

---

# 45. AI Evaluation Dataset

Create a controlled test dataset containing representative synthetic or appropriately licensed resume/job examples.

The dataset should test:

* Straightforward resumes
* Career switchers
* Technology switchers
* Missing information
* Ambiguous roles
* Multiple technologies
* Different experience levels

Do not commit real users' personal resumes to the repository.

---

# 46. Security Architecture

Security must be considered across the entire system.

Important requirements:

* Secure password hashing
* Authentication on protected endpoints
* Authorization checks
* User data isolation
* Input validation
* File validation
* Safe file handling
* Environment-based secrets
* No sensitive data in logs
* Secure token handling
* Rate limiting where appropriate
* Protection against prompt injection where external content is processed

---

# 47. Prompt Injection Considerations

CareerIQ may process external or user-controlled text such as:

* Resume content
* Job descriptions
* Imported job listings

These inputs must be treated as **data**, not instructions.

For example, if a job description contains text instructing the AI to ignore CareerIQ's rules, the system must treat that text as job content rather than an instruction.

AI prompts should clearly separate:

```text
System instructions
User data
External data
Task
```

---

# 48. Logging and Observability

The initial application should provide useful structured logs.

Logs should help diagnose:

* Authentication failures
* Resume processing failures
* AI failures
* Job ingestion failures
* Database errors

Do not log:

* Passwords
* Authentication secrets
* Full resume contents
* Sensitive personal information
* Access tokens

unless explicitly required for a controlled debugging process and safely redacted.

---

# 49. Privacy Architecture

CareerIQ should minimize unnecessary storage and processing of sensitive career information.

The initial architecture should prefer local AI processing.

External AI providers should be optional future adapters.

Users should be able to understand what information is stored and processed.

---

# 50. Dependency Principles

Dependencies should be introduced only when they provide meaningful value.

Prefer:

* Well-maintained libraries
* Widely adopted libraries
* Small focused dependencies
* Libraries compatible with the existing architecture

Avoid introducing large frameworks solely because they are popular.

Every significant dependency should have a clear reason for inclusion.

---

# 51. API and Domain Boundaries

Domain modules should communicate through explicit interfaces.

Avoid tightly coupling:

```text
Resume → direct Ollama calls
Job → direct database internals
Frontend → database
```

Preferred:

```text
Resume Module
      ↓
AI Service
      ↓
AI Provider
```

and:

```text
Frontend
      ↓
API
      ↓
Domain Service
      ↓
Repository
      ↓
Database
```

---

# 52. Repository Layer

Database access should be isolated from business logic where practical.

Conceptually:

```text
API
 ↓
Service
 ↓
Repository
 ↓
Database
```

Services contain business rules.

Repositories contain persistence operations.

Do not create unnecessary repository abstractions for trivial operations where they add no value.

---

# 53. Service Layer

Services should contain domain-level business logic.

Examples:

```text
ResumeService
CareerProfileService
ResumeAnalysisService
CareerTransitionService
ResumeImprovementService
JobService
JobMatchingService
CareerRoadmapService
```

Services may coordinate:

* Repositories
* AI services
* External adapters
* Validation

---

# 54. External Integrations

External systems must be isolated behind adapters.

Examples:

```text
AIProvider
JobSource
DocumentParser
```

This allows implementations to change without rewriting the rest of the application.

---

# 55. Frontend / Backend Contract

The frontend should consume documented API contracts.

The frontend should not reproduce backend business logic simply to display a result.

For example, job match scores should be calculated by the backend.

The frontend should display the result and supporting information.

---

# 56. Data Flow — Initial Resume

```text
User
 ↓
Next.js
 ↓
Upload API
 ↓
Authentication
 ↓
File Validation
 ↓
Resume Storage / Processing
 ↓
Document Parser
 ↓
Structured Resume
 ↓
Career Profile Service
 ↓
AI Analysis
 ↓
PostgreSQL
 ↓
Next.js
 ↓
Career Profile UI
```

---

# 57. Data Flow — Resume Improvement

```text
User
 ↓
Select "Improve Resume"
 ↓
Next.js
 ↓
FastAPI
 ↓
Load Career Profile + Resume Version
 ↓
Relevant Context Retrieval
 ↓
AI Service
 ↓
Ollama
 ↓
Structured Suggestions
 ↓
Validation
 ↓
Next.js
 ↓
User Review
 ↓
Accept / Reject
 ↓
Create New Resume Version
```

---

# 58. Data Flow — Career Switch

```text
User
 ↓
Select "Switch My Career"
 ↓
Choose Target Role
 ↓
FastAPI
 ↓
Load Career Profile
 ↓
Load Target Role Requirements
 ↓
Deterministic Skill Comparison
 ↓
AI Reasoning
 ↓
Career Transition Analysis
 ↓
Skill Gaps
 ↓
Recommendations
 ↓
Career Roadmap
```

---

# 59. Data Flow — Job Matching

```text
Job Sources
 ↓
Source Adapter
 ↓
Normalize Job
 ↓
Store Job
 ↓
Generate Embedding
 ↓
pgvector
        +
Career Profile
        ↓
Matching Engine
        ↓
Match Score
        ↓
Match Explanation
        ↓
Next.js
```

---

# 60. Performance Principles

The application should avoid blocking the user interface during long-running operations.

Potentially expensive operations include:

* Resume parsing
* Embedding generation
* LLM inference
* Large job ingestion
* Bulk job matching

The initial implementation may use synchronous processing where acceptable.

As actual performance requirements emerge, long-running operations can be moved to background jobs.

Do not introduce a task queue before there is a demonstrated need.

---

# 61. Scalability Strategy

The initial system should prioritize simplicity.

If usage grows, individual modules can be extracted.

Potential future extraction candidates:

```text
AI Service
Resume Processing Service
Job Ingestion Service
Job Matching Service
```

The modular boundaries should make such extraction possible.

Microservices are a future optimization, not an initial requirement.

---

# 62. Architecture Decision Records

Important architectural decisions should be documented when they have meaningful long-term impact.

Examples:

* Authentication approach
* LLM provider abstraction
* Database/vector strategy
* Job source strategy
* Resume storage strategy
* Background processing strategy

Architecture decisions should explain:

* Context
* Decision
* Alternatives considered
* Reasoning
* Consequences

---

# 63. Initial Repository Structure

The exact structure may evolve, but the target architecture is:

```text
career-iq/
│
├── CLAUDE.md
├── PRODUCT.md
├── DESIGN.md
├── ARCHITECTURE.md
├── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
│
├── apps/
│   ├── web/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   └── ...
│   │
│   └── api/
│       ├── app/
│       │   ├── auth/
│       │   ├── users/
│       │   ├── resumes/
│       │   ├── career/
│       │   ├── analysis/
│       │   ├── transition/
│       │   ├── improvement/
│       │   ├── jobs/
│       │   ├── matching/
│       │   ├── roadmap/
│       │   ├── ai/
│       │   ├── database/
│       │   └── common/
│       └── tests/
│
├── docs/
│   ├── ai/
│   ├── api/
│   ├── database/
│   └── decisions/
│
└── scripts/
```

This is a target structure, not a requirement to create every directory immediately.

---

# 64. Development Sequence

Implementation should proceed incrementally.

### Phase 1 — Project Foundation

* Repository structure
* Next.js application
* FastAPI application
* PostgreSQL
* Docker development environment
* Environment configuration
* Basic CI
* Authentication foundation

### Phase 2 — Career Profile

* User account
* Resume upload
* PDF/DOCX parsing
* Structured resume
* Career Profile

### Phase 3 — Resume Intelligence

* Resume analysis
* Target role
* Skill analysis
* ATS indicators
* Match analysis

### Phase 4 — Career Transition

* Target career
* Transferable skills
* Skill gaps
* Transition readiness
* Career roadmap

### Phase 5 — Resume Improvement

* AI suggestions
* Evidence/rationale
* Accept/reject
* Resume versions
* Resume comparison
* Export

### Phase 6 — Job Intelligence

* Job source adapters
* Job normalization
* Job search
* Matching
* Match explanations

### Phase 7 — Hardening

* Tests
* AI evaluation
* Security review
* Performance review
* Accessibility
* Error handling
* Documentation
* CI/CD improvements

---

# 65. Git Development Strategy

CareerIQ must be developed incrementally with focused commits.

Do not create one large commit containing an entire feature set.

Preferred progression:

```text
docs: establish project foundation
docs: define product specification
docs: define architecture
feat: scaffold frontend
feat: scaffold backend
feat: add authentication
feat: add database foundation
feat: implement resume upload
feat: implement resume parsing
...
```

Each commit should represent a coherent change.

Before committing:

```text
git status
git diff
tests
```

Claude Code must not commit or push changes unless explicitly instructed.

---

# 66. Code Review Strategy

Before accepting a significant Claude Code change:

1. Inspect the diff.
2. Run relevant tests.
3. Check for unnecessary dependencies.
4. Check security-sensitive changes.
5. Verify the implementation against PRODUCT.md.
6. Verify UI changes against DESIGN.md.
7. Verify architecture against ARCHITECTURE.md.
8. Commit only after review.

Claude Code should not make product decisions that contradict these documents without first explaining the conflict.

---

# 67. Architecture Source of Truth

This document defines **how CareerIQ should be built**.

The documentation hierarchy is:

```text
CLAUDE.md
    ↓
How Claude should work

PRODUCT.md
    ↓
What CareerIQ should do

DESIGN.md
    ↓
How CareerIQ should look

ARCHITECTURE.md
    ↓
How CareerIQ should be built
```

When implementation decisions conflict with these documents, the conflict should be identified and discussed rather than silently resolved.

The architecture may evolve as implementation reveals new requirements, but changes should be intentional, documented, and reflected in the appropriate source-of-truth document.