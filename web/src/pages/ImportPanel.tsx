import { useState } from "react";
import type { QuestionOutline, TeacherView } from "../types";

// 老師匯入 Guided Notes：已登入 Google 時直接讀雲端試算表（匯入時建立副本），上傳 xlsx 為備援
// （guided-notes-import、guided-notes-sheets-sync D4）
export function ImportPanel({
  view,
  onUpload,
  onUrl,
  onSettings,
  onTimeLimit,
  googleReady = false,
  sheetUrl,
}: {
  view: TeacherView;
  onUpload: (file: File) => void;
  onUrl: (url: string) => void;
  onSettings?: (question: number, multiplier: number) => void;
  onTimeLimit?: (question: number, seconds: number) => void;
  googleReady?: boolean;
  sheetUrl?: string | null;
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
          style={{ flex: 1, minWidth: 260 }}
          placeholder="https://docs.google.com/spreadsheets/d/…"
          aria-label="Google 試算表連結"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button disabled={locked || !googleReady || !url.trim()} onClick={() => onUrl(url.trim())}>
          從 Google 試算表匯入
        </button>
      </div>
      <p className="muted">
        {googleReady
          ? "匯入時會在你的雲端硬碟複製一份「<原標題>-搶答結果」，結束後答案寫進這份副本，原試算表不動；搶答結束前請勿改副本版面。"
          : "先以 Google 帳號登入才能從試算表匯入。"}
      </p>
      {sheetUrl && (
        <p>
          副本：
          <a href={sheetUrl} target="_blank" rel="noreferrer">
            開啟 Google 試算表副本
          </a>
        </p>
      )}
      <div className="row">
        <span className="muted">備援：</span>
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
      {view.source && (
        <p>
          目前題目來源：<strong>{view.source}</strong>，共 {view.questions.length} 題
        </p>
      )}
      <QuestionList
        questions={view.questions}
        onDouble={locked ? undefined : (question, on) => onSettings?.(question, on ? 2 : 1)}
        onTimeLimit={locked ? undefined : onTimeLimit}
      />
    </section>
  );
}

export function DoubleTag({ multiplier }: { multiplier?: number }) {
  return multiplier === 2 ? <span className="tag">雙倍分數</span> : null;
}

// 題目清單；老師在準備階段可勾「雙倍分數」（question-settings D4），學生只看標記
export function QuestionList({
  questions,
  onDouble,
  onTimeLimit,
}: {
  questions: QuestionOutline[];
  onDouble?: (question: number, on: boolean) => void;
  onTimeLimit?: (question: number, seconds: number) => void;
}) {
  if (questions.length === 0) return <p className="muted">尚未匯入題目。</p>;
  return (
    <ol className="question-list">
      {questions.map((q) => (
        <li key={q.number} value={q.number}>
          第 {q.number} 題{q.labels.length > 1 ? `（題組，${q.labels.length} 個子題：${q.labels.join("、")}）` : ""}
          {onDouble ? (
            <label className="inline">
              <input
                type="checkbox"
                aria-label={`第 ${q.number} 題雙倍分數`}
                checked={q.multiplier === 2}
                onChange={(e) => onDouble(q.number, e.target.checked)}
              />
              雙倍分數
            </label>
          ) : (
            <DoubleTag multiplier={q.multiplier} />
          )}
          {onTimeLimit && (
            <label className="inline">
              時限
              <input
                type="number"
                min={5}
                max={120}
                aria-label={`第 ${q.number} 題時限`}
                defaultValue={q.time_limit ?? 20}
                onBlur={(e) => onTimeLimit(q.number, Number(e.target.value))}
                style={{ width: 64 }}
              />
              秒
            </label>
          )}
        </li>
      ))}
    </ol>
  );
}
