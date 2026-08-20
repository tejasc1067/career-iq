# CareerIQ — Product Specification

**Document Status:** Initial Product Specification
**Product:** CareerIQ
**Version:** 1.0
**Purpose:** Define the product vision, user experience, capabilities, rules, and initial scope of CareerIQ.

---

## 1. Product Overview

CareerIQ is an AI-powered career intelligence platform that helps users understand their current professional profile, improve their resume, transition into new roles or technologies, discover relevant jobs, and plan their career growth.

CareerIQ is designed around a simple principle:

> **Understand where you are. Discover where you can go.**

The user provides their resume once. CareerIQ analyzes it and creates a structured career profile that becomes the foundation for the rest of the application.

The application should feel like a premium career product rather than a generic AI chatbot or resume generator.

---

## 2. Product Goals

CareerIQ should help a user:

1. Understand what their resume communicates about their current career.
2. Identify their strengths and weaknesses.
3. Understand how well their resume aligns with a target role.
4. Improve their resume without fabricating information.
5. Transition from their current career into another role, domain, or technology.
6. Understand transferable skills between careers.
7. Identify skills they need to develop for a target role.
8. Find relevant job opportunities.
9. Understand why a particular job matches their profile.
10. Build a realistic roadmap toward a target career.

---

## 3. Target Users

CareerIQ is primarily designed for professionals and job seekers who want to understand or improve their career positioning.

**Primary user groups**

### 3.1 Active Job Seekers

Users who already work in a target field and want to improve their resume and find better opportunities.

Example:

> Java Developer → Senior Java Developer

### 3.2 Career Switchers

Users who want to move into a different role, domain, or technology.

Examples:

> Network Engineer → Software Engineer

> Java Developer → Python Developer

> DevOps Engineer → Cloud Engineer

> Software Engineer → GenAI Engineer

### 3.3 Technology Switchers

Users who want to move from one technical stack to another.

Examples:

> Java → Python

> Angular → React

> AWS → Azure

### 3.4 Early-Career Professionals

Users who have limited professional experience and need help understanding how to position projects, education, skills, and certifications.

---

## 4. User Accounts & Authentication

CareerIQ requires user authentication before users can access personalized CareerIQ functionality.

Authentication allows CareerIQ to securely associate resumes, career profiles, resume versions, job preferences, career transition analyses, and other personalized information with the correct user account.

### 4.1 Authentication Requirements

Users should be able to:

* Create an account
* Log in to their account
* Log out
* Maintain an authenticated session
* Access their personalized CareerIQ data after authentication

Authentication must use secure password handling and must never store plaintext passwords.

### 4.2 User Data Isolation

Every user's data must be isolated from other users.

User-specific data includes:

* Resumes
* Resume versions
* Career profiles
* Resume analyses
* Career transition analyses
* Job preferences
* Saved jobs
* Career roadmaps
* Other personalized CareerIQ data

A user must never be able to access another user's data by manipulating an identifier, request parameter, or API request.

All protected backend operations must determine the current user from the authenticated session rather than trusting a user ID supplied by the client.

### 4.3 Authentication Flow

#### New User

```text
CareerIQ
   ↓
Sign Up
   ↓
Create Account
   ↓
Authenticated Session
   ↓
Upload Resume
   ↓
Career Profile
   ↓
CareerIQ Dashboard
```

#### Returning User

```text
CareerIQ
   ↓
Login
   ↓
Authenticated Session
   ↓
CareerIQ Dashboard
   ↓
Existing Career Profile
```

### 4.4 Authentication and Product Experience

Authentication should be integrated into the overall CareerIQ experience without becoming the primary focus of the product.

Unauthenticated users may view the CareerIQ introduction and authentication screens.

Personalized CareerIQ functionality requires authentication.

The initial authenticated experience should guide a new user toward uploading their resume and creating their Career Profile.

### 4.5 Authentication Scope

Authentication is part of the initial CareerIQ product and must be included in the initial architecture.

The initial implementation should focus on secure, straightforward account authentication.

Advanced authentication features such as social login, multi-factor authentication, passwordless authentication, and enterprise SSO are outside the initial product scope and may be considered later.

---

## 5. Core Product Concept

CareerIQ follows a profile-first model.

The user should not need to repeatedly provide their resume information for every feature.

The primary flow is:

```text
Resume Upload
      ↓
Resume Processing
      ↓
Resume Understanding
      ↓
Career Profile
      ↓
User chooses an action
      ↓
┌──────────────┬────────────────┬──────────────┬────────────────┐
│ Analyze      │ Switch         │ Find Jobs    │ Improve        │
│ Resume       │ Career         │              │ Resume         │
└──────────────┴────────────────┴──────────────┴────────────────┘
```

