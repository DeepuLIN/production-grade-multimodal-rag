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
            PDFs • Scanned Docs • Images • Figures • Diagrams • Hybrid RAG
          </div>

          <h2 className="mb-6 text-5xl font-bold leading-tight md:text-7xl">
            AI Search for
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-emerald-300 bg-clip-text text-transparent">
              Documents & Images
            </span>
          </h2>

          <p className="mx-auto mb-10 max-w-3xl text-lg leading-relaxed text-slate-300 md:text-xl">
            Upload PDFs, scanned documents, images, research papers, manuals,
            reports, and technical files. Ask questions, retrieve grounded
            answers, inspect sources, and understand both text and visual
            content using a production-grade multimodal RAG pipeline.
          </p>

          <div className="mb-14 flex flex-wrap justify-center gap-3 text-sm text-slate-300">
            <span className="rounded-full border border-white/10 bg-white/10 px-4 py-2">
              Amazon Titan Embeddings
            </span>
            <span className="rounded-full border border-white/10 bg-white/10 px-4 py-2">
              Qdrant Vector Search
            </span>
            <span className="rounded-full border border-white/10 bg-white/10 px-4 py-2">
              BM25 Retrieval
            </span>
            <span className="rounded-full border border-white/10 bg-white/10 px-4 py-2">
              RRF Fusion
            </span>
            <span className="rounded-full border border-white/10 bg-white/10 px-4 py-2">
              Reranking
            </span>
            <span className="rounded-full border border-white/10 bg-white/10 px-4 py-2">
              Visual Retrieval
            </span>
          </div>

          <div className="mx-auto mb-12 grid max-w-6xl gap-5 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/10 p-6 text-left backdrop-blur">
              <h3 className="mb-3 text-xl font-semibold">
                Document Intelligence
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Process native PDFs, scanned PDFs, images, handwritten notes,
                reports, and research papers with OCR, metadata storage, and
                Markdown-based document representation.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/10 p-6 text-left backdrop-blur">
              <h3 className="mb-3 text-xl font-semibold">
                Multimodal Understanding
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Understand embedded figures, diagrams, charts, visual regions,
                and page images using image captioning, diagram-aware OCR, and
                visual chunk creation.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/10 p-6 text-left backdrop-blur">
              <h3 className="mb-3 text-xl font-semibold">
                Grounded Answers
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Ask questions and receive source-grounded answers with retrieved
                text chunks, visual sources, page references, filenames, and
                transparent retrieval evidence.
              </p>
            </div>
          </div>

          <div className="mx-auto mb-12 grid max-w-6xl gap-5 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6 text-left">
              <h3 className="mb-3 text-xl font-semibold">
                Hybrid Retrieval Engine
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Combines semantic search with Amazon Titan embeddings, Qdrant
                vector search, BM25 keyword retrieval, Reciprocal Rank Fusion,
                and reranking for stronger retrieval accuracy.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6 text-left">
              <h3 className="mb-3 text-xl font-semibold">
                Retrieval Inspector
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Inspect vector scores, BM25 scores, RRF scores, chunk ranks,
                source filenames, chunk types, pages, and retrieval metadata for
                transparent debugging.
              </p>
            </div>

            <div className="rounded-2xl border border-white/10 bg-slate-900/70 p-6 text-left">
              <h3 className="mb-3 text-xl font-semibold">
                Secure Cloud Platform
              </h3>
              <p className="text-sm leading-relaxed text-slate-300">
                Built with Clerk authentication, JWT validation, user isolation,
                project isolation, upload validation, AWS Lambda, S3,
                PostgreSQL, Qdrant, Docker, and Vercel.
              </p>
            </div>
          </div>

          <div className="mx-auto mb-12 max-w-5xl rounded-3xl border border-cyan-400/20 bg-cyan-500/10 p-8 text-left shadow-2xl">
            <h3 className="mb-5 text-2xl font-bold text-cyan-100">
              How the Retrieval Pipeline Works
            </h3>

            <div className="grid gap-4 text-sm text-slate-300 md:grid-cols-2">
              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
                <p className="font-semibold text-white">1. Query Rewriting</p>
                <p className="mt-2">
                  User questions are rewritten into clearer retrieval queries
                  before searching the document collection.
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
                <p className="font-semibold text-white">
                  2. Vector + Keyword Search
                </p>
                <p className="mt-2">
                  Titan embeddings and Qdrant handle semantic search, while BM25
                  captures exact terms, filenames, concepts, and keywords.
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
                <p className="font-semibold text-white">
                  3. RRF Fusion + Reranking
                </p>
                <p className="mt-2">
                  Reciprocal Rank Fusion merges retrieval signals, and reranking
                  improves final context quality before answer generation.
                </p>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
                <p className="font-semibold text-white">
                  4. Source-Grounded Answer
                </p>
                <p className="mt-2">
                  The answer is generated using the selected text and visual
                  chunks, with source attribution and retrieved evidence.
                </p>
              </div>
            </div>
          </div>

          <div className="mx-auto mb-12 max-w-5xl rounded-3xl border border-white/10 bg-slate-900/80 p-8 shadow-2xl">
            <h3 className="mb-5 text-2xl font-bold">
              Core Product Capabilities
            </h3>

            <div className="grid gap-3 text-left text-slate-300 md:grid-cols-2">
              <p>✓ PDF, scanned document, and image upload</p>
              <p>✓ OCR extraction for scanned files</p>
              <p>✓ Diagram-aware OCR processing</p>
              <p>✓ Image caption generation</p>
              <p>✓ Markdown document conversion</p>
              <p>✓ Markdown-aware chunking</p>
              <p>✓ Text chunk and visual chunk creation</p>
              <p>✓ Figure and page-image retrieval</p>
              <p>✓ Visual source attribution</p>
              <p>✓ Page-level visual preview</p>
              <p>✓ Amazon Titan embedding search</p>
              <p>✓ Qdrant vector database</p>
              <p>✓ BM25 keyword retrieval</p>
              <p>✓ Reciprocal Rank Fusion ranking</p>
              <p>✓ Reranking for better context selection</p>
              <p>✓ Query rewriting</p>
              <p>✓ Retrieval Inspector</p>
              <p>✓ Source filename and page metadata</p>
              <p>✓ Streaming LLM responses</p>
              <p>✓ Multi-project document organization</p>
              <p>✓ User and project isolation</p>
              <p>✓ PostgreSQL metadata layer</p>
              <p>✓ Amazon S3 file and image storage</p>
              <p>✓ AWS Lambda container deployment</p>
              <p>✓ Dockerized FastAPI backend</p>
              <p>✓ Vercel-hosted Next.js frontend</p>
              <p>✓ Health endpoints for app, DB, Qdrant, and S3</p>
              <p>✓ Upload safety and file validation</p>
            </div>
          </div>

          <div className="mx-auto mb-12 grid max-w-6xl gap-5 md:grid-cols-4">
            <div className="rounded-2xl border border-emerald-400/20 bg-emerald-500/10 p-6">
              <p className="text-3xl font-bold text-emerald-300">PDF</p>
              <p className="mt-2 text-sm text-slate-300">
                Reports, manuals, research papers, and technical documents.
              </p>
            </div>

            <div className="rounded-2xl border border-blue-400/20 bg-blue-500/10 p-6">
              <p className="text-3xl font-bold text-blue-300">OCR</p>
              <p className="mt-2 text-sm text-slate-300">
                Scanned documents, screenshots, and image-based pages.
              </p>
            </div>

            <div className="rounded-2xl border border-cyan-400/20 bg-cyan-500/10 p-6">
              <p className="text-3xl font-bold text-cyan-300">Vision</p>
              <p className="mt-2 text-sm text-slate-300">
                Figures, diagrams, charts, visual content, and page previews.
              </p>
            </div>

            <div className="rounded-2xl border border-purple-400/20 bg-purple-500/10 p-6">
              <p className="text-3xl font-bold text-purple-300">RAG</p>
              <p className="mt-2 text-sm text-slate-300">
                Hybrid retrieval, fusion ranking, reranking, and sources.
              </p>
            </div>
          </div>

          <div className="mx-auto mb-12 max-w-4xl rounded-3xl border border-white/10 bg-white/10 p-8 text-left backdrop-blur">
            <h3 className="mb-4 text-2xl font-bold">
              Example Questions
            </h3>

            <div className="grid gap-3 text-sm text-slate-300 md:grid-cols-2">
              <p>“Summarize this scanned document.”</p>
              <p>“What does this uploaded image contain?”</p>
              <p>“Explain the figure on page 4.”</p>
              <p>“Find the section about evaluation metrics.”</p>
              <p>“Compare the key points across these documents.”</p>
              <p>“Show the sources used for this answer.”</p>
              <p>“What does the diagram describe?”</p>
              <p>“Extract the important information from this report.”</p>
            </div>
          </div>

          <div className="mx-auto mb-12 max-w-5xl rounded-3xl border border-blue-400/20 bg-blue-500/10 p-8 text-left">
            <h3 className="mb-5 text-2xl font-bold text-blue-100">
              Built for Real Document Workflows
            </h3>

            <div className="grid gap-5 md:grid-cols-3">
              <div>
                <h4 className="mb-2 font-semibold text-white">
                  For Research
                </h4>
                <p className="text-sm leading-relaxed text-slate-300">
                  Search papers, reports, notes, figures, diagrams, and scanned
                  material with grounded answers and citations.
                </p>
              </div>

              <div>
                <h4 className="mb-2 font-semibold text-white">
                  For Technical Docs
                </h4>
                <p className="text-sm leading-relaxed text-slate-300">
                  Query manuals, engineering documents, specifications, process
                  files, and mixed text-image documents.
                </p>
              </div>

              <div>
                <h4 className="mb-2 font-semibold text-white">
                  For AI Product Demos
                </h4>
                <p className="text-sm leading-relaxed text-slate-300">
                  Demonstrates applied AI engineering, cloud deployment,
                  retrieval quality, multimodal processing, and secure access.
                </p>
              </div>
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