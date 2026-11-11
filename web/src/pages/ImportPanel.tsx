import { useState } from "react";
import type { QuestionOutline, TeacherView } from "../types";

// 老師匯入 Guided Notes：上傳 xlsx 或貼 Google 試算表連結（guided-notes-import）
export function ImportPanel({
  view,
  onUpload,
  onUrl,
}: {
  view: TeacherView;
  onUpload: (file: File) => void;
  onUrl: (url: string) => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const locked = view.phase !== "preparing";
  return (
    <section className="card">
      <h2>匯入 Guided Notes</h2>
      {locked && <p className="muted">只能在準備階段匯入。</p>}
      <div className="row">
        <input
          type="file"
          accept=".xlsx"
          aria-label="Guided Notes 檔案"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        <button disabled={locked || !file} onClick={() => file && onUpload(file)}>
          上傳 xlsx
        </button>
      </div>
      <div className="row">
        <input
          style={{ flex: 1, minWidth: 260 }}
          placeholder="https://docs.google.com/spreadsheets/d/…（知道連結者可檢視）"
          aria-label="Google 試算表連結"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button disabled={locked || !url.trim()} onClick={() => onUrl(url.trim())}>
          從連結匯入
        </button>
      </div>
      {view.source && (
        <p>
          目前題目來源：<strong>{view.source}</strong>，共 {view.questions.length} 題
        </p>
      )}
      <QuestionList questions={view.questions} />
    </section>
  );
}

export function QuestionList({ questions }: { questions: QuestionOutline[] }) {
  if (questions.length === 0) return <p className="muted">尚未匯入題目。</p>;
  return (
    <ol className="question-list">
      {questions.map((q) => (
        <li key={q.number} value={q.number}>
          第 {q.number} 題{q.labels.length > 1 ? `（題組，${q.labels.length} 個子題：${q.labels.join("、")}）` : ""}
        </li>
      ))}
    </ol>
  );
}
