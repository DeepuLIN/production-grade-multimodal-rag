"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { useAuth, useUser, UserButton } from "@clerk/nextjs";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import "katex/dist/katex.min.css";


const API_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
const ALLOWED_DEMO_EMAILS = ["deepak.ai.projects@gmail.com"];

type Project = {
  id: string;
  name: string;
};

type DocumentItem = {
  id: string;
  project_id: string;
  filename: string;
  content_type?: string;
  created_at?: string;
  status?: "processing" | "completed" | "failed";
  error_message?: string | null;
};

type Match = {
  rank?: number;
  source: string;
  filename?: string;
  page?: number;

  vector_score?: number | null;
  bm25_score?: number | null;
  rrf_score?: number | null;

  vector_rank?: number | null;
  bm25_rank?: number | null;

  text: string;
  document_id?: string;
  project_id?: string;
  chunk_index?: number | null;

  chunk_type?: "text" | "figure" | "image" | "table";
  caption?: string | null;
  image_s3_key?: string | null;
  image_url?: string | null;
  table_markdown?: string | null;





};

function shortName(name?: string, max = 44) {
  if (!name) return "Untitled document";
  return name.length > max ? `${name.slice(0, 22)}...${name.slice(-16)}` : name;
}



function normalizeMath(text: string) {
  return text.replace(/\[\s*([\s\S]*?)\s*\]/g, (match, content) => {
    const isMath =
      content.includes("=") ||
      content.includes("_") ||
      content.includes("^") ||
      content.includes("\\frac") ||
      content.includes("\\sqrt") ||
      content.includes("\\text") ||
      content.includes("\\left") ||
      content.includes("\\right");

    const isSource =
      content.includes("SOURCE") ||
      content.includes("chunk") ||
      content.includes(".pdf") ||
      content.includes("|");

    if (isMath && !isSource) {
      return `\n\n$$\n${content.trim()}\n$$\n\n`;
    }

    return match;
  });
}

