# Hackiwha Backend

This is the FastAPI backend behind Vynce, a marketplace connecting brands with content creators. Brands post paid campaigns, creators apply and submit a link to their finished social media post as proof of work, and the platform checks that submission before a creator gets paid. This repository is the API and database layer that the Hackiwha frontend talks to, built for the Hackiwha 3.0 hackathon.

## Table of Contents

- What it does
- Tech stack
- Project structure
- Data model
- Installation
- Configuration
- Running with Docker
- Running without Docker
- Database migrations
- API reference
- The verification pipeline
- Recommendations
- Performance insights
- Authentication
- Testing
- Contributing
- License

## What it does

A user registers, optionally creates one or more brands, and optionally builds a creator profile. As a brand owner, they post campaigns describing what they want, which platform it targets, a reward per one hundred thousand views, a target view count, an optional total budget, and a deadline. As a creator, they browse active campaigns, apply, and after posting their content, submit the link to that post. The backend then runs that link through a verification pipeline before the application can be marked as approved and paid out.

A single account is not locked into one role. The same person can own brands and apply to other brands' campaigns as a creator.

## Tech stack

FastAPI as the web framework

SQLAlchemy 2.0 style declarative models as the ORM

MySQL as the database, run through Docker Compose in development

Alembic for schema migrations

python jose for JWT access tokens, bcrypt for password hashing

httpx for outbound HTTP calls, used by the URL verification service

pydantic and pydantic settings for request and response validation and environment configuration

pytest and httpx for integration tests against a running instance

## Project structure

```
.
app/
    main.py
    core/
        config.py
        deps.py
        security.py
    db/
        base.py
        base_class.py
        session.py
    models/
        user.py
        profile.py
        brand.py
        campaign.py
        application.py
    schemas/
        user.py
        token.py
        profile.py
        brand.py
        campaign.py
        application.py
    crud/
        base.py
        crud_user.py
        crud_profile.py
        crud_brand.py
        crud_campaign.py
        crud_application.py
    api/
        v1/
            api.py
            endpoints/
                auth.py
                users.py
                profiles.py
                brands.py
                campaigns.py
                applications.py
    services/
        url_verification.py
        recommendations.py
        performance_insights.py
alembic/
    env.py
    script.py.mako
    versions/
alembic.ini
requirements.txt
Dockerfile
docker-compose.yml
tests/
    test_api.py
```

Layer | Responsibility
---|---
app/main.py | Creates the FastAPI app, wires up CORS, mounts the versioned API router under /api/v1, and exposes a health check at /
app/core/config.py | Reads all configuration from environment variables through pydantic settings
app/core/security.py | Password hashing and verification with bcrypt, JWT access token creation
app/core/deps.py | The get_current_user and get_current_active_user dependencies every protected endpoint relies on
app/db | The SQLAlchemy engine, session factory, and the declarative base every model inherits from
app/models | The five database tables: users, profiles, brands, campaigns, applications
app/schemas | The pydantic request and response shapes for each resource
app/crud | Thin, generic data access layer shared across resources, extended per resource where needed
app/api/v1/endpoints | The actual route handlers, one file per resource
app/services | Business logic that does not belong in a single endpoint: link verification, campaign recommendations, and performance insights

```mermaid
flowchart LR
    Client[Frontend / API client] -->|HTTP + Bearer token| Endpoints[app/api/v1/endpoints]
    Endpoints --> Deps[app/core/deps<br/>get_current_active_user]
    Endpoints --> Schemas[app/schemas<br/>request/response validation]
    Endpoints --> CRUD[app/crud<br/>data access]
    Endpoints --> Services[app/services<br/>verification, recommendations, insights]
    Deps --> CRUD
    CRUD --> Models[app/models<br/>SQLAlchemy tables]
    Services --> Models
    Models --> DB[(MySQL)]
```

## Data model

Table | Key fields | Notes
---|---|---
users | name, email, password, avatar, created_at | Password is stored as a bcrypt hash, never in plain text
profiles | user_id, bio, portfolio_url | One profile per user, created on demand rather than at registration
brands | owner_id, company_name, description, website, logo_url, created_at | A user can own more than one brand
campaigns | brand_id, title, description, platform, reward, target_views, total_budget, deadline, status, created_at | status is one of draft, active, paused, closed
applications | campaign_id, user_id, social_url, status, applied_at, submitted_at, verification_status, verification_notes, current_views, engagement_rate, amount_paid | status is one of pending, approved, rejected, completed. verification_status is one of not_submitted, pending, verified, flagged, and is set by the URL verification service described below

Deleting a user cascades to their profile. Deleting a brand cascades to its campaigns. Deleting a campaign cascades to its applications.

