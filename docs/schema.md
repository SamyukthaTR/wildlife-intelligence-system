# Database Schema

This document outlines the core tables created for the Wildlife Population Intelligence System (Stage 2). 
The database uses PostgreSQL with the PostGIS extension for spatial data handling.

## Tables

### 1. `users`
Stores all system users and their authentication details.
- `id`: Primary key (Integer)
- `name`: User's full name (String)
- `email`: User's email address (String, unique, indexed)
- `hashed_password`: Securely stored password (String)
- `role`: PostgreSQL ENUM restricting roles to `Wildlife Researcher`, `Conservation Officer`, `Forest Department Officer`, or `Administrator`. Using an ENUM instead of a lookup table ensures strict data integrity while keeping the schema simple and performant.
- `organization`: The organization the user belongs to (String, optional)
- `created_at`: Timestamp (DateTime)

### 2. `monitoring_sites`
Represents a physical location being monitored.
- `id`: Primary key (Integer)
- `location_name`: Name of the site (String)
- `geom`: PostGIS Geometry column (`POINT`, SRID 4326). Used to store coordinates (longitude/latitude) directly. This allows native spatial queries (e.g., finding all sites within 50km of a boundary) rather than relying on separate and inefficient lat/lng float columns.
- `habitat_type`: Description of the environment (String, optional)
- `protected_area`: Name of the protected area if applicable (String, optional)
- `monitoring_device_type`: Primary device type at the site (String, optional)
- `created_by`: Foreign Key referencing `users.id`
- `created_at`: Timestamp (DateTime)

### 3. `surveys`
Records surveying campaigns or visits to a specific site.
- `id`: Primary key (Integer)
- `site_id`: Foreign Key referencing `monitoring_sites.id`
- `survey_date`: Date of the survey (Date)
- `status`: PostgreSQL ENUM (`planned`, `active`, `completed`)
- `notes`: Any specific survey notes (String, optional)

### 4. `devices`
Tracks hardware devices deployed at monitoring sites.
- `id`: Primary key (Integer)
- `site_id`: Foreign Key referencing `monitoring_sites.id`
- `device_type`: PostgreSQL ENUM (`camera_trap`, `audio_sensor`)
- `serial`: Device serial number (String, unique, indexed)
- `status`: Current device status (String)
- `last_active`: Last time the device phoned home (DateTime, optional)

### 5. `observation_log`
Registers raw observational data (images or audio) uploaded from devices or surveys.
- `id`: Primary key (Integer)
- `survey_id`: Foreign Key referencing `surveys.id`
- `uploaded_by`: Foreign Key referencing `users.id`
- `file_type`: PostgreSQL ENUM (`image`, `audio`)
- `storage_path`: Path or URL to the stored asset (String)
- `uploaded_at`: Timestamp (DateTime)
- `processing_status`: Status of downstream processing (String)

> [!NOTE]
> **Why is `observation_log` so thin?**
> The `observation_log` is intentionally kept minimal (with no fields for detected species, bounding boxes, or confidence scores). This is because the platform will eventually integrate complex Machine Learning pipelines (Image Analysis and Bioacoustics) in later milestones. These distinct ML engines will consume the raw logs and write their highly-specialized outputs to their own downstream tables (e.g., `image_detections`, `audio_classifications`). A monolithic table here would become a massive bottleneck and create tight coupling between unrelated domains.