The Career Profile acts as the central source of structured information for the user's career.

---

## 6. Initial User Journey

### Step 1 — Upload Resume

The landing experience should immediately focus on the resume.

The user should see:

> **Upload your resume to get started**

Supported initial formats:

* PDF
* DOCX

The user should be able to:

* Drag and drop a file.
* Browse for a file.
* See the selected filename.
* Remove and replace the file before processing.

The application should clearly communicate that the resume is being analyzed locally where possible.

---

### Step 2 — Resume Processing

After upload:

```text
Resume
  ↓
Document Processing
  ↓
Text Extraction
  ↓
Section Detection
  ↓
Information Extraction
  ↓
Career Profile
```

The UI should show meaningful progress rather than a generic indefinite spinner.

For example:

```text
Reading resume
        ✓

Understanding experience
        ✓

Identifying skills
        ✓

Building your career profile
        ●
```

If processing fails, the user should receive a useful error message and an option to retry.

---

## 7. Current Career Profile

After the resume is analyzed, CareerIQ should present an inferred current profile.

The language must communicate that the profile is an AI interpretation, not an unquestionable fact.

Preferred wording:

> **Based on your resume, you appear to be a Software Engineer.**

Avoid:

> **Your role is Software Engineer.**

The profile should include:

* Current role
* Career level
* Total professional experience
* Previous roles
* Primary skills
* Secondary skills
* Technologies
* Domains
* Education
* Certifications
* Projects
* Transferable skills
* AI confidence where useful

The user should be able to correct important inferred information.

Example:

```text
Based on your resume, you appear to be:

Software Engineer

4+ years experience

[This looks right] [Edit]
```

---

## 8. CareerIQ Home / Dashboard

Once the resume has been processed, the user's main dashboard should show the career profile at the top.

Example conceptual structure:

```text
CareerIQ

Based on your resume, you appear to be

Software Engineer
4+ years experience

Java • Python • Spring Boot • AWS • Docker

--------------------------------------------

What do you want to do?

┌────────────────────┐  ┌────────────────────┐
│                    │  │                    │
│  Analyze My        │  │  Switch My         │
│  Resume            │  │  Career            │
│                    │  │                    │
└────────────────────┘  └────────────────────┘

┌────────────────────┐  ┌────────────────────┐
│                    │  │                    │
│  Find Jobs         │  │  Improve My        │
│                    │  │  Resume            │
│                    │  │                    │
└────────────────────┘  └────────────────────┘
```

These four actions are the primary product entry points.

---

## 9. Resume Intelligence

The **Analyze My Resume** workflow provides a detailed assessment of the uploaded resume.

The analysis should cover:

### 9.1 Resume Overview

* Detected role
* Experience
* Career level
* Key skills
* Main technologies
* Primary domain

### 9.2 Resume Strengths

Identify areas where the resume communicates the user's experience effectively.

Examples:

* Strong technical skill coverage
* Clear progression
* Relevant projects
* Strong measurable achievements
* Relevant certifications

### 9.3 Resume Weaknesses

Identify areas that could be improved.

Examples:

* Weak or generic summary
* Responsibilities without measurable impact
* Missing technical context
* Poorly structured project descriptions
* Repetition
* Missing relevant keywords

### 9.4 ATS Analysis

Evaluate factors such as:

* Section structure
* Keyword relevance
* Role alignment
* Readability
* Formatting concerns
* Excessive graphics or unusual structures
* Missing standard sections

CareerIQ should not claim that a resume is guaranteed to pass or fail a particular ATS.

Instead, use language such as:

> **ATS compatibility indicators**

or

> **Potential ATS issues**

### 9.5 Skill Analysis

Group skills into:

* Strongly demonstrated
* Mentioned but weakly demonstrated
* Potentially missing
* Transferable

The system must distinguish between a skill being mentioned and a skill being demonstrated through experience.

---

## 10. Target Role Analysis

CareerIQ should allow the user to specify a target role.

Examples:

```text
Java Backend Developer
Senior Software Engineer
Cloud Engineer
GenAI Engineer
DevOps Engineer
Data Engineer
```

The target role can be entered manually or selected from suggested roles.

CareerIQ should analyze the target role and compare it with the user's profile.

Conceptual flow:

```text
Current Career Profile
          +
Target Role
          ↓
Role Requirements
          ↓
Profile Comparison
          ↓
Match Analysis
```

---

## 11. Resume-to-Role Match

