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
