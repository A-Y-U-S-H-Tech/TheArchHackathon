
# FMCG Operations Copilot Design Document

## System-wise Distribution of Roles and Work

### Systems
- **Product Knowledge Management System (PKMS)** — Level 0
- **Complaint Management System (CMS)** — Level 1
- **RAG Retrieval System (RRS)** — Level 2
- **Complaint Triage Agent System (CTAS)** — Level 3
- **Ticket Generation System (TGS)** — Level 3
- **Dashboard Analytics System (DAS)** — Level 2
- **Data Management System (DMS)** — Independent
- **Authentication Magement System (AMS)** - Level 0
- **Product Mangement System (PMS)** - Level 0

---

## Roles of Each System

### 1. Product Knowledge Management System (PKMS)

Maintains all FMCG knowledge documents:

1. Product catalogs
2. SOP documents
3. Complaint resolution manuals
4. Quality guidelines
5. Manufacturing guidelines
6. Product specifications

### 2. Complaint Management System (CMS)

Manages customer complaints:

1. Complaint registration
2. Complaint tracking
3. Complaint update
4. Complaint resolution
5. Complaint history

### 3. RAG Retrieval System (RRS)

Retrieves relevant information from the knowledge base:

1. Search product information
2. Search SOP documents
3. Search previous complaints
4. Search quality guidelines
5. Search resolution procedures

### 4. Complaint Triage Agent System (CTAS)

Intelligently analyzes complaints:

1. Complaint classification
2. Severity detection
3. Root cause analysis
4. Department assignment
5. Resolution recommendation

### 5. Ticket Generation System (TGS)

Generates and manages support tickets:

1. Create ticket
2. Update ticket
3. Escalate ticket
4. Close ticket
5. Assign ticket

### 6. Dashboard Analytics System (DAS)

Generates business insights:

1. Complaint statistics
2. Product-wise complaints
3. Severity distribution
4. Resolution time analysis
5. Agent activity tracking

### 7. Frontend Serving System (FSS)

Serves the frontend dashboard:

- HTML
- CSS
- JavaScript
- Dashboard components
- Charts
- Agent workflow visualization

### 8. Validation System

Validates all incoming data for the other systems and returns a boolean response:

- `true` if valid
- `false` if invalid

### 9. Verification System

Verifies all data for the other systems and returns a boolean response:

- `true` if verified
- `false` if not verified

### 10. Data Management System (DMS)

Manages all data for the other systems:

1. Create entity
2. Update entity
3. Delete entity
4. Check entity existence
5. Retrieve entity

### 11. Authentication Management System(AMS)
manages all the account and authentication related tasks
  1. Login
  2. Register
  3. Delete
  4. Logout
  5. Authentication Token

---

## Entity Structures

### 1. Product

```text
{
    PID: Product_ID,
    PNM: Product_Name,
    PCAT: Product_Category,
    PDES: Product_Description,
    PSTA: Product_Status
}
```

### 2. Complaint

```text
{
    CID: Complaint_ID,
    CUS: Customer_Name,
    PID: Product_ID,
    CDES: Complaint_Description,
    CST: Complaint_Status,
    CSEV: Complaint_Severity,
    CDT: Complaint_Date
}
```

### 3. Ticket

```text
{
    TID: Ticket_ID,
    CID: Complaint_ID,
    DES: Ticket_Description
    DEP: Assigned_Department,
    PRI: Priority_Level,
    STA: Ticket_Status,
    CRT: Creation_Time
}
```

### 4. Knowledge Document

```text
{
    DID: Document_ID,
    DNM: Document_Name,
    DTYPE: Document_Type,
    DPATH: Storage_Path
}
```

### 5. Retrieved Context