CareerIQ should provide an understandable match assessment.

Example:

```text
Overall Match

84%

Skills             88%
Experience         82%
Role alignment     86%
Projects           78%
Cloud              72%
```

The exact scoring algorithm is not defined by this document and should be calibrated later using actual data.

The system should not present the score as a prediction of hiring success.

It represents **profile/resume alignment with the analyzed role requirements**.

---

## 12. Career Transition

Career Transition is a core CareerIQ capability.

The user can say, through the UI:

> **I want to switch my career to...**

The user then selects or enters a target role, domain, or technology.

Examples:

```text
Current:
Network Engineer

Target:
Java Backend Developer
```

or:

```text
Current:
Java Developer

Target:
GenAI Engineer
```

---

## 13. Career Transition Analysis

CareerIQ should compare the user's current profile with the target career.

The analysis should identify:

### 13.1 Transferable Skills

Skills and experience that can carry over to the new career.

Example:

```text
Transferable

✓ AWS
✓ Docker
✓ Git
✓ Production support
✓ REST APIs
```

### 13.2 Existing Target Skills

Skills the user already possesses that are directly relevant to the target role.

### 13.3 Skill Gaps

Skills commonly required for the target role that are not sufficiently demonstrated by the user's profile.

Example:

```text
Skills to develop

• Java
• Spring Boot
• SQL
• Microservices
```

### 13.4 Experience Gaps

Identify where the user may lack practical experience rather than simply missing a keyword.

### 13.5 Career Transition Readiness

Provide an overall transition assessment.

The score should be treated as an estimate of **readiness based on available profile evidence**, not a guarantee of employment.

---

## 14. Career Transition Rules

CareerIQ must never recommend that users falsely claim skills or experience.

For example:

If a user wants to become a Java developer but has never used Java professionally, CareerIQ must not suggest:

> "Add Java to your work experience."

Instead it can recommend:

> "Consider adding a Java/Spring Boot project if you have genuinely completed one."

CareerIQ may recommend:

* Learning a technology
* Building a project
* Obtaining practical experience
* Reframing transferable experience
* Improving existing projects
* Pursuing certifications where relevant

But it must not manufacture experience.

---

## 15. Career Roadmap

After a career transition analysis, CareerIQ can generate a career roadmap.

Example:

```text
Current Profile
      ↓
Target Role
      ↓
Skill Gaps
      ↓
Learning
      ↓
Projects
      ↓
Resume Preparation
      ↓
Interview Preparation
      ↓
Job Applications
```

The roadmap can include:

### Learn

Skills and concepts to develop.

### Build

Projects that demonstrate the target skills.

### Demonstrate

Ways to show the new skills through legitimate experience or projects.

### Apply

Relevant job types to target.

### Prepare

Interview topics based on the target role.

---

## 16. Resume Improvement

The **Improve My Resume** workflow provides user-controlled AI suggestions.

The user should not need to type a prompt for common actions.

Provide predefined actions such as:

```text
Improve Summary

Improve Experience

Improve Project Descriptions

Improve Skills Section

Make ATS Friendly

Improve Keywords

Make More Concise

Improve Achievement Statements

Target a Specific Role
```

An optional free-form prompt can be provided as an advanced feature.

---

## 17. AI Resume Suggestions

CareerIQ should never silently modify a resume.

The workflow is:

```text
Current Content
      ↓
AI Analysis
      ↓
Suggested Change
      ↓
Reason
      ↓
Source / Evidence
      ↓
User Decision
      ↓
Accept / Reject / Edit
```

Each suggestion should clearly communicate:

* What is being changed
* Why it is being changed
* What information supports the suggestion
* Whether the content is extracted, rewritten, or recommended

---

## 18. Resume Change Integrity

AI-generated content must be distinguishable from user-provided content while it is still a suggestion.

Proposed content should have a clear visual indication.

Once the user accepts a suggestion, it becomes part of the user's resume and no longer needs to appear as an AI proposal.

The original resume must remain recoverable.

---

## 19. Resume Versioning

CareerIQ should maintain resume versions.

Example:

```text
Resume v1
Original

Resume v2
Java Backend optimized

Resume v3
AWS Developer optimized
```

Users should be able to:

* View versions
* Compare versions
* Restore a previous version
* Create a new version for a target role

The original uploaded resume should never be destroyed.

---

## 20. Resume Comparison

CareerIQ should provide a visual comparison between versions.

Example:

```text
Original                    Optimized

Software Engineer           Backend-focused Software Engineer

Worked on APIs              Developed REST APIs using...
```

Changes should be visually distinguishable.

The comparison should support:

