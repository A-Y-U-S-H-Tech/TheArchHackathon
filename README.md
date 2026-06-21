# TheArchHackathon — FMCG Operations Copilot

An enterprise-style FMCG operations copilot built as a **monolithic FastAPI backend** with modular systems for complaint intake, RAG retrieval, triage, ticketing, analytics, authentication, and product/knowledge management. The repository currently includes `app/` modules for `AUTH`, `CMS`, `CTAS`, `DAS`, `DMS`, `PKMS`, `PMS`, `RRS`, `STAT`, `TGS`, and `URSS`, wired together from `app/server.py`. citeturn600096view0turn319062view0turn288738view0

The system design is based on the FMCG Operations Copilot architecture document: PKMS, CMS, RRS, CTAS, TGS, DAS, DMS, AMS, PMS, and URSS, with validation and verification subsystems around them

## What this project does

- Registers and tracks FMCG customer complaints
- Retrieves relevant SOPs, product knowledge, and past cases using RAG
- Classifies complaints with an AI triage layer
- Generates support tickets and escalation paths
- Provides analytics for complaint trends, severity, and resolution flow
- Protects user and supervisor actions with authentication

## Hackathon value proposition

This project targets a real FMCG operations pain point: complaint handling is usually fragmented across support, quality, product, and escalation teams. The copilot unifies that flow into one operational loop:

**Complaint → Retrieval → Triage → Ticket → Dashboard**

That end-to-end flow is directly reflected in the design document and the seeded SOP data pack. fileciteturn1file12turn1file5

## Architecture

### Core systems
- **PKMS** — manages product catalogs, SOPs, manuals, and quality documents
- **CMS** — creates, updates, and tracks customer complaints
- **RRS** — retrieves relevant context from the knowledge base
- **CTAS** — analyzes complaint type, severity, root cause, and routing
- **TGS** — creates, updates, escalates, and closes tickets
- **DAS** — shows complaint and resolution analytics
- **AMS** — handles login, signup, logout, and token-based access
- **PMS** — manages product master data
- **URSS** — serves complaint history, status, and resolution context to the user
- **DMS** — shared persistence layer for products, complaints, tickets, documents, and users

This system breakdown and the entity model come from the design doc in the repo. fileciteturn1file4turn1file9

### Backend stack
- **FastAPI** for the API layer
- **Python** as the implementation language
- **CORS + cookie-based auth** for browser access
- **Vercel** for frontend deployment
- **Render** for backend deployment
- **Gemini 2.5 Flash** for complaint analysis and recommendation
- **ChromaDB** for vector retrieval
- **PostgreSQL** for structured data

The FastAPI app is assembled in `app/server.py` and includes the modular routers used by the project. citeturn288738view0

## Repository layout

```text
app/
├── AUTH/
├── CMS/
├── CTAS/
├── DAS/
├── DMS/
├── PKMS/
├── PMS/
├── RRS/
├── STAT/
├── TGS/
├── URSS/
├── HTML/
├── dms_instance.py
└── server.py
```

The repository also contains `requirements.txt`, `runtime.txt`, and deployment config files. GitHub’s file listing shows the project is mostly Python, with some HTML for the served UI. citeturn600096view0turn319062view0

## Key data models

### Product
```json
{
  "PID": "Product_ID",
  "PNM": "Product_Name",
  "PCAT": "Product_Category",
  "PDES": "Product_Description",
  "PSTA": "Product_Status"
}
```

### Complaint
```json
{
  "CID": "Complaint_ID",
  "CUS": "Customer_Name",
  "PID": "Product_ID",
  "CDES": "Complaint_Description",
  "CST": "Complaint_Status",
  "CSEV": "Complaint_Severity",
  "CDT": "Complaint_Date"
}
```

