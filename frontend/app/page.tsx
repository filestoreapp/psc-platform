"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

interface NewsItem {
  id: number;
  title: string;
  body: string;
  hashtags?: string | null;
  published_at: string;
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

export default function HomePage() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [examTypes, setExamTypes] = useState<ExamType[]>([]);
  const [selectedSubject, setSelectedSubject] = useState("");
  const [selectedExamType, setSelectedExamType] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSubjects();
    fetchExamTypes();
    fetchNews();
  }, []);

  useEffect(() => {
    fetchNews();
  }, [selectedSubject, selectedExamType]);

  async function fetchSubjects() {
    try {
      const res = await fetch(`${API_URL}/subjects`);
      if (res.ok) setSubjects(await res.json());
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchExamTypes() {
    try {
      const res = await fetch(`${API_URL}/exam-types`);
      if (res.ok) setExamTypes(await res.json());
    } catch (e) {
      console.error(e);
    }
  }

  async function fetchNews() {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (selectedSubject) params.append("subject", selectedSubject);
      if (selectedExamType) params.append("exam_type", selectedExamType);
      const res = await fetch(`${API_URL}/news?${params.toString()}`);
      if (!res.ok) throw new Error("Failed to fetch news");
      const data = await res.json();
      setNews(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function formatDate(dateStr: string) {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-IN", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8">
        Current Affairs & PSC News
      </h1>

      <div className="flex flex-col sm:flex-row gap-4 mb-8">
        <select
          value={selectedSubject}
          onChange={(e) => setSelectedSubject(e.target.value)}
          className="p-2 border border-gray-300 rounded w-full sm:w-1/2"
        >
          <option value="">All Subjects</option>
          {subjects.map((s) => (
            <option key={s.id} value={s.name}>
              {s.name}
            </option>
          ))}
        </select>

        <select
          value={selectedExamType}
          onChange={(e) => setSelectedExamType(e.target.value)}
          className="p-2 border border-gray-300 rounded w-full sm:w-1/2"
        >
          <option value="">All Exam Types</option>
          {examTypes.map((e) => (
            <option key={e.id} value={e.name}>
              {e.name}
            </option>
          ))}
        </select>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading ? (
        <p className="text-center">Loading news...</p>
      ) : news.length === 0 ? (
        <p className="text-center text-gray-500">No news found.</p>
      ) : (
        <div className="space-y-6">
          {news.map((item) => (
            <article
              key={item.id}
              className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <h2 className="text-xl font-semibold mb-2">{item.title}</h2>
              <div className="text-sm text-gray-500 mb-2">
                {formatDate(item.published_at)}
                {item.subjects.length > 0 && (
                  <span className="ml-2">• {item.subjects.join(", ")}</span>
                )}
                {item.exam_types.length > 0 && (
                  <span className="ml-2">• {item.exam_types.join(", ")}</span>
                )}
              </div>
              {item.hashtags && (
                <p className="text-blue-600 text-sm mb-2">{item.hashtags}</p>
              )}
              <p className="text-gray-700 whitespace-pre-line">
                {item.body.length > 250
                  ? item.body.substring(0, 250) + "..."
                  : item.body}
              </p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
