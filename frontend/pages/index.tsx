"use client";

import Link from "next/link";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="container mx-auto px-4 py-12">
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-slate-800">
            Multimodal Rag
          </h1>

          <div>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="bg-slate-800 hover:bg-slate-900 text-white font-medium py-2 px-6 rounded-xl transition-all shadow-sm">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>

            <SignedIn>
              <div className="flex items-center gap-4 bg-white rounded-xl px-3 py-2 border border-slate-200 shadow-sm">
                <Link
                  href="/product"
                  className="bg-slate-800 hover:bg-slate-900 text-white font-medium py-2 px-6 rounded-xl transition-all shadow-sm"
                >
                  Go to App
                </Link>

                <UserButton showName={true} />
              </div>
            </SignedIn>
          </div>
        </nav>

        <div className="text-center py-24">
          <h2 className="text-6xl font-bold text-slate-800 mb-6">
            Transform Handwritten Notes
            <br />
            Into Digital Text
          </h2>

          <p className="text-xl text-slate-600 mb-8 max-w-2xl mx-auto">
            Upload handwritten notes, lecture pages, meeting notes, or study
            material and convert them into clean, editable digital text using AI.
          </p>

          <div className="bg-white border border-slate-200 rounded-3xl shadow-xl p-8 max-w-sm mx-auto mb-10">
            <h3 className="text-2xl font-bold mb-3 text-slate-800">
              Premium Subscription
            </h3>

            <p className="text-5xl font-bold text-slate-800 mb-3">
              $8
              <span className="text-lg text-slate-500">/month</span>
            </p>

            <ul className="text-left text-slate-600 space-y-2 mb-6">
              <li>✓ Unlimited note digitization</li>
              <li>✓ AI-powered handwritten OCR</li>
              <li>✓ Clean editable digital text</li>
              <li>✓ Future summaries and flashcards</li>
            </ul>
          </div>

          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-slate-800 hover:bg-slate-900 text-white font-bold py-4 px-10 rounded-2xl text-lg transition-all duration-300 hover:scale-105 shadow-sm">
                Start Converting Notes
              </button>
            </SignInButton>
          </SignedOut>

          <SignedIn>
            <Link href="/product">
              <button className="bg-slate-800 hover:bg-slate-900 text-white font-bold py-4 px-10 rounded-2xl text-lg transition-all duration-300 hover:scale-105 shadow-sm">
                Access NoteVision AI
              </button>
            </Link>
          </SignedIn>
        </div>
      </div>
    </main>
  );
}