### Ticket
```json
{
  "TID": "Ticket_ID",
  "CID": "Complaint_ID",
  "DES": "Ticket_Description",
  "DEP": "Assigned_Department",
  "PRI": "Priority_Level",
  "STA": "Ticket_Status",
  "CRT": "Creation_Time"
}
```

### Knowledge Document
```json
{
  "DID": "Document_ID",
  "DNM": "Document_Name",
  "DTYPE": "Document_Type",
  "DPATH": "Storage_Path"
}
```

### User
```json
{
  "NAM": "user_name",
  "PAS": "user_password",
  "EMA": "user_email",
  "ROL": "user_role"
}
```

These entities are defined in the design document and used across the project’s systems. fileciteturn1file0turn1file4

## Typical workflow

1. A customer submits a complaint through the frontend or CMS.
2. The complaint is stored and validated.
3. RRS fetches relevant SOPs, product knowledge, and similar complaints.
4. CTAS classifies the issue and recommends severity and department routing.
5. TGS creates a ticket and assigns the case.
6. DAS updates operational metrics for the dashboard.
7. URSS exposes complaint history, progress, and resolution status to the user.

The SOP seed data in the repository supports this flow by providing complaint intake and packaging investigation examples. fileciteturn1file5turn1file7

## API surface

### Authentication
- `POST /AMS/login`
- `POST /AMS/signup`
- `POST /AMS/{user_name}/Update`
- `POST /AMS/logout`

### Product management
- `POST /PMS/Create`
- `POST /PMS/{PID}/Delete`
- `POST /PMS/{PID}/Update`
- `POST /PMS/Get_ALL`
- `GET /PMS/{Product_ID}/Get`

### Complaint management
- `POST /CMS/Create`
- `POST /CMS/return_all`
- `GET /CMS/{Complaint_ID}`
- `POST /CMS/{Complaint_ID}/Update`

### Knowledge management
- `POST /PKMS/upload_document`
- `GET /PKMS/all_documents`
- `POST /PKMS/{Document_ID}/Delete`

### Retrieval and triage
- `POST /RRS/retrieve`
- `POST /CTAS/analyze`

### Tickets
- `POST /TGS/create_ticket`
- `POST /TGS/{Ticket_ID}/Update`
- `POST /TGS/{Ticket_ID}/Escalate`
- `POST /TGS/{Ticket_ID}/Close`
- `POST /TGS/return_all`
- `GET /TGS/{Ticket_ID}/return`

### Dashboard and stats
- `GET /DAS/overview`
- `GET /DAS/agent_steps`
- `GET /STAT`

### User resources
- `POST /URSS/Complain/return_all`
- `GET /URSS/Complain/latest`
- `GET /URSS/Complain_Progress/{Complain_ID}`

These endpoints are taken from the design document. fileciteturn1file0turn1file4

## Local development

### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.server:app --reload --port 8080
```

### Notes
- The app is currently organized as a monolith with modular routers.
- `app/server.py` wires the routers together and serves the frontend HTML entry point. citeturn288738view0
- If you use cookies for auth in the browser, make sure frontend origin and backend CORS settings match. The server already defines allowed local and production frontend origins. citeturn288738view0

## Environment variables

A typical deployment may need:

```env
PORT=8080
GEMINI_API_KEY=...
DATABASE_URL=...
CHROMA_PATH=...
JWT_SECRET=...
```

## Demo seed data

The repo includes synthetic SOP data for hackathon use, such as complaint intake/triage and packaging defect investigation documents. These are useful as the initial knowledge base for RAG demonstrations. fileciteturn1file5turn1file7

## Suggested demo script

- Log in as a supervisor
- Upload an SOP document
- Create a complaint
- Run triage
- Generate a ticket
- Open the dashboard and show analytics
- Query complaint progress through URSS

## Future improvements

- Stronger validation layer
- Better UI workflow visualization
- More realistic sample documents
- Role-based dashboard views
- Persistent vector indexing and replayable demo scenarios

## License
The Project is in GPL v2 lincence.
