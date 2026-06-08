"use client";

import Link from "next/link";
import {
  SignInButton,
  SignedIn,
  SignedOut,
  UserButton,
  useUser,
} from "@clerk/nextjs";

const ALLOWED_DEMO_EMAILS = ["deepak.ai.projects@gmail.com"];

export default function Home() {
  const { user, isLoaded } = useUser();

  const userEmail = user?.primaryEmailAddress?.emailAddress?.toLowerCase();

  const isAllowedDemoUser =
    !!userEmail && ALLOWED_DEMO_EMAILS.includes(userEmail);

  const signedInButBlocked = isLoaded && user && !isAllowedDemoUser;

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-white">
      <div className="container mx-auto px-4 py-10">
        <nav className="mb-20 flex items-center justify-between">
          <h1 className="text-2xl font-bold tracking-tight">
            Multimodal RAG Platform
          </h1>

          <div>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="rounded-xl bg-blue-600 px-6 py-2 font-medium text-white shadow-lg shadow-blue-900/30 transition-all hover:bg-blue-700">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>

            <SignedIn>
              <div className="flex items-center gap-4 rounded-xl border border-white/10 bg-white/10 px-3 py-2 shadow-sm backdrop-blur">
                {isAllowedDemoUser ? (
                  <Link
                    href="/product"
                    className="rounded-xl bg-blue-600 px-6 py-2 font-medium text-white shadow-lg shadow-blue-900/30 transition-all hover:bg-blue-700"
                  >
                    Go to App
                  </Link>
                ) : (
                  <span className="rounded-xl border border-red-400/40 bg-red-500/10 px-4 py-2 text-sm text-red-200">
                    Private demo
                  </span>
                )}

                <UserButton showName={true} />
              </div>
            </SignedIn>
          </div>
        </nav>

        {signedInButBlocked && (
          <section className="mx-auto mb-12 max-w-2xl rounded-3xl border border-red-400/30 bg-red-500/10 p-8 text-center shadow-2xl">
            <h2 className="mb-3 text-3xl font-bold text-red-100">
              Private Recruiter Demo
            </h2>
            <p className="text-slate-300">
              This demo is restricted. Please use the provided recruiter demo
              account to access the application.
            </p>
          </section>
        )}

        <section className="py-20 text-center">
          <div className="mb-8 inline-flex items-center rounded-full border border-blue-400/30 bg-blue-500/10 px-4 py-2 text-sm text-blue-200">
            AWS deployed • OCR • Figures • Tables • Hybrid retrieval • Reranking
          </div>

          <h2 className="mb-6 text-5xl font-bold leading-tight md:text-7xl">
            Production-Grade
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-emerald-300 bg-clip-text text-transparent">
              Multimodal RAG Platform
            </span>
          </h2>

          <p className="mx-auto mb-10 max-w-3xl text-lg leading-relaxed text-slate-300 md:text-xl">
            A secure AI knowledge platform for PDFs, research papers, scanned
            documents, figures, tables, diagrams, and technical content. It
            combines OCR, visual extraction, hybrid search, reranking, streaming
            answers, and project-level document comparison.
          </p>

          <div className="mx-auto mb-12 grid max-w-6xl gap-5 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/10 p-6 text-left backdrop-blur">
              <h3 className="mb-3 text-xl font-semibold">
                Multimodal Document Ingestion
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Upload PDFs and images, extract text with OCR, render page
                images, detect visual content, caption figures, extract tables,
                and convert documents into Markdown-aware RAG chunks.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/10 p-6 text-left backdrop-blur">
              <h3 className="mb-3 text-xl font-semibold">
                Figure & Table Retrieval
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Ask questions like “show Figure 6” or “explain Table 2” and
                retrieve visual/page-image sources, extracted table chunks,
                captions, metadata, and grounded explanations.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/10 p-6 text-left backdrop-blur">
              <h3 className="mb-3 text-xl font-semibold">
                Hybrid Retrieval Engine
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Combines Amazon Titan embeddings, Qdrant vector search, BM25
                keyword search, metadata filters, RRF fusion, and reranking for
                accurate document-grounded answers.
              </p>
            </div>
          </div>

          <div className="mx-auto mb-12 grid max-w-6xl gap-5 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6 text-left">
              <h3 className="mb-3 text-xl font-semibold">
                Cross-Document Reasoning
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Compare multiple documents, summarize all documents in a project,
                identify shared themes.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6 text-left">
              <h3 className="mb-3 text-xl font-semibold">
                Retrieval Inspector
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Inspect top matches with vector scores, BM25 scores, RRF scores,
                chunk types, pages, document IDs, and retrieved source snippets
                for transparent debugging.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6 text-left">
              <h3 className="mb-3 text-xl font-semibold">
                Secure Cloud Architecture
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Built with Next.js, FastAPI, AWS Lambda, Amazon S3, PostgreSQL,
                Qdrant, Clerk authentication, Docker, Vercel, and production
                upload validation.
              </p>
            </div>
          </div>

          <div className="mx-auto mb-10 max-w-4xl rounded-3xl border border-white/10 bg-slate-900/80 p-8 shadow-2xl">
            <h3 className="mb-5 text-2xl font-bold">Core Capabilities</h3>

            <div className="grid gap-3 text-left text-slate-300 md:grid-cols-2">
              <p>✓ PDF, image, and scanned document upload</p>
              <p>✓ OCR text extraction and cleanup</p>
              <p>✓ Markdown-based document representation</p>
              <p>✓ Markdown-aware chunking</p>
              <p>✓ Figure and page-image captioning</p>
              <p>✓ Table extraction with table images</p>
              <p>✓ Figure/table-aware retrieval routing</p>
              <p>✓ Amazon Titan embedding model</p>
              <p>✓ Qdrant vector database</p>
              <p>✓ BM25 keyword retrieval</p>
              <p>✓ RRF hybrid ranking</p>
              <p>✓ Cross-encoder reranking</p>
              <p>✓ Project and document isolation</p>
              <p>✓ Cross-document summaries and comparison</p>
              <p>✓ Streaming LLM responses</p>
              <p>✓ Retrieval Inspector for debugging</p>
              <p>✓ PostgreSQL metadata layer</p>
              <p>✓ Amazon S3 document and image storage</p>
              <p>✓ Clerk authentication</p>
              <p>✓ AWS Lambda deployment</p>
              <p>✓ Health endpoints and upload safety checks</p>
              <p>✓ Private recruiter demo access</p>
            </div>
          </div>

          <div className="mx-auto mb-12 max-w-4xl rounded-3xl border border-cyan-400/20 bg-cyan-500/10 p-8 text-left">
            <h3 className="mb-4 text-2xl font-bold text-cyan-100">
              Example Questions
            </h3>

            <div className="grid gap-3 text-sm text-slate-300 md:grid-cols-2">
               <p>“Show Figure 6 from this document.”</p>
               <p>“Explain Table 2 from the uploaded file.”</p>
               <p>“Compare all documents in this project.”</p>
               <p>“Summarize the uploaded notes.”</p>
               <p>“What are the main differences between these documents?”</p>
               <p>“Extract the key points from this scanned page.”</p>
            </div>
          </div>

          <SignedOut>
            <SignInButton mode="modal">
              <button className="rounded-2xl bg-blue-600 px-10 py-4 text-lg font-bold text-white shadow-lg shadow-blue-900/40 transition-all duration-300 hover:scale-105 hover:bg-blue-700">
                Explore Platform
              </button>
            </SignInButton>
          </SignedOut>

          <SignedIn>
            {isAllowedDemoUser ? (
              <Link href="/product">
                <button className="rounded-2xl bg-blue-600 px-10 py-4 text-lg font-bold text-white shadow-lg shadow-blue-900/40 transition-all duration-300 hover:scale-105 hover:bg-blue-700">
                  Launch Application
                </button>
              </Link>
            ) : (
              <button
                disabled
                className="cursor-not-allowed rounded-2xl bg-slate-700 px-10 py-4 text-lg font-bold text-slate-300 opacity-70"
              >
                Use Provided Demo Account
              </button>
            )}
          </SignedIn>
        </section>
      </div>
    </main>
  );
}