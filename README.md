<!-- SYNCRONAL — AI-Powered BIS Standard Recommendation System -->

<div align="center">

# SYNCRONAL

### AI-Powered BIS Standard Recommendation System

**From Procurement Requirements to Relevant BIS Standards**

<br>

<img src="https://img.shields.io/badge/SIH26108-Smart%20India%20Hackathon%202026-1f6feb?style=for-the-badge">
<img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white">
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white">
<img src="https://img.shields.io/badge/FAISS-Vector%20Search-1877F2?style=for-the-badge">
<img src="https://img.shields.io/badge/Sentence%20Transformers-NLP-orange?style=for-the-badge">
<img src="https://img.shields.io/badge/Playwright-Data%20Acquisition-2EAD33?style=for-the-badge&logo=playwright&logoColor=white">
<img src="https://img.shields.io/badge/Vercel-Frontend-000000?style=for-the-badge&logo=vercel&logoColor=white">
<img src="https://img.shields.io/badge/Azure-Backend-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white">

<br><br>

<a href="https://sih-26108-hackthon-prototype.vercel.app/">
<img src="https://img.shields.io/badge/LIVE%20PROTOTYPE-000000?style=for-the-badge">
</a>

<a href="https://github.com/vikrampal12345/SIH26108-Hackthon-Prototype">
<img src="https://img.shields.io/badge/GITHUB%20REPOSITORY-24292F?style=for-the-badge&logo=github&logoColor=white">
</a>

</div>

---

## SYNCRONAL

Syncronal is an AI-powered decision-support system developed for **Smart India Hackathon 2026 — SIH26108** to help procurement teams discover relevant **Bureau of Indian Standards (BIS)** standards from natural-language procurement requirements.

The system bridges the gap between **human procurement language** and the **technical terminology used by BIS standards**.

Users can enter a procurement requirement directly or upload a **PDF, DOCX, or TXT** document. Syncronal validates the input, understands its semantic meaning, retrieves relevant BIS standards, applies BIS-specific hybrid ranking and lifecycle validation, and presents ranked recommendations with related standards and official BIS references.

---

## THE PROBLEM

Procurement requirements are generally written in simple, practical language, while BIS standards contain technical and highly specific terminology.

Finding the most appropriate standards can therefore require:

- Searching with different keywords
- Reviewing multiple standards
- Comparing technically similar standards
- Checking the current status of standards
- Understanding certification requirements
- Identifying related or referred standards
- Interpreting technical terminology

The challenge is not simply finding a BIS standard. The challenge is identifying the standards that are **most relevant to the actual procurement requirement**.

---

## THE SOLUTION

Syncronal converts procurement requirements into semantic representations and compares them against a structured BIS standards knowledge base.

```text
Procurement Requirement
          ↓
Input Validation
          ↓
Text / PDF / DOCX / TXT
          ↓
Sentence Transformer
all-MiniLM-L6-v2
          ↓
384-D Embeddings
          ↓
FAISS Semantic Retrieval
          ↓
Top Candidate Standards
          ↓
BIS Hybrid Ranking
          ↓
Lifecycle Validation
          ↓
Top Relevant BIS Standards
          ↓
Related / Referred Standards
          ↓
Official BIS References


## HOW IT WORKS

### 1. BIS KNOWLEDGE BASE

The prototype contains approximately **3,896 BIS standards** with structured information such as:

* IS Number
* Standard Title
* Status
* Department
* Technical Committee
* Group
* Sub Group
* Sub-Sub Group
* Type of Standard
* Certification
* Relevant Ministries
* Revisions
* Amendments
* Reaffirmation Year
* Superseding Standard
* Official BIS Source URL

---

### 2. DATA ACQUISITION

BIS information is collected from official BIS sources using **Playwright-based browser automation**.

The acquired information is converted into a structured knowledge base for preprocessing, semantic search and recommendation.

---

### 3. DATA PREPROCESSING

The preprocessing pipeline handles:

* Missing values
* Status normalization
* Certification normalization
* Technical committee cleanup
* Standard type normalization
* Revision information
* Amendment information
* Reaffirmation information
* Superseding standards
* BIS classification information
* Search-text construction

A dedicated `search_text` field combines important BIS metadata to create a richer semantic representation of each standard.

---

### 4. SEMANTIC UNDERSTANDING

Syncronal uses the **Sentence Transformers `all-MiniLM-L6-v2`** model.

The model converts both the procurement requirement and BIS standards into **384-dimensional embedding vectors**.

This enables semantic comparison based on meaning rather than relying only on exact keyword matching.

```text
Procurement Requirement
          ↓
all-MiniLM-L6-v2
          ↓
384-Dimensional Vector
```

---

### 5. FAISS VECTOR RETRIEVAL

The generated embeddings are normalized and indexed using:

```text
FAISS IndexFlatIP
```

FAISS performs vector similarity search and retrieves the strongest semantic candidates.

Because the vectors are normalized, **inner product is equivalent to cosine similarity**.

```text
Query Vector
     ↓