```mermaid
erDiagram
    USERS ||--o| PROFILES : has
    USERS ||--o{ BRANDS : owns
    BRANDS ||--o{ CAMPAIGNS : runs
    USERS ||--o{ APPLICATIONS : submits
    CAMPAIGNS ||--o{ APPLICATIONS : receives

    USERS {
        int id
        string name
        string email
        string password
        string avatar
    }
    PROFILES {
        int id
        int user_id
        string bio
        string portfolio_url
    }
    BRANDS {
        int id
        int owner_id
        string company_name
        string website
    }
    CAMPAIGNS {
        int id
        int brand_id
        string title
        float reward
        int target_views
        string status
    }
    APPLICATIONS {
        int id
        int campaign_id
        int user_id
        string social_url
        string status
        string verification_status
        int current_views
        float amount_paid
    }
```

## Installation

Requires Python 3.12, and either a local MySQL instance or Docker.

```bash
git clone https://github.com/Hackiwha-3-0-hackathon/Hackiwha-backend.git
cd Hackiwha-backend
pip install -r requirements.txt
```

## Configuration

All configuration is read from environment variables, loaded from a .env file in the project root through pydantic settings. Create a .env file with at least the following:

```
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/hackiwha
SECRET_KEY=replace-this-with-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
AI_FEATURES_ENABLED=false
AI_PROVIDER_API_KEY=
MYSQL_DATABASE=hackiwha
MYSQL_USER=user
MYSQL_PASSWORD=password
MYSQL_ROOT_PASSWORD=change-me
```

Variable | Required | Purpose
---|---|---
DATABASE_URL | Yes | SQLAlchemy connection string for MySQL
SECRET_KEY | Yes | Signs and verifies JWT access tokens, keep this private and unique per environment
ALGORITHM | No, defaults to HS256 | JWT signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES | No, defaults to 60 | How long a login token stays valid
BACKEND_CORS_ORIGINS | No, defaults to http://localhost:3000 | Origins allowed to call this API from a browser, update this to match wherever the frontend is actually served from
AI_FEATURES_ENABLED | No, defaults to false | Toggles the AI powered layers of the verification, recommendation, and insights services
AI_PROVIDER_API_KEY | No | API key for the AI provider used when AI_FEATURES_ENABLED is turned on
MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD, MYSQL_ROOT_PASSWORD | Yes, when using docker-compose.yml | Passed straight through to the MySQL container

Never commit a real .env file or a real SECRET_KEY.

## Running with Docker

```bash
docker compose up --build
```

This starts a MySQL container with a health check, waits for it to become healthy, runs alembic upgrade head to apply migrations, and then starts uvicorn on port 8000. The backend container mounts the current directory as a volume, so code changes are picked up without rebuilding the image, though uvicorn still needs to be restarted to reload unless it is run with the reload flag.

```bash
docker compose down
docker compose logs
docker ps
```

## Running without Docker

With a MySQL instance already running and DATABASE_URL pointed at it:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000, with interactive documentation at http://localhost:8000/docs, generated automatically by FastAPI.

## Database migrations

Schema changes are managed through Alembic. app/db/base.py imports every model so Alembic's autogenerate can see the full metadata.

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

The single migration currently in the repository, 49efe694ed0e_create_tables.py, creates all five tables.

## API reference

All routes are mounted under /api/v1. Routes marked as requiring auth expect an Authorization: Bearer token header, obtained from the login endpoint.

### Auth

Method and path | Description | Auth required
---|---|---
POST /auth/register | Create a new user account | No
POST /auth/login | Exchange an email and password, sent as OAuth2 form data, for a bearer token | No

### Users

Method and path | Description | Auth required
---|---|---
GET /users/me | Get the current user | Yes
PUT /users/me | Update the current user's name or avatar | Yes
GET /users/{user_id} | Get any user by id | No

### Profiles

Method and path | Description | Auth required
---|---|---
GET /profiles/me | Get the current user's creator profile, if one exists | Yes
POST /profiles/me | Create a profile for the current user | Yes
PUT /profiles/me | Update the current user's profile | Yes
GET /profiles/{user_id} | Get another user's profile | No

### Brands

Method and path | Description | Auth required
---|---|---
POST /brands/ | Create a brand owned by the current user | Yes
GET /brands/ | List all brands, paginated with skip and limit | No
GET /brands/me | List brands owned by the current user | Yes
GET /brands/{brand_id} | Get a single brand | No
PUT /brands/{brand_id} | Update a brand, only the owner may do this | Yes
DELETE /brands/{brand_id} | Delete a brand, only the owner may do this | Yes

### Campaigns

