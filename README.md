<!-- SYNCRONAL — AI-powered BIS Standard Recommendation System -->

<div align="center">

# SYNCRONAL

### AI-Powered BIS Standard Recommendation System

**From Procurement Requirements to Relevant BIS Standards**

<br>

<img src="https://img.shields.io/badge/SIH26108-Smart%20India%20Hackathon%202026-1f6feb?style=for-the-badge">
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white">
<img src="https://img.shields.io/badge/FAISS-Vector%20Search-1877F2?style=for-the-badge">
<img src="https://img.shields.io/badge/Azure-Backend-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white">
<img src="https://img.shields.io/badge/Vercel-Frontend-000000?style=for-the-badge&logo=vercel&logoColor=white">

<br><br>

<a href="https://sih-26108-hackthon-prototype.vercel.app/">
<img src="https://img.shields.io/badge/CLICK%20HERE%20TO%20TRY%20THE%20LIVE%20PROTOTYPE-000000?style=for-the-badge">
</a>

</div>



# SYNCRONAL — GitHub Profile-Style README

Copy-paste the following directly into your `README.md`:

````markdown
<!-- SYNCRONAL — AI-powered BIS Standard Recommendation System -->

<div align="center">

# SYNCRONAL

### AI-Powered BIS Standard Recommendation System

**From Procurement Requirements to Relevant BIS Standards**

<br>

<img src="https://img.shields.io/badge/SIH26108-Smart%20India%20Hackathon%202026-1f6feb?style=for-the-badge">
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white">
<img src="https://img.shields.io/badge/FAISS-Vector%20Search-1877F2?style=for-the-badge">
<img src="https://img.shields.io/badge/Azure-Backend-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white">
<img src="https://img.shields.io/badge/Vercel-Frontend-000000?style=for-the-badge&logo=vercel&logoColor=white">

<br><br>

<a href="https://sih-26108-hackthon-prototype.vercel.app/">
<img src="https://img.shields.io/badge/CLICK%20HERE%20TO%20TRY%20THE%20LIVE%20PROTOTYPE-000000?style=for-the-badge">
</a>

</div>

---

## About Syncronal

Syncronal is an AI-powered decision-support system designed to help procurement teams identify relevant **Bureau of Indian Standards (BIS)** standards from real-world procurement requirements.

Procurement requirements are normally written in natural, practical language, while BIS standards use technical and highly specific terminology. This creates a gap between what a procurement team needs and how standards are described.

Syncronal bridges this gap using **Natural Language Processing, Semantic Search, FAISS Vector Retrieval, BIS Hybrid Ranking, Lifecycle Validation, and Document Intelligence**.

The system accepts either a natural-language procurement requirement or an uploaded procurement document and returns a ranked list of relevant BIS standards.

---

## Problem

Finding the right BIS standard for a procurement requirement can require searching through multiple standards and determining which one is actually applicable.

The challenge becomes harder when:

- The requirement is written in natural language.
- BIS standards use technical terminology.
- Multiple standards appear semantically relevant.
- Standards may have different lifecycle statuses.
- Users may need to understand related or referred standards.
- Procurement documents can contain much more information than a simple keyword query.

Syncronal addresses this problem by converting the procurement requirement into a machine-understandable semantic representation and ranking BIS standards according to relevance and BIS-specific information.

---

## Proposed Solution

