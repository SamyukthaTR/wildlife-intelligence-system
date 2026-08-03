# Wildlife Population Intelligence System
## Day 1: Project Initialization, Requirement Analysis & Workflow Analysis

## 1. Project Overview

The Wildlife Population Intelligence System is an AI-powered platform that uses computer vision and bioacoustic analysis on camera trap images, drone imagery, satellite data, and audio recordings to automatically identify wildlife species, estimate population sizes, monitor biodiversity changes, and assess habitat health. The platform serves wildlife researchers, conservation officers, forest department officials, NGOs, and biodiversity monitoring teams by combining AI-driven species/acoustic recognition with population intelligence and conservation recommendation engines.

## 2. SDLC Model Selection

**Chosen Model: Agile (Scrum)**

### Justification
- The project is structured into 4 milestones over 8 weeks, each covering a distinct set of modules (setup & auth → species/biodiversity recognition → population/conservation intelligence → deployment). This maps naturally onto 2-week Agile sprints.
- Requirements across AI modules (image recognition, bioacoustics, population estimation) are expected to evolve as models are tested against real datasets, which Agile accommodates better than a rigid plan.
- Enables incremental testing and validation at the end of each milestone rather than deferring all verification to Week 8.
- Supports parallel development of frontend, backend, and ML components with regular integration checkpoints.


## 3. Functional Requirements (FR)

ID - Requirement 
FR1 - System shall allow users to register and log in with role-based access (Wildlife Researcher, Conservation Officer, Forest Department Officer, Administrator) |
FR2 - System shall support JWT-based authentication and OAuth2 login |
FR3 - System shall allow creation and management of wildlife monitoring surveys with Survey ID, GPS coordinates, habitat type, survey date, and protected area details |
FR4 - System shall allow registration and management of camera traps and audio sensors at monitoring sites |
FR5 - System shall allow upload of camera trap and drone images for automated species detection and counting |
FR6 - System shall classify detected animals by species with bounding boxes and confidence scores |
FR7 - System shall allow upload of audio recordings for bioacoustic species identification (bird calls, mammal vocalizations, amphibian/insect sounds) |
FR8 - System shall estimate population size, density, and growth rate per site/species |
FR9 - System shall compute a biodiversity index and overall ecosystem health score |
FR10 - System shall assess habitat quality and generate conservation recommendations |
FR11 - System shall generate alerts for endangered species detection, population decline, or habitat degradation |
FR12 - System shall generate exportable survey, population, biodiversity, and conservation reports in PDF and Excel formats |
FR13 - System shall provide role-specific dashboards for Researchers, Conservation Officers, Forest Department, and Admins |


## 4. Non-Functional Requirements (NFR)

ID - Requirement
NFR1 - Image species-detection inference should complete within 2–3 seconds per image |
NFR2 - System should support concurrent image/audio uploads from multiple monitoring sites |
NFR3 - All sensitive data (GPS coordinates, species records, user data) must be encrypted in transit and at rest |
NFR4 - System should be containerized using Docker for portability across AWS/Azure |
NFR5 - REST APIs should maintain an average response time under 500ms |
NFR6 - System architecture should be horizontally scalable as monitoring sites and data volume grow |
NFR7 - Platform should target 99% uptime in production |
NFR8 - UI should be responsive across desktop and tablet devices for field use |
NFR9 - System should maintain audit logs for monitoring, security, and compliance purposes |


## 5. User Stories

**Wildlife Researcher**
- As a Wildlife Researcher, I want to upload camera trap images so that species can be automatically identified without manual review.
- As a Wildlife Researcher, I want to view population and biodiversity analytics for my survey sites so that I can track ecological trends over time.

**Conservation Officer**
- As a Conservation Officer, I want to receive alerts on endangered species sightings so that I can prioritize protection actions.
- As a Conservation Officer, I want habitat restoration recommendations so that I can plan targeted conservation interventions.

**Forest Department Officer**
- As a Forest Department Officer, I want to view wildlife movement patterns on a map so that I can plan patrol routes.
- As a Forest Department Officer, I want to log and review incident reports so that I can track protected area security.

**Administrator**
- As an Administrator, I want to manage user roles and access so that data is only visible to authorized personnel.
- As an Administrator, I want platform-wide analytics and monitoring device management so that I can oversee system health.


## 6. Wildlife Monitoring Workflow Analysis

**End-to-end workflow:**

Survey Creation
      ↓
Monitoring Site Registration (GPS, habitat type, protected area)
      ↓
Camera Trap / Audio Sensor Registration
      ↓
Data Capture (images / drone imagery / audio recordings)
      ↓
AI Processing
   ├── Image Analysis Engine → Species Detection, Counting, Bounding Boxes
   └── Bioacoustic Engine → Call Detection, Species Classification
      ↓
Species Identification & Confidence Scoring
      ↓
Population Estimation & Biodiversity Analytics
      ↓
Habitat Intelligence & Conservation Recommendations
      ↓
Ecosystem Health Scoring
      ↓
Dashboards & Alerts (role-specific)
      ↓
Reports & Export (PDF / Excel)

**Key observation:** Every downstream module (population estimation, biodiversity index, conservation recommendations) depends on the initial survey and monitoring site setup being correctly structured — this is why Day 1's requirement analysis and Day 3's schema design need to align closely.