FAISS Index
     ↓
Top-K Semantic Candidates
```

---

### 6. BIS HYBRID RANKING

Semantic similarity alone is not sufficient for procurement-oriented recommendations.

Syncronal therefore combines semantic similarity with structured BIS information.

The current prototype uses:

```text
Final Score =
0.70 × Semantic Similarity
+ 0.15 × Classification Similarity
+ 0.10 × Status Score
+ 0.05 × Certification Score
```

The ranking considers:

* Semantic similarity
* BIS classification similarity
* Standard status
* Certification information

This creates a **BIS Hybrid Ranking** layer on top of semantic retrieval.

---

### 7. LIFECYCLE VALIDATION

A semantically similar standard should not automatically become a primary recommendation if it is no longer active.

Syncronal applies lifecycle validation after ranking.

The current prototype:

* Removes withdrawn standards from primary recommendations
* Retains superseding-standard information
* Uses standard status as a ranking signal
* Helps distinguish active standards from withdrawn standards

```text
Semantic Relevance
        +
BIS Metadata
        ↓
Hybrid Ranking
        ↓
Lifecycle Validation
        ↓
Final Recommendations
```

---

### 8. RELATED AND REFERRED STANDARDS

BIS standards can reference other standards.

Syncronal maintains a separate relationship dataset containing approximately **31,981 standard relationships**.

The system identifies:

* **Referred In Standards**
* **Referred By Standards**

These relationships are shown separately from the primary recommendations because a related standard is not necessarily the best direct procurement recommendation.

---

## DOCUMENT INTELLIGENCE

Syncronal supports multiple input formats:

```text
Plain Text
PDF
DOCX
TXT
```

For uploaded documents, the system:

```text
Document Upload
      ↓
Text Extraction
      ↓
Input Validation
      ↓
Semantic Processing
      ↓
FAISS Retrieval
      ↓
Hybrid Ranking
      ↓
Recommendations
```

The prototype uses:

* `pypdf` for PDF extraction
* `python-docx` for DOCX extraction
* Text decoding for TXT files

---

## INPUT VALIDATION

Syncronal validates the incoming requirement before performing recommendation.

The validation layer identifies whether the input appears to represent a procurement or BIS-related requirement.

Clearly unrelated content such as:

* Resumes
* Unrelated documents
* Non-procurement text

can be rejected before entering the recommendation pipeline.

This prevents irrelevant inputs from producing misleading BIS recommendations.

---

## KEY FEATURES

| Feature                 | Description                                               |
| ----------------------- | --------------------------------------------------------- |
| Natural Language Search | Search BIS standards using practical procurement language |
| Document Upload         | Process PDF, DOCX and TXT requirements                    |
| Semantic Search         | Understand meaning beyond exact keywords                  |
| 384-D Embeddings        | Represent requirements and standards in vector space      |
| FAISS Retrieval         | Retrieve high-similarity candidate standards              |
| BIS Hybrid Ranking      | Combine semantic and BIS-specific signals                 |
| Lifecycle Validation    | Remove withdrawn standards from primary results           |
| Certification Awareness | Consider certification information                        |
| Related Standards       | Show referred-in and referred-by relationships            |
| Input Validation        | Reject clearly unrelated requirements                     |
| Official BIS References | Provide source information and BIS links                  |
| Ranked Recommendations  | Present relevant standards in ranked order                |

---

## SYSTEM ARCHITECTURE

```text
                       BIS OFFICIAL SOURCES
                                ↓
                       Playwright Acquisition
                                ↓
                        Data Preprocessing
                                ↓
                    BIS Standards Knowledge Base
                                ↓
                    Sentence Transformer Model
                       all-MiniLM-L6-v2
                                ↓
                         384-D Embeddings
                                ↓
                           FAISS Index
                                ↑
                                |
USER → Frontend → FastAPI Backend
                       ↓
                 Input Validation
                       ↓
                  Query Embedding
                       ↓
                  FAISS Retrieval
                       ↓
                BIS Hybrid Ranking
                       ↓
               Lifecycle Validation
                       ↓
             Related Standards Layer
                       ↓
              Ranked Recommendations
                       ↓
              Official BIS References