```text
Procurement Requirement
        |
        v
Input Validation
        |
        v
Text / PDF / DOCX / TXT
        |
        v
Semantic Understanding
        |
        v
Sentence Transformer
all-MiniLM-L6-v2
        |
        v
384-D Embeddings
        |
        v
FAISS Vector Retrieval
        |
        v
Top Candidate Standards
        |
        v
BIS Hybrid Ranking
        |
        v
Lifecycle Validation
        |
        v
Top Relevant BIS Standards
        |
        v
Related / Referred Standards
        |
        v
Explanation + Official BIS Links
````

---

## How Syncronal Works

### 1. BIS Knowledge Base

The system uses a structured BIS standards knowledge base containing information such as:

* IS Number
* Standard Title
* Status
* Department
* Technical Committee
* Group
* Sub Group
* Sub-Sub Group
* Type of Standard
* Certification Information
* Relevant Ministries
* Revisions
* Amendments
* Reaffirmation Year
* Superseding Standard
* Official BIS Source URL

The knowledge base currently contains approximately **3,896 BIS standards** for the prototype.

### 2. Data Acquisition

BIS information is collected from official BIS sources using **Playwright-based browser automation**.

The acquired information is cleaned and converted into a structured dataset suitable for semantic search and ranking.

### 3. Data Preprocessing

The preprocessing pipeline handles:

* Missing values
* Status normalization
* Certification normalization
* Technical committee cleanup
* Standard type normalization
* Revisions and amendments
* Reaffirmation information
* Superseding standards
* BIS classification information
* Search-text construction

A dedicated `search_text` representation combines important BIS metadata to create a richer semantic representation of each standard.

### 4. Semantic Understanding

Syncronal uses the **Sentence Transformers `all-MiniLM-L6-v2`** model.

Each BIS standard is converted into a **384-dimensional embedding vector**.

The procurement requirement is also converted into the same vector space.

This allows the system to compare the meaning of the procurement requirement with the meaning of BIS standards rather than relying only on exact keyword matching.

### 5. FAISS Vector Retrieval

The generated embeddings are indexed using **FAISS**.

Syncronal uses:

```text
FAISS IndexFlatIP
```

The embeddings are normalized before indexing.

Because normalized vectors are used, the inner product becomes equivalent to cosine similarity.

FAISS retrieves the strongest semantic candidates from the BIS knowledge base.

### 6. BIS Hybrid Ranking

Semantic similarity alone is not sufficient for procurement-oriented recommendations.

Therefore, Syncronal applies a BIS-specific hybrid ranking layer.

The current prototype uses:

```text
Final Score =
0.70 × Semantic Similarity
+ 0.15 × Classification Similarity
+ 0.10 × Status Score
+ 0.05 × Certification Score
```

The ranking considers:

* Semantic relevance
* BIS classification relevance
* Standard status
* Certification requirements

This allows the system to combine AI-based semantic understanding with structured BIS information.

### 7. Lifecycle Validation

A highly similar standard should not automatically become the final recommendation if it is no longer active.

Syncronal therefore applies lifecycle handling after ranking.

The prototype specifically filters **withdrawn standards** from the primary recommendations while retaining lifecycle-related information such as superseding standards for version awareness.

This separates:

```text
Ranking Signal
        +
Hard Lifecycle Rule
```

from one another.

### 8. Related and Referred Standards

BIS standards can reference other standards.

Syncronal maintains a separate relationship layer containing approximately **31,981 standard relationships**.

The system can identify:

* Referred In Standards
* Referred By Standards

These relationships are shown separately from the primary recommendations because a related standard is not necessarily the best direct procurement recommendation.

### 9. Document Intelligence

Syncronal supports procurement requirements provided as:

* Plain text
* PDF
* DOCX
* TXT

The system extracts the document content and processes the extracted requirement through the same recommendation pipeline.

Document size and extraction limits are applied to prevent excessively large inputs.

### 10. Input Validation

The system validates the input before performing recommendation.

It checks whether the input appears to represent a procurement/BIS-related requirement.

Examples of inputs that can be rejected include:

* Resume documents
* Unrelated text
* Non-procurement content

This prevents irrelevant documents from being passed into the recommendation engine.

---

## Core Features

| Feature                 | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| Natural Language Search | Search BIS standards using procurement language          |
| Document Upload         | Upload PDF, DOCX or TXT procurement documents            |
| Semantic Search         | Understand meaning beyond exact keywords                 |
| Vector Retrieval        | Retrieve candidate standards using FAISS                 |
| Hybrid Ranking          | Combine semantic and BIS-specific signals                |
| Lifecycle Handling      | Prevent withdrawn standards from primary recommendations |
| Certification Awareness | Consider mandatory/voluntary certification information   |
| Related Standards       | Show referred-in and referred-by relationships           |
| Official Links          | Provide access to official BIS source information        |
| Input Validation        | Reject clearly irrelevant documents and queries          |
| Ranked Results          | Present the most relevant standards first                |

---

## Technology Stack

| Layer               | Technology                          |
| ------------------- | ----------------------------------- |
| Frontend            | HTML, CSS, JavaScript               |
| Backend             | FastAPI                             |
| API Server          | Uvicorn                             |
| Data Processing     | Python, Pandas, NumPy, scikit-learn |
| NLP / Embeddings    | Sentence Transformers               |
| Embedding Model     | all-MiniLM-L6-v2                    |
| Embedding Dimension | 384                                 |
| Vector Search       | FAISS                               |
| Data Acquisition    | Playwright                          |
| PDF Processing      | pypdf                               |
| DOCX Processing     | python-docx                         |
| Backend Deployment  | Azure App Service                   |
| Frontend Deployment | Vercel                              |
| Version Control     | Git + GitHub                        |

---

## System Architecture

```text
                    BIS OFFICIAL SOURCES
                           |
                           v
                    Playwright Scraper
                           |
                           v
                    Data Preprocessing
                           |
                           v
                 BIS Standards Knowledge Base
                           |
                           v
              Sentence Transformer Model
                  all-MiniLM-L6-v2
                           |
                           v
                  384-D Embeddings
                           |
                           v
                    FAISS Index
                           |
                           |