Method and path | Description | Auth required
---|---|---
GET /campaigns/ | List campaigns, paginated, filtered to active only by default | No
GET /campaigns/recommended | List campaigns ranked for the current user's profile, see Recommendations below | Yes
GET /campaigns/{campaign_id} | Get a single campaign | No
GET /campaigns/{campaign_id}/insights | Get the top performing submissions for a campaign, see Performance insights below | No
POST /campaigns/brand/{brand_id} | Create a campaign under a brand, only the brand owner may do this | Yes
GET /campaigns/brand/{brand_id} | List every campaign under a brand | No
PUT /campaigns/{campaign_id} | Update a campaign, only the brand owner may do this | Yes
DELETE /campaigns/{campaign_id} | Delete a campaign, only the brand owner may do this | Yes

### Applications

Method and path | Description | Auth required
---|---|---
POST /applications/ | Apply to a campaign, fails if the current user already applied | Yes
GET /applications/me | List the current user's own applications | Yes
GET /applications/campaign/{campaign_id} | List every application to a campaign, only the campaign's brand owner may view this | Yes
PUT /applications/{application_id} | Update an application. The applicant may update social_url, the brand owner may additionally update status. Submitting a social_url here automatically triggers verification | Yes
POST /applications/{application_id}/verify | Re run verification on an application's current social_url. Either the applicant or the brand owner may call this | Yes

## The verification pipeline

app/services/url_verification.py decides whether a creator's submitted social media link is legitimate before payment. When a creator submits a social_url, the service makes a real HTTP GET request to that URL and checks for a non error status code. GET is used instead of HEAD because TikTok and Instagram reject HEAD requests.

If the URL is unreachable, the application is immediately marked flagged. If it is reachable, the application is left in a pending verification state so a human reviewer, typically the brand owner, can inspect the submitted content and make the final call by updating the application's status directly. This keeps a person in the loop on every payout decision.

Verification runs automatically whenever a social_url is set through PUT /applications/{application_id}, and can be re triggered on demand through POST /applications/{application_id}/verify.

```mermaid
flowchart TD
    A[Creator submits social_url] --> B[Reachability check<br/>real HTTP GET to social_url]
    B --> C{URL reachable?}
    C -- no --> D[verification_status = flagged]
    C -- yes --> E[verification_status = pending]
    E --> F[Human reviewer, typically the brand owner,<br/>makes the final call via application status]
```

## Recommendations

app/services/recommendations.py powers GET /campaigns/recommended. It tokenizes the current user's profile bio and portfolio URL, tokenizes each active campaign's title and description, strips a small stopword list, and ranks campaigns by how many tokens overlap between the two. If the user has no profile or an empty bio and portfolio URL, it falls back to the most recent active campaigns, so the endpoint always returns a useful ranked list.

## Performance insights

app/services/performance_insights.py powers GET /campaigns/{campaign_id}/insights. get_top_performing_submissions queries completed applications for a campaign and ranks them by current_views, giving a brand owner a quick view of which creator submissions performed best.

## Authentication

Login uses the OAuth2 password flow. The username field in the form body is the user's email. A successful login returns a JWT bearer token whose subject claim is the user's id and which expires after ACCESS_TOKEN_EXPIRE_MINUTES.

Every protected endpoint depends on get_current_active_user, which decodes the token, loads the corresponding user from the database, and rejects the request with a 401 if the token is missing, invalid, expired, or does not resolve to a real user.

```mermaid
sequenceDiagram
    participant Client
    participant Auth as POST /auth/login
    participant DB as Database
    participant Endpoint as Protected endpoint

    Client->>Auth: username (email), password
    Auth->>DB: look up user by email
    DB-->>Auth: user row with password hash
    Auth->>Auth: verify_password (bcrypt)
    Auth->>Auth: create_access_token (JWT, subject = user id)
    Auth-->>Client: access_token

    Client->>Endpoint: request with Authorization: Bearer token
    Endpoint->>Endpoint: decode JWT, extract subject
    Endpoint->>DB: load user by id
    DB-->>Endpoint: user row
    Endpoint-->>Client: 200 with response, or 401 if missing/invalid/expired
```

## Testing

```bash
pytest
```

tests/test_api.py runs integration style tests against a live instance at http://localhost:8000/api/v1, registering a fresh throwaway user for each test run rather than mocking the database. The backend needs to already be running, migrated, and reachable at that address before running pytest.

## Contributing

1. Fork the repository
2. Create a branch: git checkout -b feature/your-feature
3. Commit your changes with clear, scoped commit messages
4. Open a pull request describing what changed and why

When adding a new resource, follow the existing pattern: a SQLAlchemy model under app/models, a pydantic schema under app/schemas, a CRUD class extending CRUDBase under app/crud, and a router under app/api/v1/endpoints registered in app/api/v1/api.py.

## License

MIT. See LICENSE if present in the repository, or add one before making the repository public.

Built for Hackiwha 3.0.