* Added content
* Removed content
* Modified content

---

## 21. Job Discovery

The **Find Jobs** workflow should use the user's Career Profile rather than requiring them to manually enter all their information again.

Users should be able to specify:

* Target role
* Location
* Remote / hybrid / on-site preference
* Experience range
* Technology
* Domain
* Optional salary preference

The application should remember these preferences when appropriate.

---

## 22. Job Sources

Job data should only come from sources and access methods that permit the application to retrieve and use the data.

CareerIQ must not depend on unauthorized scraping.

The job ingestion architecture should allow multiple sources to be added later.

Job data should be normalized into a common structure.

---

## 23. Job Matching

CareerIQ should rank jobs based on alignment with the user's Career Profile.

Potential matching dimensions include:

* Skills
* Technologies
* Experience
* Role
* Domain
* Location
* Work preference
* Education where relevant

The exact weighting is an implementation decision and should be configurable.

---

## 24. Job Match Presentation

Each job should provide a clear match explanation.

Example:

```text
Senior Java Developer

92% Profile Match

Strong matches
✓ Java
✓ Spring Boot
✓ AWS
✓ REST APIs
✓ PostgreSQL

Potential gaps
△ Kafka
△ Kubernetes

Why this matches you
Your backend development experience and AWS
background align strongly with the technical
requirements of this role.
```

The match score should never be presented as:

> "You have a 92% chance of getting hired."

It is a **profile-to-job alignment score**, not a hiring probability.

---

## 25. Job Recommendation Categories

CareerIQ can categorize opportunities as:

### Strong Match

The user's profile aligns strongly with the role.

### Good Match

The user meets many requirements but has some gaps.

### Stretch Opportunity

The role requires meaningful skills or experience that the user currently lacks.

### Low Match

The role has substantial differences from the user's profile.

These categories should be based on the matching system rather than arbitrary AI wording.

---

## 26. Job Details

A job detail view should provide:

* Job title
* Company
* Location
* Work arrangement
* Experience requirements
* Key skills
* Job description
* Match score
* Matching skills
* Skill gaps
* Why it matches
* Potential concerns
* Source
* Application link

---

## 27. Career Profile as Shared Context

The Career Profile should be reusable across the product.

For example:

```text
Career Profile
      │
      ├── Resume Analysis
      │
      ├── Career Transition
      │
      ├── Resume Improvement
      │
      ├── Job Matching
      │
      └── Career Roadmap
```

The user should not have to repeatedly upload the same resume for each workflow.

---

## 28. User Corrections

AI inference can be wrong.

Users should be able to correct important profile information.

Examples:

```text
AI:
Current Role → Software Engineer

User:
[Edit] → Java Developer
```

or:

```text
AI:
Experience → 4 years

User:
[Edit] → 4 years 6 months
```

User corrections should be treated as authoritative for subsequent analysis unless the user changes them again.

---

## 29. AI Transparency

CareerIQ should clearly distinguish between:

### User-provided information

Information directly extracted from or entered by the user.

### AI interpretation

Information inferred from user-provided information.

### AI recommendation

Suggestions about what the user could learn, change, or pursue.

### External information

Information retrieved from job listings or other external sources.

This distinction should be reflected in the UI where it matters.

---

## 30. AI Safety and Accuracy Principles

CareerIQ should prioritize truthful career representation.

The AI must not:

* Invent employment history
* Invent projects
* Invent certifications
* Invent education
* Invent skills
* Invent achievements
* Invent job responsibilities
* Claim the user has experience they do not have

When information is uncertain, CareerIQ should communicate uncertainty.

For example:

> "Your resume appears to indicate..."

instead of:

> "You have..."

when the information is inferred.

---

## 31. AI Interaction Model

CareerIQ should primarily be **UI-driven**, not chatbot-driven.

Users should be able to accomplish common actions through buttons, cards, forms, selectors, and structured workflows.

Example:

```text
What do you want to do?

[ Analyze My Resume ]

[ Switch My Career ]

[ Find Jobs ]

[ Improve My Resume ]
```

AI should operate behind these workflows.

A free-form AI input may be provided as an optional advanced interaction, but the core product must remain usable without requiring users to know how to prompt an AI.

---

## 32. Loading and Processing States

AI and document processing can take time.

CareerIQ should provide meaningful progress states.

Examples:

```text
Reading your resume
Identifying experience
Analyzing skills
Building career profile
```

Avoid unexplained infinite loading indicators.

---

## 33. Error Handling

Errors should be understandable to normal users.

Avoid exposing raw stack traces or implementation details.

Examples:

Instead of:

> `PDFParserException: invalid xref table`

Use:

> **We couldn't read this PDF.**

> Try uploading another PDF or a DOCX version of your resume.

Provide a clear recovery action.

---

## 34. Privacy

Career information is sensitive.

CareerIQ should follow a privacy-first approach.

The initial product should prioritize local processing wherever practical.

The application should not send resume contents to external AI providers without the user's explicit understanding and consent.

Secrets and credentials must never be stored in source code.

---

## 35. Free / Local-First Requirement

The initial version should be runnable without paid AI APIs.

Preferred AI architecture:

```text
CareerIQ
   ↓
Local AI Provider
   ↓
Ollama
   ↓
Local Open-Source Model
```

The AI provider should be abstracted so additional providers can be supported later.

Potential future providers may include commercial APIs, but they must not be required for the initial product.

---

## 36. Initial Scope

The first complete product should focus on:

### Must Have

* Resume upload
* PDF/DOCX parsing
* Career Profile generation
* Resume analysis
* Target role selection
* Career transition analysis
* Resume improvement suggestions
* Accept/reject changes
* Resume versioning
* Basic job discovery
* Job matching
* Career roadmap

---

## 37. Post-MVP Features

The following features should not be implemented until the core product is stable:

### Interview Preparation

Generate interview topics and questions based on a selected target role.

### Mock Interview

Interactive AI interview simulation.

### Cover Letter Generation

Generate role-specific cover letters based on the verified profile.

### Application Tracker

Track jobs applied to and application status.

### GitHub Profile Analysis

Analyze public GitHub activity and projects as additional career evidence.

### LinkedIn Profile Analysis

Potential future capability depending on permitted access methods.

### Salary Intelligence

Estimate market salary ranges based on available external data.

### Skill Demand Trends

Show technology and role demand trends.

These are future capabilities and should not expand the initial implementation scope.

---

## 38. Non-Goals

CareerIQ is not intended to:

* Guarantee employment
* Guarantee ATS success
* Guarantee interview selection
* Guarantee salary outcomes
* Automatically apply to jobs without explicit user action
* Fabricate resume information
* Replace professional career counseling
* Replace human judgment

---

## 39. Success Criteria

The initial product should allow a new user to complete this journey:

```text
Upload Resume
      ↓
Understand Current Profile
      ↓
Review Career Analysis
      ↓
Choose Target Role
      ↓
Understand Career Gap
      ↓
Improve Resume
      ↓
Review and Accept Changes
      ↓
Find Relevant Jobs
      ↓
Understand Job Matches
      ↓
Receive a Career Roadmap
```

The user should leave the application with a clearer understanding of:

1. **Where they currently stand**
2. **What they are good at**
3. **What they are missing**
4. **What they can realistically transition into**
5. **How they should improve their resume**
6. **Which jobs are relevant**
7. **What they should do next**

---

## 40. Product Principles

CareerIQ should consistently follow these principles:

### Truth over optimization

Never improve a resume by making it less truthful.

### User control over automation

AI proposes; the user decides.

### Evidence over assumptions

Recommendations should be grounded in the user's profile or clearly identified external information.

### Explainability over black-box scores

Whenever possible, explain why a score or recommendation was produced.

### Profile once, reuse everywhere

The Career Profile should power multiple workflows.

### UI first, AI second

Users interact with CareerIQ through clear product workflows. AI is the intelligence behind those workflows, not the interface itself.

### Privacy first

Career data should be handled with care and local processing should be preferred.

### Progressive complexity

The application should be simple for a first-time user while providing deeper functionality for users who need it.

---

## 41. Initial Product Navigation

The exact visual design is defined separately in `DESIGN.md`.

Conceptually, the application should provide access to:

```text
CareerIQ
│
├── Home
├── My Profile
├── Analyze Resume
├── Switch Career
├── Improve Resume
├── Find Jobs
└── Career Roadmap
```

Additional navigation items can be introduced as features mature.

---

## 42. Product Source of Truth

This document defines **what CareerIQ should do**.

It does not define:

* Specific implementation architecture
* Database schema
* API contracts
* Exact AI models
* Exact UI component implementation
* Deployment infrastructure

Those decisions belong in separate technical documentation.

The hierarchy is:

```text
CLAUDE.md
    ↓
How Claude should work

PRODUCT.md
    ↓
What CareerIQ should do

DESIGN.md
    ↓
How CareerIQ should look and behave visually

ARCHITECTURE.md
    ↓
How CareerIQ should be built
```

All future implementation decisions should remain consistent with these documents unless the product requirements are explicitly revised.