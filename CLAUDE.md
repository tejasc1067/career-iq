# CareerIQ

CareerIQ is an AI-powered career intelligence platform.

## Goal

Help users understand their current career profile,
optimize their resume, transition into new roles,
and discover relevant jobs.

## Core capabilities

1. Career Profile
2. Resume Intelligence
3. Career Transition
4. Resume Improvement
5. Job Discovery & Matching
6. Career Roadmap

## Frontend

Next.js
TypeScript
Tailwind CSS
shadcn/ui

## Backend

Python
FastAPI
Pydantic
SQLAlchemy
Alembic

## Database

PostgreSQL
pgvector

## AI

Ollama
Local open-source LLM
Local embeddings

## Design

The project must have a premium, polished, production-quality UI.

Use the cloned awesome-design-md repository as the primary design
reference and inspiration.

Before implementing major UI components:
- Inspect the relevant design patterns in awesome-design-md.
- Follow its established visual principles where appropriate.
- Do not blindly copy designs.
- Maintain a consistent CareerIQ design system.
- Prioritize typography, spacing, hierarchy, responsiveness,
  accessibility, loading states, empty states, and error states.

## Development Rules

- Do not make large architectural changes without explaining them first.
- Prefer simple solutions over unnecessary abstractions.
- Do not introduce a dependency when the standard library or an
  existing project dependency is sufficient.
- Keep frontend and backend responsibilities clearly separated.
- Never hardcode secrets, API keys, credentials, or personal data.
- Use environment variables for configuration.
- Write tests for meaningful business logic.
- Do not silently change existing behavior.
- Preserve backward compatibility when modifying APIs.
- Keep commits focused and logically grouped.

## Comment Policy

Keep comments to a minimum.

A comment is allowed only when removing it would cause:
- the application to fail
- the build or tooling to fail
- configuration behavior to change
- a required tool/compiler/interpreter directive to stop working

Remove all other comments, including:
- explanatory comments
- obvious comments
- implementation notes
- historical comments
- TODO comments
- instructional comments
- comments describing code behavior that is already clear from the code
- comments in configuration files that only explain configuration values

Do not replace removed comments with docstrings.

Required tool directives such as `# noqa` and managed tool markers
must be preserved when removing them would change tooling behavior.

Before completing a development task, check newly created or modified
files for unnecessary comments.

## Resume Integrity

CareerIQ must never fabricate or invent:
- Skills
- Employment experience
- Job titles
- Projects
- Certifications
- Education
- Achievements
- Technologies

AI-generated suggestions must be based on information provided by
the user or clearly identified as recommendations.

Resume improvements should improve clarity, relevance, structure,
and presentation without introducing unsupported claims.

Users must review and approve AI-generated resume changes before
they are applied

## Principles

- Local-first
- Free to run
- Privacy-first
- No fabricated resume information
- AI suggestions must be reviewable
- User must approve resume changes
- Modular architecture
- Strong typing
- Automated tests