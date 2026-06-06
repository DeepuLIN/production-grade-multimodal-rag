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
![Status](https://img.shields.io/badge/Status-Production%20MVP-success)

A production-grade multimodal Retrieval-Augmented Generation (RAG) platform designed for intelligent document understanding, knowledge retrieval, and question answering across PDFs, scanned documents, images, and mixed-content files.

The system combines OCR, image understanding, hybrid retrieval, vector search, metadata filtering, and cloud-native deployment to provide a scalable document intelligence platform.

The platform supports multimodal document ingestion, hybrid retrieval, neural reranking, secure multi-tenant access, and cloud-native deployment on AWS.

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

* Amazon Titan Embedding Search
* BM25 Keyword Search
* Hybrid Retrieval
* Reciprocal Rank Fusion (RRF)
* Query Rewriting
* Cross-Encoder Reranking
* Metadata Filtering
* Project-Level Isolation
* Retrieval Inspector
* Source Attribution

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
FastAPI Backend (AWS Lambda Container)
 │
 ├─────────────────────────────────────────────┐
 │                                             │
 ▼                                             ▼
PostgreSQL (metadata)                     Amazon S3 (raw files)
 │                                             │
 │                                             ▼
 │                                    Large Document Storage
 │                                             │
 │                                             ▼
 │                              OCR / Multimodal Processing
 │                              (Lambda-compatible async flow)
 │                                             │
 └──────────────────────────────┬──────────────┘
                                │
                                ▼
                     Document Processing Pipeline
                                │
     ┌──────────────────────────┼──────────────────────────┐
     ▼                          ▼                          ▼
 OCR Extraction         Image Processing         Markdown Builder
                                │
                                ▼
                    Markdown-Aware Chunking
                                │
                                ▼
                      Amazon Titan Embeddings
                                │
                                ▼
                       Qdrant Vector Storage
                                │
────────────────────────────────────────────────────────────

                      Question Answering Flow

                                │
                                ▼
                          User Query
                                │
                                ▼
                         Query Rewriting
                                │
                                ▼
             ┌──────────────────┴──────────────────┐
             ▼                                     ▼

      Vector Search                        BM25 Search
        (Qdrant)                         (Keyword Index)

             ▼                                     ▼
             └──────────────────┬──────────────────┘
                                │
                                ▼
                  Reciprocal Rank Fusion (RRF)
                                │
                                ▼
                    Candidate Pool Generation
                           (20–32 chunks)
                                │
                                ▼
                    Cross-Encoder Reranking
                                │
                                ▼
                     Top-K Relevant Chunks
                                │
                                ▼
                      Context Assembly Layer
                                │
                                ▼
                   LLM Generation (OpenRouter)
                                │
                                ▼
                    Streaming Response to UI
```



# Enterprise Retrieval Pipeline

The retrieval system follows a modern production-grade architecture rather than relying solely on vector similarity search.

```text
Query
  ↓
Query Rewriting
  ↓
Vector Search (Titan + Qdrant)
      +
BM25 Retrieval
  ↓
Reciprocal Rank Fusion (RRF)
  ↓
Candidate Pool Generation
  ↓
Cross-Encoder Reranking
  ↓
Context Assembly
  ↓
LLM Generation
```

This design combines semantic retrieval, lexical retrieval, rank fusion, and neural reranking to improve retrieval precision and answer grounding across long and complex documents.


# Technology Stack

## Frontend

* ![Next.js](https://img.shields.io/badge/-Next.js-black?logo=next.js&style=flat-square) Next.js 15
* ![React](https://img.shields.io/badge/-React-61DAFB?logo=react&style=flat-square) React
* ![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?logo=typescript&style=flat-square) TypeScript
* ![Tailwind](https://img.shields.io/badge/-Tailwind-06B6D4?logo=tailwindcss&style=flat-square) Tailwind CSS
* ![Clerk](https://img.shields.io/badge/-Clerk-6C47FF?style=flat-square) Clerk Authentication
* ![Vercel](https://img.shields.io/badge/-Vercel-black?logo=vercel&style=flat-square) Vercel

## Backend

* ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&style=flat-square) FastAPI
* ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&style=flat-square) Python 3.13
* ![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-D71F00?style=flat-square) SQLAlchemy
* ![PyMuPDF](https://img.shields.io/badge/-PyMuPDF-4B4B4B?style=flat-square) PyMuPDF
* ![OCR](https://img.shields.io/badge/-OCR-4285F4?style=flat-square) OCR Pipeline

## AI / RAG

* ![Titan](https://img.shields.io/badge/-Titan_Text_Embeddings-FF9900?logo=amazonaws&style=flat-square) Amazon Titan Embeddings
* ![BM25](https://img.shields.io/badge/-BM25_Search-blue?style=flat-square) BM25 Retrieval
* ![Hybrid Retrieval](https://img.shields.io/badge/-Hybrid_Retrieval-green?style=flat-square) Hybrid Retrieval
* ![RRF](https://img.shields.io/badge/-RRF-orange?style=flat-square) Reciprocal Rank Fusion (RRF)
* ![Cross Encoder](https://img.shields.io/badge/-Cross_Encoder_Reranking-red?style=flat-square) Cross-Encoder Reranking
* ![Query Rewriting](https://img.shields.io/badge/-Query_Rewriting-purple?style=flat-square) Query Rewriting
* ![Markdown](https://img.shields.io/badge/-Markdown_Chunking-black?logo=markdown&style=flat-square) Markdown-Aware Chunking
* ![OCR](https://img.shields.io/badge/-Diagram_Aware_OCR-blue?style=flat-square) Diagram-Aware OCR
* ![Inspector](https://img.shields.io/badge/-Retrieval_Inspector-teal?style=flat-square) Retrieval Inspector
* ![OpenRouter](https://img.shields.io/badge/-OpenRouter-black?style=flat-square) OpenRouter LLM Gateway
* ![Amazon Bedrock](https://img.shields.io/badge/-Amazon_Bedrock-FF9900?logo=amazonaws&style=flat-square) Amazon Bedrock

## Data Layer

* ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?logo=postgresql&style=flat-square) PostgreSQL (Neon)
* ![Qdrant](https://img.shields.io/badge/-Qdrant-DC244C?style=flat-square) Qdrant Vector Database
* ![S3](https://img.shields.io/badge/-Amazon_S3-569A31?logo=amazons3&style=flat-square) Amazon S3

## Infrastructure

* ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&style=flat-square) Docker
* ![Lambda](https://img.shields.io/badge/-AWS_Lambda-FF9900?logo=awslambda&style=flat-square) AWS Lambda
* ![ECR](https://img.shields.io/badge/-AWS_ECR-FF9900?style=flat-square) AWS ECR
* ![Lambda Web Adapter](https://img.shields.io/badge/-Lambda_Web_Adapter-yellow?style=flat-square) Lambda Web Adapter
* ![Vercel](https://img.shields.io/badge/-Vercel-black?logo=vercel&style=flat-square) Vercel


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
* Diagram-Aware OCR
* Markdown Conversion
* Chunking Pipeline
* Amazon Titan Embeddings
* Qdrant Vector Storage
* PostgreSQL Metadata Storage
* Amazon S3 Storage
* Hybrid Retrieval
* Reciprocal Rank Fusion
* Streaming Responses

### Retrieval Inspector v1

* Retrieved Chunk Display
* Source Filename Display
* Chunk Index Display
* Vector Score Display
* BM25 Score Display
* RRF Score Display
* Retrieval Ranking Transparency
* Query Rewriting Visibility
* Automatic BM25 Rebuild from Qdrant after Lambda Cold Starts
* Hybrid Retrieval Debugging Support

### Cloud Deployment

* Docker Containerization
* AWS ECR
* AWS Lambda
* Amazon S3
* Neon PostgreSQL
* Qdrant
* Vercel Frontend Deployment

### Production Readiness

* Upload Validation
* Health Monitoring
* Container Security
* JWT Authentication
* User Isolation
* Project Isolation
* Production CORS Configuration


## Retrieval Quality

* Amazon Titan Embeddings
* Vector Retrieval
* BM25 Retrieval
* Hybrid Search
* Reciprocal Rank Fusion (RRF)
* Query Rewriting
* Cross-Encoder Reranking
* Candidate Pool Expansion
* Retrieval Inspector
* Source Attribution


### Retrieval Quality Improvements

The retrieval pipeline uses a cross-encoder reranking stage after hybrid retrieval.

Pipeline:

Vector Search
+
BM25 Search
↓
RRF Fusion
↓
Candidate Pool Generation
↓
Cross-Encoder Reranking
↓
Final Context Selection

This significantly improves retrieval precision compared to vector search alone by scoring query-document relevance jointly before context assembly.


---

# Release History

## v1.1.0 — Retrieval Inspector v1

### Features

* Added Retrieval Inspector panel
* Added vector score visibility
* Added BM25 score visibility
* Added RRF score visibility
* Added chunk index visibility
* Added source filename visibility
* Added hybrid retrieval transparency
* Added automatic BM25 rebuild from Qdrant for Lambda cold starts

---

## v1.0.0 — Production-Hardened MVP

### Features

* PDF Upload
* Image Upload
* OCR Processing
* Image Caption Processing
* Diagram-Aware OCR
* Markdown Conversion
* Chunking Pipeline
* Amazon Titan Embeddings
* Qdrant Integration
* PostgreSQL Integration
* S3 Storage
* Streaming Responses
* AWS Deployment
* Health Monitoring
* Upload Validation


---


## v1.2.0 — Hybrid Retrieval Complete

### Features

* BM25 Retrieval Integration
* Reciprocal Rank Fusion (RRF)
* Query Rewriting
* Retrieval Inspector
* Vector Score Visualization
* BM25 Score Visualization
* RRF Score Visualization
* Automatic BM25 Rebuild from Qdrant
* Lambda Cold-Start Recovery
* Hybrid Retrieval Debugging Support

---


## v1.3.0 — Retrieval Quality Upgrade

### Features

* Cross-Encoder Reranking
* Expanded Candidate Retrieval
* Cross-Encoder Reranking
* Improved Context Selection
* Better Answer Grounding
* Enhanced Retrieval Precision

### Improvements

* Increased retrieval candidate pool before reranking
* Improved ranking quality for long documents
* Reduced irrelevant chunk selection
* Improved multi-topic document retrieval

# Planned Roadmap

## v1.4.0 — Evaluation Dashboard

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





## v2.0.0 — Visual RAG

Goal: extend the current image-caption pipeline into true visual retrieval, where figures, diagrams, charts, and tables inside PDFs/images are extracted, indexed, and retrievable as first-class knowledge units.

Planned capabilities:

* Extract figures, diagrams, charts, and tables from PDFs/images
* Detect the surrounding section or paragraph where each visual element appears
* Generate visual captions and structured metadata for each extracted image region
* Store visual chunks separately from text chunks
* Link each visual chunk back to its source document, page, and surrounding text
* Support visual retrieval for questions about figures, diagrams, charts, and tables
* Add visual citations showing the source page and image region used in the answer

Possible approach:

```text
PDF / Image
    ↓
Page Rendering
    ↓
Visual Region Detection
    ↓
Figure / Table / Diagram Extraction
    ↓
Vision Model Captioning
    ↓
Visual Metadata Generation
    ↓
Visual Chunk Creation
    ↓
Embedding + Vector Storage
    ↓
Visual Retrieval
    ↓
Answer with Visual Citations
```

Research direction:

* Use multimodal models to identify and describe figures, diagrams, charts, and tables
* Explore image patching or region-based visual chunking inspired by Vision Transformer-style processing
* Combine visual chunks with nearby text chunks for better context-aware retrieval
* Evaluate whether visual embeddings, text captions, or hybrid image-text retrieval gives the best result


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
Markdown-Aware Chunking
      ↓
Vector Search + BM25
      ↓
RRF Fusion
      ↓
Cross-Encoder Reranking
      ↓
Context Assembly
      ↓
Streaming LLM Response
      ↓
AWS Cloud Deployment
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
* Retrieval Evaluation Dashboard
* Automated Benchmarking

---

# Author

**Deepak Lingaraju**



Machine Learning • Computer Vision • Multimodal AI • Retrieval-Augmented Generation • Cloud Engineering