```

---

## TECHNOLOGY STACK

| Layer               | Technology                  |
| ------------------- | --------------------------- |
| Frontend            | HTML, CSS, JavaScript       |
| Backend             | FastAPI                     |
| API Server          | Uvicorn                     |
| Programming         | Python 3.11                 |
| NLP                 | Sentence Transformers       |
| Embedding Model     | all-MiniLM-L6-v2            |
| Embedding Dimension | 384                         |
| Vector Search       | FAISS                       |
| Data Processing     | Pandas, NumPy, scikit-learn |
| Data Acquisition    | Playwright                  |
| PDF Processing      | pypdf                       |
| DOCX Processing     | python-docx                 |
| Backend Deployment  | Azure App Service           |
| Frontend Deployment | Vercel                      |
| Version Control     | Git + GitHub                |

---

## PROJECT STRUCTURE

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
│   ├── classification.csv
│   └── relationships.csv
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

## API ENDPOINTS

```text
GET  /
GET  /health
POST /recommend
POST /recommend-document
```

### `/recommend`

Accepts a natural-language procurement requirement and returns ranked BIS standard recommendations.

### `/recommend-document`

Accepts a PDF, DOCX or TXT procurement document, extracts its content and processes it through the recommendation pipeline.

---

## DEPLOYMENT ARCHITECTURE

```text
                         USER
                          ↓
                  Vercel Frontend
                          ↓
                 Azure App Service
                          ↓
                   FastAPI Backend
                          ↓
              ┌───────────┴───────────┐
              ↓                       ↓
         FAISS Index            BIS Knowledge Base
              ↓
      Sentence Transformer
```

**Frontend:** Vercel
**Backend:** Microsoft Azure App Service
**Repository:** GitHub

---

## LIVE PROTOTYPE

<div align="center">

<a href="https://sih-26108-hackthon-prototype.vercel.app/">
<img src="https://img.shields.io/badge/OPEN%20SYNCRONAL%20LIVE-000000?style=for-the-badge">
</a>

</div>

---

## RESEARCH & REFERENCES

The project was developed using official BIS resources, technical documentation, research material, tutorials and practical experimentation.

### Primary Data Source

* Bureau of Indian Standards
* BIS Standards Portal
* BIS Know Your Standard

### Technical References

* Sentence Transformers documentation
* FAISS documentation
* FastAPI documentation
* Playwright documentation
* Azure App Service documentation
* Vercel documentation
* Python documentation
* Pandas documentation
* NumPy documentation
* scikit-learn documentation
* Google technical resources
* YouTube technical lectures and tutorials
* Research papers and technical examples

### AI-Assisted Development

AI tools were used as research and development accelerators for:

* Technical research
* Concept understanding
* Architecture exploration
* Coding assistance
* Debugging
* Data preprocessing
* Machine-learning implementation
* Documentation
* Testing
* Presentation preparation

Tools used include:

* ChatGPT
* Claude
* Google Gemini
* Perplexity
* GitHub Copilot
* Notion AI

The team reviewed and understood the implementation and technical decisions rather than relying on AI-generated output without verification.

---

## CURRENT PROTOTYPE

Syncronal currently demonstrates an end-to-end working prototype containing:

```text
BIS Data Acquisition
        ↓
Data Preprocessing
        ↓
BIS Knowledge Base
        ↓
Semantic Embeddings
        ↓
FAISS Vector Search
        ↓
BIS Hybrid Ranking
        ↓
Lifecycle Validation
        ↓
Related Standards
        ↓
FastAPI Backend
        ↓
Web Frontend
        ↓
Cloud Deployment
```

---

## LIMITATIONS

Syncronal is currently a **working prototype** and should not be treated as a production-grade automated procurement decision system.

Current limitations include:

* Ranking weights are manually configured.
* Semantic similarity does not guarantee technical or legal applicability.
* Specialized standards can sometimes rank above more directly applicable standards.
* The prototype knowledge base is not yet continuously synchronized with BIS.
* Lifecycle intelligence can be expanded further.
* Domain-specific ranking can be improved using larger validated datasets.
* Final procurement decisions should be reviewed by qualified technical and procurement personnel.

---

## FUTURE SCOPE

Future development can include:

* Continuous BIS data synchronization
* Domain-specific ranking models
* Learning-to-rank
* Improved lifecycle and supersession intelligence
* Explainable recommendations
* Standard dependency graphs
* Advanced document understanding
* User authentication
* User search history
* Saved recommendations
* Procurement workflow integration
* Enterprise dashboards
* Feedback-based ranking improvement
* Production-scale infrastructure

---

## PROJECT VISION

Syncronal aims to make BIS standard discovery **faster, more intelligent and easier to navigate**.

The system acts as a decision-support layer between procurement requirements and BIS standards.

```text
Human Requirement
        ↓
Semantic Understanding
        ↓
BIS Knowledge
        ↓
Intelligent Retrieval
        ↓
BIS Hybrid Ranking
        ↓
Lifecycle Validation
        ↓
Relevant BIS Standards
```

The goal is simple:

**Help procurement teams move from what they need to the BIS standards most relevant to that requirement.**

---

<div align="center">

# SYNCRONAL

### Intelligent Discovery of BIS Standards

**SIH26108 | Smart India Hackathon 2026**

<br>

<a href="https://sih-26108-hackthon-prototype.vercel.app/">
<b>LIVE PROTOTYPE</b>
</a>

  |  

<a href="https://github.com/vikrampal12345/SIH26108-Hackthon-Prototype">
<b>GITHUB REPOSITORY</b>
</a>

<br><br>

**From Procurement Requirements to Relevant BIS Standards**

</div>
```