User ----------------> FastAPI Backend
 |                         |
 |                         v
 |                  Input Validation
 |                         |
 |                         v
 |                  Query Embedding
 |                         |
 |                         v
 |                  FAISS Retrieval
 |                         |
 |                         v
 |                 Hybrid Ranking
 |                         |
 |                         v
 |                Lifecycle Validation
 |                         |
 |                         v
 |              Related Standards Layer
 |                         |
 v                         v
Frontend <----------- Recommendations
                           |
                           v
                  Official BIS References
```

---

## Project Structure

```text
SIH26108-Hackthon-Prototype/
│
├── backend/
│   ├── main.py
│   └── schemas.py
│
├── ml/
│   ├── embeddings.py
│   ├── faiss_retriever.py
│   ├── hybrid_ranker.py
│   └── intent_detector.py
│
├── data/
│   ├── master_standards.csv
│   ├── relationships.csv
│   └── classification.csv
│
├── models/
│   ├── standard_embeddings.npy
│   └── standards.faiss
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── logo.png
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## API Endpoints

```text
GET  /
GET  /health
POST /recommend
POST /recommend-document
```

### `/recommend`

Accepts a natural-language procurement requirement and returns ranked BIS recommendations.

### `/recommend-document`

Accepts a procurement document and extracts its text before running the recommendation pipeline.

---

## Example Input

```text
We require low-voltage copper power cables with PVC insulation
for electrical power distribution in a commercial building.
The cables should comply with applicable BIS requirements,
including testing, marking and certification requirements.
```

### Example Output

```text
Recommended BIS Standards

1. Most relevant standard
2. Second relevant standard
3. Third relevant standard
4. Additional relevant standards
...
10. Relevant standard

Each recommendation can provide:
- IS Number
- Standard Title
- Relevance Score
- Status
- Certification
- BIS classification
- Related standards
- Official BIS source
```

---

## Deployment

The prototype uses a separated deployment architecture:

```text
                    Internet User
                          |
                          v
                 Vercel Frontend
                          |
                          v
                Azure App Service
                    FastAPI API
                          |
             +------------+------------+
             |                         |
             v                         v
        FAISS Index              BIS Dataset
             |
             v
     Sentence Transformer
```

Frontend:

**Vercel**

Backend:

**Microsoft Azure App Service**

Repository:

**GitHub**

Live Prototype:

[https://sih-26108-hackthon-prototype.vercel.app/](https://sih-26108-hackthon-prototype.vercel.app/)

---

## Research and References

The project was developed using a combination of official documentation, technical resources, research material and practical experimentation.

### Primary Data Source

* Bureau of Indian Standards (BIS)
* BIS Standards Portal
* BIS Know Your Standard

### Technical References

* Sentence Transformers documentation
* FAISS documentation
* FastAPI documentation
* Playwright documentation
* Azure App Service documentation
* Vercel documentation
* Python and machine-learning documentation
* Google technical resources
* YouTube technical lectures and tutorials
* Research papers and technical examples

### AI-Assisted Development

AI tools were used as development and research accelerators for:

* Technical research
* Concept understanding
* Architecture exploration
* Coding assistance
* Debugging
* Data-processing ideas
* Machine-learning implementation
* Documentation
* Testing
* Presentation preparation

The implementation was reviewed and understood by the team rather than relying on AI-generated code without verification.

---

## Current Prototype

Syncronal is currently a **working prototype developed for Smart India Hackathon 2026 problem statement SIH26108**.

Current capabilities include:

* BIS standards knowledge base
* Semantic embedding pipeline
* FAISS vector retrieval
* BIS Hybrid Ranking
* Lifecycle filtering
* Related-standard relationships
* Natural-language procurement search
* PDF/DOCX/TXT document processing
* Input validation
* FastAPI backend
* Web frontend
* Cloud deployment

---

## Current Limitations

The current system is a prototype and is not intended to be treated as a production-grade BIS decision system.

Current limitations include:

* Ranking weights are manually configured.
* Semantic similarity does not guarantee legal or technical applicability.
* Some specialized standards can still rank above a more directly applicable standard.
* The current dataset represents a prototype knowledge base rather than a continuously synchronized production BIS database.
* Lifecycle intelligence can be expanded further.
* Domain-specific ranking can be improved with larger validated datasets.
* Recommendations should be reviewed by qualified procurement or technical personnel before final decisions.

---

## Future Scope

Future versions of Syncronal can include:

* Continuous BIS data synchronization
* Domain-specific ranking models
* Learning-to-rank models
* Improved lifecycle and supersession intelligence
* Explainable recommendation reasoning
* Standard-to-standard dependency graphs
* Advanced document understanding
* User authentication
* User search history
* Saved recommendations
* Procurement workflow integration
* Enterprise dashboards
* Feedback-based ranking improvement
* Large-scale production infrastructure

---

## Project Vision

Syncronal aims to reduce the gap between **procurement requirements and technical standards**.

The objective is not to replace BIS standards, technical experts, or procurement officers.

The objective is to make the discovery process faster, more intelligent and easier to navigate by transforming natural-language requirements into ranked, explainable BIS standard recommendations.

```text
Human Requirement
       ↓
AI Semantic Understanding
       ↓
BIS Knowledge
       ↓
Intelligent Retrieval
       ↓
BIS Hybrid Ranking
       ↓
Lifecycle Validation
       ↓
Relevant Standards
```

---

<div align="center">

## SYNCRONAL

### Intelligent Discovery of BIS Standards

**SIH26108 | Smart India Hackathon 2026**

<br>

<a href="https://sih-26108-hackthon-prototype.vercel.app/">
<b>Live Prototype</b>
</a>

  |  

<a href="https://github.com/vikrampal12345/SIH26108-Hackthon-Prototype">
<b>GitHub Repository</b>
</a>

<br><br>

Built for smarter procurement, better standard discovery, and faster decision support.

</div>
```


---

## About Syncronal

Syncronal is an AI-powered decision-support system designed to help procurement teams identify relevant **Bureau of Indian Standards (BIS)** standards from real-world procurement requirements.

Procurement requirements are normally written in natural, practical language, while BIS standards use technical and highly specific terminology. This creates a gap between what a procurement team needs and how standards are described.

Syncronal bridges this gap using **Natural Language Processing, Semantic Search, FAISS Vector Retrieval, BIS Hybrid Ranking, Lifecycle Validation, and Document Intelligence**.

The system accepts either a natural-language procurement requirement or an uploaded procurement document and returns a ranked list of relevant BIS standards.

---

## Problem

Finding the right BIS standard for a procurement requirement can require searching through multiple standards and determining which one is actually applicable.

The challenge becomes harder when:

- The requirement is written in natural language.
- BIS standards use technical terminology.
- Multiple standards appear semantically relevant.
- Standards may have different lifecycle statuses.
- Users may need to understand related or referred standards.
- Procurement documents can contain much more information than a simple keyword query.

Syncronal addresses this problem by converting the procurement requirement into a machine-understandable semantic representation and ranking BIS standards according to relevance and BIS-specific information.

---

## Proposed Solution

```text
Procurement Requirement
        |
        v
Input Validation
        |
        v
Text / PDF / DOCX / TXT
        |
        v
Semantic Understanding
        |
        v
Sentence Transformer
all-MiniLM-L6-v2
        |
        v
384-D Embeddings
        |
        v
FAISS Vector Retrieval
        |
        v
Top Candidate Standards
        |
        v
BIS Hybrid Ranking
        |
        v
Lifecycle Validation
        |
        v
Top Relevant BIS Standards
        |
        v
Related / Referred Standards
        |
        v
Explanation + Official BIS Links