```text
{
    RID: Retrieval_ID,
    QUERY: User_Query,
    CONTEXT: Retrieved_Content
}
```
### 6. USER
'''Json
{
    NAM:user_nam,
    PAS:user_password,
    EMA:user_email,
    ROL:users_role,
}

---

## System Definitions
##
## Product Managment System
  - Only SUP roles can call this resoureces and fucnctions
  - /PMS/Create POST:-
    - It Creates A Product ID
    - it requries the foolowing json request:-
      -{
        PNM:Product_Name,
        PCAT:Product_Catogory,
        PDES:Product_Description,
        PSTA:Product_Status (Active,Deactive,Archived)
      }
  - /PMS/{PID}/Delete POST:-
    - here PID refres to the product ID 
    - It deletes the given product with the given PID
  - /PMS/{PID}/Update POST:-
    - PID refres to the Product ID
    - it updates a Particular Product with a Product ID
    - It requires the foolowing json Request:-
      -{
        PSTA:product_Status | Pass false if don't want to update
        PDES:product_Statis | pass false if don't want to update
      }
  
  - /PMS/Get_ALL POST:-
    - It returns product between i and j index PID
    - it takes the following json :{
      i : Start_Index
      j : Stop_Index
    }
    - if there are no product in that range it will return a empty list

  - /PMS/{Product_ID}/Get GET:-
    - this will return the product with the respective product id or will return 400 status code

## Authentication Management System
  - Role Defination:-
    - CUS :- Coustomer of the bussniess
    - SUP :- Coustomer Executieve supervisor
    - CSE :- Coustomer Service Executive
  - AMS/login (POST):-
    - This url allowes user login and sends a JWT to client for authentication
    - the request should be supplied in this json formate:-
      - {
        NAM:user_name,
        PAS:user_password
      }
    - the response will be this json with 200 if succeded and a JWT cookie will be set
    - if failes to login then status code 401 will be returned
  - AMS/signup (POST):-
    - A Sigup doesn't login automaticly you need to pass a seprate login request
    - For Coustomer:-
      - the request should be in this json formate:-
        - {
          NAM:user_name,
          PAS:user_password,
          EMA:user_email,
          ROL:'CUS'
        }
      - the response will be 200 if success and 401 if failed
    - For Coustomer Service Executive-
      - The Account can only be created by a Coustomer Service Supervisor who has loged in else the Account creation will fail
      - the request should be in this json formate:-
        - {
          NAM:user_name,
          PAS:user_password,
          EMA:user_email,
          ROL:'CSE'
        }
    - For Coustomer Service Supervisor:-
      - A Coustomer Service Superviser account needs to be manully created it cann't be created by request to this route
  - /AMS/{user_name}/Update (POST):
    - ALL resources here are protected and need authenication
    - For Coustomers:-
      - The json Request Should be:-
        - {
          EMA:Updated_email or false if no need for email update
          PAS:Updated_password or false if no need for password update
        }
      - The response will be 200 status if succeded and 400 status code if failed
    - For Coustomer Service Executive:-
      - The json Request by a CSE role user:-
        - {
          EMA:Updated_email or false if no need for email update
          PAS:Updated_password or false if no need for password update
        }
      - the json Request by a SUP role user:-
        - {
          EMA:Updated_email or false if no need for email update
          PAS:Updated_password or false if no need for password update
          ROL:true to change role to SUP & false to not change
        }
      - The response will be 200 status if succeded and 400 status code if failed
    - For Coustomer Service Supervisor:-
      - The json Request Should be:-
        - {
          EMA:Updated_email or false if no need for email update
          PAS:Updated_password or false if no need for password update
        }
      - The response will be 200 status if succeded and 400 status code if failed
  - /AMS/logout (POST):-
    - will logout the currently loged in user
## Product Knowledge Management System (PKMS)

All resources are protected and require authentication with role SUP (superviser).

### `POST /PKMS/upload_document`

Uploads product knowledge documents.

multi-part form data Request:
  - part 1 as the uploadfile as Ufile
  - part 2 as the metaData with the following stringified json
  {
    DID: Document_ID,
    DNM: Document_Name,
    DTYPE: Document_Type,(in this formate cat1/subcat2/ there should be trailing /)
  }

Behavior:

- Validates file
- Stores file
- Sends file to RAG processing

Response:

```json
{
  "ok"
}
```with 200 status code 

### `GET /PKMS/all_documents`

Returns all uploaded documents.

### `POST /PKMS/{Document_ID}/Delete`

Deletes a document.

---

## Complaint Management System (CMS)

### `POST /CMS/Create`

Request:

```json
{
  "CUS": "Customer Name",
  "PID": "Product ID",
  "CDES": "Complaint Description"
}
```

Creates a complaint entry.

### `POST /CMS/return_all`

Request:

```json
{
  "i": "start_index",
  "j": "end_index"
}
```

Returns all complaints between `i` and `j`.

### `GET /CMS/{Complaint_ID}`

Returns complaint details.

### `POST /CMS/{Complaint_ID}/Update`

Request:

```json
{
  "CDES": "Updated Description",
  "CST": "Updated Status"
}
```

Updates complaint.

---

## RAG Retrieval System (RRS)

Internal system only.

### Process Flow

```text
Document
   ↓
Chunking
   ↓
Embedding Creation
   ↓
Store in ChromaDB
```

### Retrieval Flow

```text
User Query
      ↓
Vector Search
      ↓
Relevant Chunks
      ↓
Return Context
```

### `POST /RRS/retrieve`

Request:

```json
{
  "query": "Leaking shampoo bottle complaint"
}
```

Response:

```json
{
  "retrieved_context": "Relevant SOP and previous complaints"
}
```

---

## Complaint Triage Agent System (CTAS)

### `POST /CTAS/analyze`

Request:

```json
{
  "CID": "Complaint_ID"
}
```

Agent actions:

1. Retrieve product information
2. Retrieve SOP
3. Retrieve similar complaints
4. Analyze complaint
5. Classify severity
6. Recommend resolution

Response:

```json
{
  "category": "Packaging Issue",
  "severity": "High",
  "department": "Quality Control",
  "recommended_action": "Immediate Inspection"
}
```

---

## Ticket Generation System (TGS)

### `POST /TGS/create_ticket`

Request:

```json
{
  "CID": "Complaint_ID",
  "PRI": "Priority",
  "DEP": "Depatment",
  "DES": "Description of ticket"
}
```



### `POST /TGS/{Ticket_ID}/Update`

Updates ticket status.

### `POST /TGS/{Ticket_ID}/Escalate`

Escalates ticket.

### `POST /TGS/{Ticket_ID}/Close`

Closes ticket.

## 'POST /TGS/return_all'
- Json Request Needed
{
  i:start_index,
  j:end_index
}
- will return ticket between these indices
- return empty list if there exits non between the range i an j 

## 'GET /TGS/{Ticket_ID}/return'
- this will fetch ticket with the coreesponding ticket_ID given else return 400 status cod if none are found 

---

## Dashboard Analytics System (DAS)

### `GET /DAS/overview`

Returns:

```json
{
  "total_complaints": 150,
  "resolved_complaints": 120,
  "open_complaints": 30,
  "high_severity": 18
}
```

### `GET /DAS/agent_steps`

Returns:

```json
{
  "Step1": "Complaint Received",
  "Step2": "Knowledge Retrieval",
  "Step3": "Triage Analysis",
  "Step4": "Ticket Generated",
  "Step5": "Assigned To Team"
}
```

---

## Data Management System (DMS)

### Backend Technologies

- ChromaDB — vector database
- PostgreSQL — structured data

Internal system only.

### Create Entity

#### Product
Creates product records.

#### Complaint
Creates complaint records.

#### Ticket
Creates ticket records.

#### Document
Creates document records.

### Update Entity

#### Complaint
Updates complaint information.

#### Ticket
Updates ticket status.

### Retrieve Entity

#### Complaint
Retrieves complaint information.

#### Product
Retrieves product information.

#### Ticket
Retrieves ticket information.

### Check Exists

#### Product
Returns:

```text
true
false
```

#### Complaint
Returns:

```text
true
false
```

---

## Statistics System

### `GET /STAT`

Returns:

```json
{
  "total_products": 250,
  "total_documents": 500,
  "total_complaints": 150,
  "total_tickets": 150,
  "total_resolved": 120
}
```

---

## Frontend Serving System

### Deployment

- Vercel

### Main Pages

### `/dashboard`

Contains:

1. Complaint submission form
2. Product search
3. Complaint history
4. Agent workflow viewer
5. Ticket dashboard

### `/knowledge`

Contains:

1. Upload documents
2. View documents
3. Search knowledge base

### `/tickets`

Contains:

1. Open tickets
2. Escalated tickets
3. Closed tickets

---

## Backend Infrastructure

### Backend API

- FastAPI

### Deployment

- Render

### AI Model

- Google AI Studio / Gemini 2.5 Flash

Use for:

1. Complaint analysis
2. Severity detection
3. Root cause analysis
4. Ticket recommendation

---

## Complete System Flow

```text
Customer Complaint
        ↓
Complaint Management System
        ↓
RAG Retrieval System
        ↓
Retrieve SOP + Product Knowledge + Past Complaints
        ↓
Complaint Triage Agent
        ↓
Severity Detection
        ↓
Department Assignment
        ↓
Ticket Generation System
        ↓
Ticket Creation
        ↓
Dashboard Analytics System
        ↓
Agent Workflow Display
        ↓
Final Resolution Recommendation
```

This design is structured for an enterprise-style hackathon submission and demonstrates RAG, agentic AI, ticket automation, and FMCG operational value.
## Note:-

-Server is Monolitic in nature
