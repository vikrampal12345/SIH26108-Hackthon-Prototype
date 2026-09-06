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