function MultimodalRAGApp() {
  const { getToken } = useAuth();

  const [projects, setProjects] = useState<Project[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [selectedDocumentId, setSelectedDocumentId] = useState("all");
  const [newProjectName, setNewProjectName] = useState("");

  const [extractedText, setExtractedText] = useState("");
  const [matches, setMatches] = useState<Match[]>([]);
  const [selectedMatch, setSelectedMatch] = useState("all");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const [loadingProjects, setLoadingProjects] = useState(false);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [creatingProject, setCreatingProject] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [processingMode, setProcessingMode] = useState("auto");
  const [uploadStatus, setUploadStatus] = useState("");
  const [asking, setAsking] = useState(false);
  const [deletingId, setDeletingId] = useState("");
  const [deletingProjectId, setDeletingProjectId] = useState("");
  async function authHeaders(json = false) {
    const jwt = await getToken();
    if (!jwt) throw new Error("Authentication required");

    return {
      Authorization: `Bearer ${jwt}`,
      ...(json ? { "Content-Type": "application/json" } : {}),
    };
  }

  async function loadProjects() {
    setLoadingProjects(true);
    try {
      const headers = await authHeaders();

      const res = await fetch(`${API_BASE}/projects`, { headers });
      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();
      const loadedProjects = data.projects || [];
      setProjects(loadedProjects);

      if (!selectedProjectId && loadedProjects.length > 0) {
        setSelectedProjectId(loadedProjects[0].id);
      }
    } finally {
      setLoadingProjects(false);
    }
  }

  async function loadDocuments(projectId?: string) {
    setLoadingDocuments(true);
    try {
      const headers = await authHeaders();
      const targetProjectId = projectId || selectedProjectId;

      const url =
        targetProjectId && targetProjectId !== "all"
          ? `${API_BASE}/documents?project_id=${targetProjectId}`
          : `${API_BASE}/documents`;

      const res = await fetch(url, { headers });
      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();
      setDocuments(data.documents || []);
    } finally {
      setLoadingDocuments(false);
    }
  }

  async function pollDocumentStatus(documentId: string, projectId: string) {
    const interval = setInterval(async () => {
      try {
        const headers = await authHeaders();

        const res = await fetch(`${API_BASE}/documents/${documentId}/status`, {
          headers,
        });

        if (!res.ok) throw new Error(await res.text());

        const data = await res.json();

        if (data.status === "completed") {
          clearInterval(interval);
          setUploadStatus("Document indexed successfully.");
          await loadDocuments(projectId);
          setSelectedDocumentId(documentId);
        }

        if (data.status === "failed") {
          clearInterval(interval);
          setUploadStatus(
            `Processing failed: ${data.error_message || "Unknown error"}`
          );
          await loadDocuments(projectId);
        }
      } catch (error) {
        clearInterval(interval);
        setUploadStatus(`Status check failed: ${String(error)}`);
      }
    }, 3000);
  }

  useEffect(() => {
    loadProjects();
    loadDocuments();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (selectedProjectId) {
      setSelectedDocumentId("all");
      loadDocuments(selectedProjectId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProjectId]);

  useEffect(() => {
  if (!selectedProjectId) return;

  const hasProcessing = documents.some(
    (doc) => doc.status === "processing"
  );

  if (!hasProcessing) return;

  const interval = setInterval(() => {
    loadDocuments(selectedProjectId);
  }, 5000);

  return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [selectedProjectId, documents]);




  async function handleCreateProject() {
    if (!newProjectName.trim()) return;

    setCreatingProject(true);

    try {
      const headers = await authHeaders(true);

      const res = await fetch(`${API_BASE}/projects`, {
        method: "POST",
        headers,
        body: JSON.stringify({ name: newProjectName.trim() }),
      });

      if (!res.ok) throw new Error(await res.text());

      const project = await res.json();

      setNewProjectName("");
      setSelectedProjectId(project.id);

      await loadProjects();
      await loadDocuments(project.id);
    } catch (error) {
      setUploadStatus(`Project creation failed: ${String(error)}`);
      setExtractedText(`Error: ${String(error)}`);
    } finally {
      setCreatingProject(false);
    }
  }
  async function handleDeleteProject(projectId: string) {
    const project = projects.find((p) => p.id === projectId);
    const projectName = project?.name || "this project";

    const ok = window.confirm(
      `Delete project "${projectName}" and all its documents from Postgres, Qdrant, and S3?`
    );

    if (!ok) return;

    setDeletingProjectId(projectId);

    try {
      const headers = await authHeaders();

      const res = await fetch(`${API_BASE}/projects/${projectId}`, {
        method: "DELETE",
        headers,
      });

      if (!res.ok) throw new Error(await res.text());

      setSelectedDocumentId("all");
      setExtractedText("");
      setMatches([]);
      setAnswer("");

      const remainingProjects = projects.filter((p) => p.id !== projectId);
      const nextProjectId = remainingProjects[0]?.id || "";

      setSelectedProjectId(nextProjectId);

      await loadProjects();
      await loadDocuments(nextProjectId);
    } catch (error) {
      alert(`Delete project failed: ${String(error)}`);
    } finally {
      setDeletingProjectId("");
    }
  }
  async function uploadOneFile(file: File, index: number, total: number) {
    const headers = await authHeaders();
    const formData = new FormData();

    formData.append("file", file);

    if (selectedProjectId) {
      formData.append("project_id", selectedProjectId);
    }

    formData.append("processing_mode", processingMode);

    setUploadStatus(`Uploading ${index + 1}/${total}: ${file.name}`);

    const res = await fetch(`${API_BASE}/api`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!res.ok) throw new Error(await res.text());

    return await res.json();
  }

  async function handleFilesSelected(files: FileList | null) {
    if (!files || files.length === 0) return;

    setUploading(true);
    setAnswer("");
    setMatches([]);
    setExtractedText("");

    const fileArray = Array.from(files);

    try {
      let lastData: any = null;
      let lastDocumentId: string | null = null;

      for (let i = 0; i < fileArray.length; i++) {
        lastData = await uploadOneFile(fileArray[i], i, fileArray.length);

        if (lastData?.document_id) {
          lastDocumentId = lastData.document_id;
        }
      }

      if (lastDocumentId) {
        console.log("🔥 AUTO SELECTING NEW DOC:", lastDocumentId);
        setSelectedDocumentId(lastDocumentId);
      }

      setExtractedText(
        lastData?.extracted_text ||
          lastData?.cleaned_text ||
          lastData?.ocr_text ||
          lastData?.preview ||
          ""
      );

      setUploadStatus("Uploaded. Processing document...");
      await loadDocuments(selectedProjectId);

      if (lastDocumentId) {
        pollDocumentStatus(lastDocumentId, selectedProjectId);
      }
    } catch (error) {
      setUploadStatus(`Upload failed: ${String(error)}`);
      setExtractedText(`Error: ${String(error)}`);
    } finally {
      setUploading(false);
    }
  }

  async function handleDeleteDocument(documentId: string) {
    const ok = window.confirm("Delete this document from Postgres, Qdrant, and S3?");
    if (!ok) return;

    setDeletingId(documentId);

    try {
      const headers = await authHeaders();

      const res = await fetch(`${API_BASE}/documents/${documentId}`, {
        method: "DELETE",
        headers,
      });

      if (!res.ok) throw new Error(await res.text());

      if (selectedDocumentId === documentId) {
        setSelectedDocumentId("all");
      }

      await loadDocuments(selectedProjectId);
    } catch (error) {
      alert(`Delete failed: ${String(error)}`);
    } finally {
      setDeletingId("");
    }
  }


  async function handleProjectSummary() {
    if (!selectedProjectId) return;

    setAsking(true);
    setAnswer("");
    setMatches([]);
    setSelectedMatch("all");

    try {
      const headers = await authHeaders(true);

      const res = await fetch(`${API_BASE}/ask`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          query: "summarize all papers in this project",
          question: "summarize all papers in this project",
          top_k: 5,
          project_id: selectedProjectId,
          document_id: "all",
          rewrite: false,
        }),
      });

      if (!res.ok) throw new Error(await res.text());

      const data = await res.json();

      setAnswer(data.answer || "No project summary generated.");
      setMatches(data.top_matches || []);
    } catch (error) {
      setAnswer(`Error: ${String(error)}`);
    } finally {
      setAsking(false);
    }
  }


async function handleComparePapers() {
  if (!selectedProjectId) return;

  setAsking(true);
  setAnswer("");
  setMatches([]);
  setSelectedMatch("all");

  try {
    const headers = await authHeaders(true);

    const res = await fetch(`${API_BASE}/ask`, {
      method: "POST",
      headers,
      body: JSON.stringify({
        query: "compare all papers in this project",
        question: "compare all papers in this project",
        top_k: 5,
        project_id: selectedProjectId,
        document_id: "all",
        rewrite: false,
      }),
    });

    if (!res.ok) throw new Error(await res.text());

    const data = await res.json();

    setAnswer(data.answer || "No comparison generated.");
    setMatches(data.top_matches || []);
  } catch (error) {
    setAnswer(`Error: ${String(error)}`);
  } finally {
    setAsking(false);
  }
}

  async function handleAsk() {
    if (!question.trim()) return;

    const documentId = selectedDocumentId === "all" ? null : selectedDocumentId;

    console.log("🔥 FINAL ASK PAYLOAD DOC ID:", documentId);
    console.log("======== ASK DEBUG ========");
    console.log("question:", question);
    console.log("selectedProjectId:", selectedProjectId);
    console.log("selectedDocumentId:", selectedDocumentId);
    console.log("document_id sent:", documentId);
    console.log("===========================");

    setAsking(true);
    setAnswer("");
    setMatches([]);
    setSelectedMatch("all");

    try {
      const headers = await authHeaders(true);

      const res = await fetch(`${API_BASE}/ask/stream`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          query: question,
          question,
          top_k: 5,
          project_id: selectedProjectId || null,
          document_id: documentId,
        }),
      });

      if (!res.ok || !res.body) throw new Error(await res.text());

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() || "";

        for (const event of events) {
          if (!event.startsWith("data: ")) continue;

          const data = JSON.parse(event.replace("data: ", ""));

          if (data.type === "sources") {
            setMatches(data.top_matches || []);
          }

          if (data.type === "token") {
            setAnswer((prev) => prev + data.content);
          }

          if (data.type === "error") {
            setAnswer(`Error: ${data.message}`);
          }
        }
      }
    } catch (error) {
      setAnswer(`Error: ${String(error)}`);
    } finally {
      setAsking(false);
    }
  }

  const selectedMatchObject =
    selectedMatch === "all"
      ? null
      : matches.find((_, idx) => String(idx) === selectedMatch);

  const firstImageMatch = matches.find(
    (match) =>
      (match.chunk_type === "figure" || match.chunk_type === "image") &&
      match.image_url
  );
  
  const firstTableMatch = matches.find(
    (match) =>
      match.chunk_type === "table" &&
      (match.image_url || match.table_markdown)
  );

  const selectedDocument =
    selectedDocumentId === "all"
      ? null
      : documents.find((doc) => doc.id === selectedDocumentId);

  const canAsk =
    selectedDocumentId === "all" ||
    selectedDocument?.status === "completed";


  




  return (
    <main className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,#e0f2fe,transparent_35%),radial-gradient(circle_at_top_right,#f5d0fe,transparent_30%),linear-gradient(to_bottom,#f8fafc,#eef2ff)]">
      <div className="relative mx-auto grid max-w-7xl grid-cols-1 gap-6 px-4 py-8 lg:grid-cols-[330px_1fr]">
        <aside className="rounded-[2rem] border border-white/70 bg-white/75 p-5 shadow-2xl shadow-slate-200/70 backdrop-blur-xl">
          <h2 className="mb-4 text-xl font-bold text-slate-900">Workspace</h2>

          <label className="mb-2 block text-sm font-semibold text-slate-600">
            Project
          </label>

          <select
            title="Choose the project where documents should be stored and searched"
            value={selectedProjectId}
            onChange={(e) => {
              console.log("PROJECT CHANGED:", e.target.value);
              setSelectedProjectId(e.target.value);
            }}
            className="mb-4 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none focus:ring-4 focus:ring-slate-200"
          >
            {loadingProjects ? (
              <option>Loading projects...</option>
            ) : (
              projects.map((project) => (
                <option key={project.id} value={project.id}>
                  {project.name}
                </option>
              ))
            )}
          </select>
          

          <button
            title="Delete selected project and its documents"
            onClick={() => handleDeleteProject(selectedProjectId)}
            disabled={!selectedProjectId || deletingProjectId === selectedProjectId}
            className="mb-4 mt-2 w-full rounded-2xl border border-red-200 bg-red-50 px-4 py-2 text-xs font-bold text-red-700 transition hover:bg-red-100 disabled:opacity-50"
          >
            {deletingProjectId === selectedProjectId
              ? "Deleting project..."
              : "Delete Selected Project"}
          </button>

          <div className="mb-4 flex gap-2">
            <input
              title="Enter a new project name"
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              placeholder="New project"
              className="min-w-0 flex-1 rounded-2xl border border-indigo-300 bg-indigo-50 px-4 py-3 text-sm text-slate-900 placeholder:text-slate-500 outline-none focus:ring-4 focus:ring-indigo-200 focus:border-indigo-500"
            />

            <button
              title="Create project"
              onClick={handleCreateProject}
              disabled={!newProjectName.trim() || creatingProject}
              className="rounded-2xl bg-slate-900 px-4 py-3 text-sm font-bold text-white transition hover:scale-105 disabled:opacity-50"
            >
              +
            </button>
          </div>
          
          <div className="mb-5 rounded-2xl border border-dashed border-slate-300 bg-slate-50/80 p-4">

            <label className="mb-2 block text-xs font-bold text-slate-600">
              Processing mode
            </label>

            <select
              value={processingMode}
              onChange={(e) => setProcessingMode(e.target.value)}
              className="mb-4 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none focus:ring-4 focus:ring-slate-200"
            >
              <option value="auto">Auto detect</option>
              <option value="pdf_text">Text PDF / Research paper</option>
              <option value="scanned_pdf">Scanned PDF / OCR</option>
              <option value="handwritten">Handwritten notes / image</option>
              <option value="visual_heavy">Visual-heavy document</option>
            </select>

            <input
              id="multi-upload"
              type="file"
              multiple
              accept="image/*,.pdf,application/pdf"
              onChange={(e) => handleFilesSelected(e.target.files)}
              className="hidden"
            />

            <label
              title="Select one or more documents. They will be uploaded, OCR processed, chunked, and indexed automatically."
              htmlFor="multi-upload"
              className="block cursor-pointer rounded-2xl bg-slate-900 px-4 py-3 text-center text-sm font-bold text-white transition hover:scale-[1.01] hover:bg-black"
            >
              {uploading ? "Uploading..." : "Upload Documents"}
            </label>

            <p
              title={uploadStatus || "You can upload multiple files at once"}
              className="mt-3 truncate text-xs text-slate-500"
            >
              {uploadStatus || "Upload PDFs/images directly into this project."}
            </p>
          </div>

          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">Documents</h3>
            <button
              title="Refresh document list"
              onClick={() => loadDocuments(selectedProjectId)}
              className="rounded-xl px-2 py-1 text-xs text-slate-500 transition hover:bg-slate-100 hover:text-slate-900"
            >
              Refresh
            </button>
          </div>

          <select
            title="Ask all project documents or only one selected document"
            value={selectedDocumentId}
            onChange={(e) => {
              console.log("DOCUMENT DROPDOWN CHANGED:", e.target.value);
              setSelectedDocumentId(e.target.value);
            }}
            className="mb-4 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none focus:ring-4 focus:ring-slate-200"
          >
            <option value="all">Ask all documents in project</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {shortName(doc.filename)}
              </option>
            ))}
          </select>

          <div className="max-h-[34rem] space-y-2 overflow-y-auto pr-1">
            {loadingDocuments ? (
              <p className="text-sm text-slate-400">Loading documents...</p>
            ) : documents.length === 0 ? (
              <p className="text-sm text-slate-400">No documents uploaded yet.</p>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  className={`group flex items-center gap-2 rounded-2xl border px-3 py-2 transition ${
                    selectedDocumentId === doc.id
                      ? "border-slate-900 bg-white"
                      : "border-slate-200 bg-white/70 hover:bg-white"
                  }`}
                >
                  <button
                    title={doc.filename}
                    onClick={() => {
                      console.log("DOCUMENT CARD SELECTED:", doc.id);
                      setSelectedDocumentId(doc.id);
                    }}
                    className="min-w-0 flex-1 text-left"
                  >
                    <p className="truncate text-sm font-semibold text-slate-800">
                      {doc.filename}
                    </p>

                    <p className="truncate text-[11px] text-slate-400">
                      {doc.content_type || "document"}
                      {doc.status ? ` · ${doc.status}` : ""}
                    </p>

                    {doc.status === "failed" && doc.error_message ? (
                      <p className="truncate text-[11px] text-red-500">
                        {doc.error_message}
                      </p>
                    ) : null}
                  </button>

                  <button
                    title="Delete document"
                    onClick={() => handleDeleteDocument(doc.id)}
                    disabled={deletingId === doc.id}
                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm text-slate-400 opacity-60 transition hover:bg-red-50 hover:text-red-600 hover:opacity-100 disabled:opacity-30"
                  >
                    {deletingId === doc.id ? "…" : "×"}
                  </button>
                </div>
              ))
            )}
          </div>
        </aside>

        <section className="space-y-6">
          <header className="rounded-[2rem] border border-white/70 bg-white/75 p-8 text-center shadow-2xl shadow-slate-200/70 backdrop-blur-xl">
            <h1 className="mb-3 text-5xl font-bold tracking-tight text-slate-900">
              Multimodal RAG
            </h1>
            <p className="mx-auto max-w-3xl text-slate-600">
              Upload documents, extract text, index chunks, and ask grounded
              questions inside selected projects.
            </p>
          </header>

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <section className="rounded-[2rem] border border-white/70 bg-white/75 p-6 shadow-2xl shadow-slate-200/70 backdrop-blur-xl">
              <h2 className="mb-5 text-2xl font-bold text-slate-900">
                Extracted Text
              </h2>

              <div className="min-h-[28rem] max-h-[36rem] overflow-y-auto whitespace-pre-wrap rounded-3xl border border-slate-200 bg-white/80 p-5 text-slate-700 shadow-inner">
                {extractedText ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                    {extractedText}
                  </ReactMarkdown>
                ) : (
                  <p className="text-slate-400">
                    After uploading, the latest extracted OCR text will appear here.
                  </p>
                )}
              </div>
            </section>

            <section className="rounded-[2rem] border border-white/70 bg-white/75 p-6 shadow-2xl shadow-slate-200/70 backdrop-blur-xl">
              <h2 className="mb-5 text-2xl font-bold text-slate-900">
                Top 3 Matches
              </h2>

              <select
                title="Select which retrieved chunk to inspect"
                value={selectedMatch}
                onChange={(e) => setSelectedMatch(e.target.value)}
                className="mb-5 w-full rounded-2xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-700 outline-none focus:ring-4 focus:ring-slate-200"
              >
                <option value="all">
                  {matches.length ? "Show all top matches" : "No matches yet"}
                </option>

                {matches.slice(0, 3).map((match, idx) => (
                  <option key={idx} value={String(idx)}>
                    Match #{idx + 1} — {shortName(match.filename || match.source)}
                  </option>
                ))}
              </select>

              <div className="min-h-[28rem] max-h-[36rem] overflow-y-auto rounded-3xl border border-slate-200 bg-white/80 p-5 shadow-inner">
                {matches.length === 0 ? (
                  <p className="text-slate-400">
                    Ask a question to see retrieved chunks.
                  </p>
                ) : selectedMatchObject ? (
                  <div>
                    <p
                      title={selectedMatchObject.filename || selectedMatchObject.source}
                      className="mb-3 max-w-full truncate text-sm text-slate-500"
                    >
                      Source:{" "}
                      {selectedMatchObject.filename || selectedMatchObject.source}
                      {selectedMatchObject.chunk_index !== undefined &&
                      selectedMatchObject.chunk_index !== null
                        ? ` · Chunk ${selectedMatchObject.chunk_index}`
                        : ""}
                    </p>

                    <div className="mb-3 mt-2 grid grid-cols-1 gap-2 text-xs sm:grid-cols-3">
                      <div className="rounded-xl bg-slate-100 px-3 py-2">
                        <p className="font-semibold text-slate-500">Vector</p>
                        <p className="font-bold text-slate-900">
                          {selectedMatchObject.vector_score !== undefined &&
                          selectedMatchObject.vector_score !== null
                            ? selectedMatchObject.vector_score.toFixed(3)
                            : "—"}
                        </p>
                      </div>

                      <div className="rounded-xl bg-slate-100 px-3 py-2">
                        <p className="font-semibold text-slate-500">BM25</p>
                        <p className="font-bold text-slate-900">
                          {selectedMatchObject.bm25_score !== undefined &&
                          selectedMatchObject.bm25_score !== null
                            ? selectedMatchObject.bm25_score.toFixed(3)
                            : "—"}
                        </p>
                      </div>

                      <div className="rounded-xl bg-slate-100 px-3 py-2">
                        <p className="font-semibold text-slate-500">RRF</p>
                        <p className="font-bold text-slate-900">
                          {selectedMatchObject.rrf_score !== undefined &&
                          selectedMatchObject.rrf_score !== null
                            ? selectedMatchObject.rrf_score.toFixed(4)
                            : "—"}
                        </p>
                      </div>
                    </div>
                    {(selectedMatchObject.chunk_type === "figure" ||
                      selectedMatchObject.chunk_type === "image") &&
                      selectedMatchObject.image_url && (
                        <img
                          src={selectedMatchObject.image_url}
                          alt={selectedMatchObject.caption || "Retrieved visual source"}
                          className="mb-4 max-h-[420px] w-full rounded-2xl border border-slate-200 object-contain"
                        />
                      )}

                    {selectedMatchObject.chunk_type === "table" &&
                      selectedMatchObject.table_markdown && (
                        <div className="prose prose-sm mb-4 max-w-none overflow-x-auto rounded-2xl border border-slate-200 bg-white p-4">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {selectedMatchObject.table_markdown}
                          </ReactMarkdown>
                        </div>
                      )}

                    <p className="whitespace-pre-wrap break-words text-sm leading-6 text-slate-700">
                      {selectedMatchObject.text}
                    </p>
                    



                  </div>
                ) : (
                  <div className="space-y-4">
                    {matches.slice(0, 3).map((match, idx) => (
                      <div
                        key={idx}
                        className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4"
                      >
                        <h3 className="mb-1 font-bold text-slate-900">
                          Match #{idx + 1}
                        </h3>

                        <p
                          title={match.filename || match.source}
                          className="mb-2 max-w-full truncate text-sm text-slate-500"
                        >
                          Source: {match.filename || match.source}
                          {match.chunk_index !== undefined &&
                          match.chunk_index !== null
                            ? ` · Chunk ${match.chunk_index}`
                            : ""}
                        </p>

                        <div className="mb-3 mt-2 grid grid-cols-1 gap-2 text-xs sm:grid-cols-3">
                          <div className="rounded-xl bg-slate-100 px-3 py-2">
                            <p className="font-semibold text-slate-500">Vector</p>
                            <p className="font-bold text-slate-900">
                              {match.vector_score !== undefined &&
                              match.vector_score !== null
                                ? match.vector_score.toFixed(3)
                                : "—"}
                            </p>
                          </div>

                          <div className="rounded-xl bg-slate-100 px-3 py-2">
                            <p className="font-semibold text-slate-500">BM25</p>
                            <p className="font-bold text-slate-900">
                              {match.bm25_score !== undefined &&
                              match.bm25_score !== null
                                ? match.bm25_score.toFixed(3)
                                : "—"}
                            </p>
                          </div>

                          <div className="rounded-xl bg-slate-100 px-3 py-2">
                            <p className="font-semibold text-slate-500">RRF</p>
                            <p className="font-bold text-slate-900">
                              {match.rrf_score !== undefined &&
                              match.rrf_score !== null
                                ? match.rrf_score.toFixed(4)
                                : "—"}
                            </p>
                          </div>
                        </div>
                        {(match.chunk_type === "figure" || match.chunk_type === "image") && ( 
                          <p className="mb-2 text-xs font-bold text-emerald-700">
                            Visual source detected · image_url: {match.image_url ? "yes" : "no"}
                          </p>
                        )}

                        {(match.chunk_type === "figure" || match.chunk_type === "image") &&
                        match.image_url && (
                          <img
                            src={match.image_url}
                            alt={match.caption || "Retrieved figure"}
                            className="mb-4 max-h-[420px] w-full rounded-2xl border border-slate-200 bg-white object-contain"
                          />
                        )}

                        {match.chunk_type === "table" && match.table_markdown && (
                          <div className="prose prose-sm mb-4 max-w-none overflow-x-auto rounded-2xl border border-slate-200 bg-white p-4">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {match.table_markdown}
                            </ReactMarkdown>
                          </div>
                        )}

                        <p className="whitespace-pre-wrap break-words text-sm leading-6 text-slate-700">
                          {match.text}
                        </p>

                      </div>
                    ))}
                  </div>
                )}
              </div>
            </section>
          </div>

          <section className="rounded-[2rem] border border-white/70 bg-white/75 p-6 shadow-2xl shadow-slate-200/70 backdrop-blur-xl">
            <h2 className="mb-5 text-2xl font-bold text-slate-900">
              Ask a Question
            </h2>

            <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-[260px_1fr]">
              <select
                title="Choose whether to ask all project documents or one document"
                value={selectedDocumentId}
                onChange={(e) => {
                  console.log("ASK DOCUMENT SELECT CHANGED:", e.target.value);
                  setSelectedDocumentId(e.target.value);
                }}
                className="rounded-2xl border border-slate-300 bg-white px-4 py-4 text-sm text-slate-700 outline-none focus:ring-4 focus:ring-slate-200"
              >
                <option value="all">Ask all documents</option>
                {documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {shortName(doc.filename)}
                  </option>
                ))}
              </select>

              <input
                title="Ask a question grounded in the selected project or document"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question about your uploaded documents..."
                className="rounded-2xl border border-slate-300 bg-white px-5 py-4 text-slate-700 outline-none focus:ring-4 focus:ring-slate-200"
              />
            </div>
            <div className="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={handleProjectSummary}
                disabled={!selectedProjectId || asking}
                className="rounded-2xl border border-slate-300 bg-white px-5 py-3 text-sm font-bold text-slate-700 transition hover:scale-[1.01] hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                📄 Summarize Project
              </button>

              <button
                type="button"
                onClick={handleComparePapers}
                disabled={!selectedProjectId || asking}
                className="rounded-2xl border border-slate-300 bg-white px-5 py-3 text-sm font-bold text-slate-700 transition hover:scale-[1.01] hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                Compare Documents
              </button>
            </div>
            <button
              title="Search your filtered Qdrant chunks and stream an answer"
              onClick={handleAsk}
              disabled={!question.trim() || asking || !canAsk}
              className="w-full rounded-2xl bg-slate-900 px-8 py-4 text-lg font-bold text-white shadow-xl shadow-slate-300 transition hover:scale-[1.01] hover:bg-black disabled:cursor-not-allowed disabled:opacity-50"
            >
              {asking
                ? "Streaming answer..."
                : !canAsk
                  ? "Document still processing..."
                  : "Ask with RAG"}
            </button>

            <div className="mt-6">
              <h3 className="mb-3 text-xl font-bold text-slate-900">
                Grounded Answer
              </h3>

              <div className="min-h-40 rounded-3xl border border-slate-200 bg-white/80 p-6 text-slate-700 shadow-inner">
                {answer ? (
                  <div className="prose max-w-none prose-slate">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkBreaks, remarkMath]}
                      rehypePlugins={[rehypeKatex]}
                    >
                      {normalizeMath(answer)}
                    </ReactMarkdown>

                    {firstImageMatch && (
                      <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-4">
                        <p className="mb-2 text-sm font-bold text-slate-900">
                          Retrieved Visual Source
                        </p>

                        <img
                          src={firstImageMatch.image_url || ""}
                          alt={firstImageMatch.caption || "Retrieved visual source"}
                          className="max-h-[500px] w-full rounded-xl border border-slate-200 object-contain"
                        />

                        <p className="mt-3 text-xs text-slate-500">
                          Source: {firstImageMatch.filename || firstImageMatch.source}
                          {firstImageMatch.page ? ` · Page ${firstImageMatch.page}` : ""}
                        </p>
                      </div>
                    )}

                    {firstTableMatch && (
                      <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-4">
                        <p className="mb-2 text-sm font-bold text-slate-900">
                          Retrieved Table Source
                        </p>

                        {firstTableMatch.image_url && (
                          <img
                            src={firstTableMatch.image_url}
                            alt={firstTableMatch.caption || "Retrieved table source"}
                            className="mb-4 max-h-[500px] w-full rounded-xl border border-slate-200 object-contain"
                          />
                        )}

                        {firstTableMatch.table_markdown && (
                          <div className="prose prose-sm max-w-none overflow-x-auto">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {firstTableMatch.table_markdown}
                            </ReactMarkdown>
                          </div>
                        )}

                        <p className="mt-3 text-xs text-slate-500">
                          Source: {firstTableMatch.filename || firstTableMatch.source}
                          {firstTableMatch.page ? ` · Page ${firstTableMatch.page}` : ""}
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <p className="text-slate-400">
                    The streamed answer will appear here.
                  </p>
                )}
              </div>
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}

export default function Product() {
  const { user, isLoaded } = useUser();

  const userEmail = user?.primaryEmailAddress?.emailAddress?.toLowerCase();

  const isAllowedDemoUser =
    !!userEmail && ALLOWED_DEMO_EMAILS.includes(userEmail);

  if (!isLoaded) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
        <p className="text-sm text-slate-300">Loading demo access...</p>
      </main>
    );
  }

  if (!user || !isAllowedDemoUser) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-950 p-6 text-white">
        <div className="max-w-md rounded-3xl border border-red-400/30 bg-red-500/10 p-8 text-center shadow-2xl">
          <h1 className="mb-3 text-2xl font-bold text-red-100">
            Private Recruiter Demo
          </h1>

          <p className="mb-6 text-sm leading-relaxed text-slate-300">
            This application is restricted. Please use the provided recruiter
            demo account to access the platform.
          </p>

          <UserButton showName={true} />
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50">
      <div
        title="Your account"
        className="absolute right-4 top-4 z-20 rounded-2xl border border-white/70 bg-white/80 px-3 py-2 shadow-lg backdrop-blur-xl"
      >
        <UserButton showName={true} />
      </div>

      <MultimodalRAGApp />
    </main>
  );
}