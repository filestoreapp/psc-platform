"use client";

import { useState, useEffect } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;
const ADMIN_KEY = process.env.NEXT_PUBLIC_ADMIN_API_KEY;

interface NewsItem {
  id: number;
  title: string;
  body: string;
  hashtags?: string | null;
  status: string;
  published_at?: string | null;
  scheduled_for?: string | null;
  subjects: string[];
  exam_types: string[];
}

interface Subject {
  id: number;
  name: string;
}

interface ExamType {
  id: number;
  name: string;
}

export default function AdminNewsPage() {
  const [newsList, setNewsList] = useState<NewsItem[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [examTypes, setExamTypes] = useState<ExamType[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [hashtags, setHashtags] = useState("");
  const [selectedSubjectIds, setSelectedSubjectIds] = useState<number[]>([]);
  const [selectedExamTypeIds, setSelectedExamTypeIds] = useState<number[]>([]);

  useEffect(() => {
    fetchNews();
    fetchSubjects();
    fetchExamTypes();
  }, []);

  async function fetchSubjects() {
    try {
      const res = await fetch(`${API_URL}/subjects`);
      if (res.ok) setSubjects(await res.json());
    } catch (e) { console.error(e); }
  }

  async function fetchExamTypes() {
    try {
      const res = await fetch(`${API_URL}/exam-types`);
      if (res.ok) setExamTypes(await res.json());
    } catch (e) { console.error(e); }
  }

  async function fetchNews() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/admin/news`, {
        headers: { "x-admin-key": ADMIN_KEY || "" },
      });
      if (!res.ok) throw new Error("Failed to fetch news");
      const data = await res.json();
      setNewsList(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function toggleSubject(id: number) {
    setSelectedSubjectIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  }

  function toggleExamType(id: number) {
    setSelectedExamTypeIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  }

  async function createDraft() {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        title,
        body,
        hashtags,
        subject_ids: selectedSubjectIds,
        exam_type_ids: selectedExamTypeIds,
        status: "draft",
      };
      const res = await fetch(`${API_URL}/admin/news`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-admin-key": ADMIN_KEY || "",
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Failed to create draft");
      setTitle("");
      setBody("");
      setHashtags("");
      setSelectedSubjectIds([]);
      setSelectedExamTypeIds([]);
      await fetchNews();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function publishNews(id: number) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/admin/news/${id}/publish`, {
        method: "POST",
        headers: { "x-admin-key": ADMIN_KEY || "" },
      });
      if (!res.ok) throw new Error("Failed to publish");
      await fetchNews();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Admin News Management</h1>

      <div className="bg-white shadow rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Create New Post</h2>
        <div className="space-y-4">
          <input
            type="text"
            placeholder="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          />
          <textarea
            placeholder="Body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={6}
            className="w-full p-2 border border-gray-300 rounded"
          />
          <input
            type="text"
            placeholder="Hashtags (e.g., #KeralaPSC #Polity)"
            value={hashtags}
            onChange={(e) => setHashtags(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
          />

          <div className="grid grid-cols-2 gap-4">
            {/* Subjects */}
            <div>
              <label className="block font-medium mb-1">Subjects</label>
              <div className="max-h-40 overflow-y-auto border border-gray-300 rounded p-2">
                {subjects.map((s) => (
                  <label key={s.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={selectedSubjectIds.includes(s.id)}
                      onChange={() => toggleSubject(s.id)}
                      className="h-4 w-4"
                    />
                    <span>{s.name}</span>
                  </label>
                ))}
              </div>
            </div>
            {/* Exam Types */}
            <div>
              <label className="block font-medium mb-1">Exam Types</label>
              <div className="max-h-40 overflow-y-auto border border-gray-300 rounded p-2">
                {examTypes.map((e) => (
                  <label key={e.id} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={selectedExamTypeIds.includes(e.id)}
                      onChange={() => toggleExamType(e.id)}
                      className="h-4 w-4"
                    />
                    <span>{e.name}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          <button
            onClick={createDraft}
            disabled={loading || !title || !body}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            Save Draft
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div>
        <h2 className="text-xl font-semibold mb-4">Existing Posts</h2>
        {loading && <p>Loading...</p>}
        <div className="space-y-4">
          {newsList.map((news) => (
            <div
              key={news.id}
              className="bg-white shadow rounded-lg p-4 flex justify-between items-start"
            >
              <div>
                <h3 className="font-medium">{news.title}</h3>
                <p className="text-sm text-gray-500">
                  Status: {news.status}
                  {news.published_at && ` | Published: ${new Date(news.published_at).toLocaleString()}`}
                </p>
                <p className="text-sm text-gray-500">
                  Subjects: {news.subjects.join(", ") || "None"} | Exam Types:{" "}
                  {news.exam_types.join(", ") || "None"}
                </p>
              </div>
              {news.status === "draft" && (
                <button
                  onClick={() => publishNews(news.id)}
                  disabled={loading}
                  className="ml-4 px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                >
                  Publish
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
