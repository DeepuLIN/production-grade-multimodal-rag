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
        <nav className="flex justify-between items-center mb-20">
          <h1 className="text-2xl font-bold tracking-tight">
            Multimodal RAG Platform
          </h1>

          <div>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-xl transition-all shadow-lg shadow-blue-900/30">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>

            <SignedIn>
              <div className="flex items-center gap-4 bg-white/10 backdrop-blur rounded-xl px-3 py-2 border border-white/10 shadow-sm">
                {isAllowedDemoUser ? (
                  <Link
                    href="/product"
                    className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-xl transition-all shadow-lg shadow-blue-900/30"
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

        <section className="text-center py-20">
          <div className="inline-flex items-center rounded-full border border-blue-400/30 bg-blue-500/10 px-4 py-2 text-sm text-blue-200 mb-8">
            AWS deployed • OCR • Hybrid retrieval • Multimodal RAG
          </div>

          <h2 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
            Production-Grade
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-cyan-300 to-emerald-300 bg-clip-text text-transparent">
              Multimodal RAG Platform
            </span>
          </h2>

          <p className="text-lg md:text-xl text-slate-300 mb-10 max-w-3xl mx-auto leading-relaxed">
            Ingest PDFs, scanned documents, images, diagrams, and technical
            content into secure AI-powered knowledge bases using OCR, visual
            extraction, hybrid retrieval, vector search, and streaming LLM
            responses.
          </p>

          <div className="grid md:grid-cols-3 gap-5 max-w-5xl mx-auto mb-12">
            <div className="bg-white/10 backdrop-blur border border-white/10 rounded-2xl p-6 text-left">
              <h3 className="text-xl font-semibold mb-3">
                Document Intelligence
              </h3>
              <p className="text-slate-300 text-sm leading-relaxed">
                Upload PDFs and images, extract OCR text, capture visual labels,
                and transform documents into Markdown-based RAG chunks.
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur border border-white/10 rounded-2xl p-6 text-left">
              <h3 className="text-xl font-semibold mb-3">Hybrid Retrieval</h3>
              <p className="text-slate-300 text-sm leading-relaxed">
                Combine semantic vector search, BM25 keyword retrieval, metadata
                filtering, project isolation, and RRF fusion for grounded
                answers.
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur border border-white/10 rounded-2xl p-6 text-left">
              <h3 className="text-xl font-semibold mb-3">Cloud Architecture</h3>
              <p className="text-slate-300 text-sm leading-relaxed">
                Built with FastAPI, AWS Lambda, S3, Qdrant, PostgreSQL, Clerk,
                Docker, and Vercel.
              </p>
            </div>
          </div>

          <div className="bg-slate-900/80 border border-white/10 rounded-3xl shadow-2xl p-8 max-w-3xl mx-auto mb-10">
            <h3 className="text-2xl font-bold mb-5">Core Capabilities</h3>

            <div className="grid md:grid-cols-2 gap-3 text-left text-slate-300">
              <p>✓ PDF & image ingestion</p>
              <p>✓ OCR and visual extraction</p>
              <p>✓ Project-based document isolation</p>
              <p>✓ Qdrant vector database</p>
              <p>✓ BM25 keyword retrieval</p>
              <p>✓ RRF hybrid ranking</p>
              <p>✓ PostgreSQL metadata layer</p>
              <p>✓ Amazon S3 document storage</p>
              <p>✓ Health monitoring endpoints</p>
              <p>✓ Secure upload validation</p>
              <p>✓ Streaming AI responses</p>
              <p>✓ AWS Lambda deployment</p>
            </div>
          </div>

          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-10 rounded-2xl text-lg transition-all duration-300 hover:scale-105 shadow-lg shadow-blue-900/40">
                Explore Platform
              </button>
            </SignInButton>
          </SignedOut>

          <SignedIn>
            {isAllowedDemoUser ? (
              <Link href="/product">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 px-10 rounded-2xl text-lg transition-all duration-300 hover:scale-105 shadow-lg shadow-blue-900/40">
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