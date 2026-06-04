# NoteVision AI

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-blue?logo=postgresql)
![Qdrant](https://img.shields.io/badge/Qdrant-VectorDB-red)
![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange?logo=awslambda)
![Amazon S3](https://img.shields.io/badge/AWS-S3-orange?logo=amazons3)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)
![Vercel](https://img.shields.io/badge/Vercel-Frontend-black?logo=vercel)
![Clerk](https://img.shields.io/badge/Auth-Clerk-purple)
![OpenRouter](https://img.shields.io/badge/LLM-OpenRouter-black)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-MVP%20Complete-success)

A production-grade multimodal Retrieval-Augmented Generation (RAG) platform designed for intelligent document understanding, knowledge retrieval, and question answering across PDFs, scanned documents, images, and mixed-content files.

The system combines OCR, image understanding, hybrid retrieval, vector search, metadata filtering, and cloud-native deployment to provide a scalable document intelligence platform.

---

# Overview

Traditional RAG systems are typically limited to plain text documents and simple vector search.

This project extends the architecture into a production-oriented multimodal platform capable of:

* Processing PDFs and images
* Extracting OCR text
* Understanding embedded figures and diagrams
* Converting documents into structured Markdown
* Performing hybrid retrieval
* Supporting secure multi-user environments
* Running on cloud-native infrastructure

---

# Key Features

## Document Ingestion

* PDF Upload
* Image Upload
* OCR Extraction
* Metadata Extraction
* Markdown Generation
* Document Storage

## Multimodal Understanding

* OCR for scanned PDFs
* Image Caption Generation
* Visual Content Processing
* Markdown-based document representation

## Retrieval Pipeline

* Semantic Search
* Vector Retrieval
* Metadata Filtering
* Project-Level Isolation
* Hybrid Retrieval
* Reciprocal Rank Fusion (RRF)

## Authentication & Security

* Clerk Authentication
* JWT Validation
* User Isolation
* Project Isolation
* Upload Validation
* Secure Cloud Storage

## Production Infrastructure

* Dockerized Deployment
* AWS Lambda Containers
* AWS ECR
* Amazon S3
* PostgreSQL Metadata Layer
* Qdrant Vector Database
* Health Monitoring Endpoints

---

# System Architecture

```text
User
 │
 ▼
Next.js Frontend
 │
 ▼
Clerk Authentication
 │
 ▼
FastAPI Backend
 │
 ├── OCR Pipeline
 ├── Image Processing Pipeline
 ├── Retrieval Pipeline
 └── LLM Pipeline
 │
 ├── PostgreSQL
 ├── Qdrant
 └── Amazon S3
 │
 ▼
Streaming Response
```

---

# Document Processing Pipeline

```text
Document Upload
        │
        ▼
OCR Extraction
        │
        ▼
Image Processing
        │
        ▼
Markdown Generation
        │
        ▼
Chunking
        │
        ▼
Embedding Generation
        │
        ▼
Qdrant Storage
```

---

# Retrieval Pipeline

```text
User Question
        │
        ▼
Query Processing
        │
        ▼
Vector Retrieval
        │
        ▼
Metadata Filtering
        │
        ▼
Hybrid Search
        │
        ▼
RRF Fusion
        │
        ▼
Context Assembly
        │
        ▼
LLM Response Generation
        │
        ▼
Streaming Answer
```

---

# Technology Stack

## Frontend

* Next.js 15
* React
* TypeScript
* Tailwind CSS
* Clerk Authentication
* Vercel

## Backend

* FastAPI
* Python 3.13
* SQLAlchemy
* PyMuPDF
* OCR Pipeline

## AI / RAG

* OpenRouter
* Embedding Models
* Hybrid Retrieval
* Reciprocal Rank Fusion (RRF)
* Markdown Chunking

## Data Layer

* PostgreSQL (Neon)
* Qdrant Vector Database
* Amazon S3

## Infrastructure

* Docker
* AWS Lambda
* AWS ECR
* Lambda Web Adapter
* Vercel

---

# Production Hardening

Implemented production-oriented improvements:

## Container Security

* Docker Base Image Updates
* Vulnerability Remediation
* Reduced Attack Surface

## Upload Safety

* PDF Size Limits
* Image Size Limits
* File Type Validation
* Content Type Validation

## Health Monitoring

```text
/health
/health/db
/health/qdrant
/health/s3
```

Verified Health Checks:

* API Status
* Database Connectivity
* Vector Database Connectivity
* S3 Connectivity

---

# Current MVP Status

## Completed

### Core Platform

* User Authentication
* Multi-Project Support
* Document Upload
* OCR Pipeline
* Image Understanding
* Markdown Conversion
* Chunking Pipeline
* Vector Storage
* Hybrid Retrieval
* Streaming Responses

### Cloud Deployment

* Docker Containerization
* AWS ECR
* AWS Lambda
* Amazon S3
* Neon PostgreSQL
* Qdrant

### Production Readiness

* Upload Validation
* Health Monitoring
* Container Security
* JWT Authentication
* User Isolation

---

# Release History

## v1.0.0 — Production-Hardened MVP

### Features

* PDF Upload
* Image Upload
* OCR Processing
* Image Caption Processing
* Markdown Conversion
* Chunking Pipeline
* Qdrant Integration
* PostgreSQL Integration
* S3 Storage
* Streaming Responses
* AWS Deployment
* Health Monitoring
* Upload Validation

---

# Planned Roadmap

## v1.1.0 — Retrieval Inspector

Visualize:

* Retrieved Chunks
* Chunk Ranking
* Vector Scores
* RRF Scores
* Final Context

---

## v1.2.0 — Evaluation Dashboard

Metrics:

* Recall@K
* Precision@K
* MRR
* nDCG
* Faithfulness
* Answer Relevance
* Context Relevance
* LLM-as-a-Judge

---

## v1.3.0 — Retrieval Quality

* Cross Encoder Reranking
* Improved Hybrid Search
* Query Rewriting

---

## v2.0.0 — Visual RAG

* Figure Retrieval
* Table Retrieval
* Diagram Understanding
* Visual Citations

---

## v3.0.0 — Agentic RAG

* Router Agent
* Verification Agent
* Retrieval Agents
* Tool-Based Reasoning

---

# Why This Project Matters

Most publicly available RAG projects stop at:

```text
Document
   ↓
Embedding
   ↓
Vector Search
   ↓
Answer
```

This project extends the architecture into a production-oriented multimodal system:

```text
PDF / Image
      ↓
OCR + Visual Understanding
      ↓
Markdown Conversion
      ↓
Chunking
      ↓
Hybrid Retrieval
      ↓
Metadata Filtering
      ↓
Cloud Infrastructure
      ↓
Streaming Answer
```

The objective is to demonstrate how modern enterprise-grade Retrieval-Augmented Generation systems can be designed, deployed, monitored, and scaled in real-world environments.

---

# Future Infrastructure Improvements

* GitHub Actions CI/CD
* Terraform Infrastructure as Code
* CloudWatch Monitoring
* Automated Deployments
* S3 Presigned Uploads
* Multi-Tenant Access Controls

---

# Author

**Deepak Lingaraju**

M.Sc. Mechatronics
University of Duisburg-Essen

Machine Learning • Computer Vision • Multimodal AI • Retrieval-Augmented Generation • Cloud Engineering
