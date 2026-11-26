import { UploadOutlined } from "@ant-design/icons";
import { Checkbox, Input, Upload } from "antd";
import { useState } from "react";
import type { QuestionOutline, TeacherView } from "../types";
import { Btn, Section } from "../ui";

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
    <Section id="import" title="題目與匯入">
      <div className="stack">
        {locked && <p className="muted" style={{ margin: 0 }}>只能在準備階段匯入。</p>}
        <div className="row">
          <Input
            style={{ flex: 1, minWidth: 260 }}
            placeholder="https://docs.google.com/spreadsheets/d/…"
            aria-label="Google 試算表連結"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />
          <Btn type="primary" disabled={locked || !googleReady || !url.trim()} onClick={() => onUrl(url.trim())}>
            從 Google 試算表匯入
          </Btn>
        </div>
        <p className="muted" style={{ margin: 0 }}>
          {googleReady
            ? "匯入時會在你的雲端硬碟複製一份「<原標題>-搶答結果」，結束後答案寫進這份副本，原試算表不動；搶答結束前請勿改副本版面。"
            : "先以 Google 帳號登入才能從試算表匯入。"}
        </p>
        {sheetUrl && (
          <p style={{ margin: 0 }}>
            副本：
            <a href={sheetUrl} target="_blank" rel="noreferrer">
              開啟 Google 試算表副本
            </a>
          </p>
        )}
        <div className="row">
          <span className="muted">備援：</span>
          <Upload
            accept=".xlsx"
            maxCount={1}
            beforeUpload={(f) => {
              setFile(f);
              return false; // 只選檔，按「上傳 xlsx」才送
            }}
            onRemove={() => setFile(null)}
          >
            <Btn icon={<UploadOutlined />} aria-label="Guided Notes 檔案">
              選擇 xlsx 檔
            </Btn>
          </Upload>
          <Btn disabled={locked || !file} onClick={() => file && onUpload(file)}>
            上傳 xlsx
          </Btn>
        </div>
        {view.source && (
          <p style={{ margin: 0 }}>
            目前題目來源：<strong>{view.source}</strong>，共 {view.questions.length} 題
          </p>
        )}
        <QuestionList
          questions={view.questions}
          onDouble={locked ? undefined : (question, on) => onSettings?.(question, on ? 2 : 1)}
          onTimeLimit={locked ? undefined : onTimeLimit}
        />
      </div>
    </Section>
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
          <span style={{ flex: "1 1 260px", minWidth: 0 }}>
            第 {q.number} 題{q.labels.length > 1 ? `（題組，${q.labels.length} 個子題：${q.labels.join("、")}）` : ""}
            {q.prompts?.some((p) => p) && (
              <span className="muted" style={{ display: "block", whiteSpace: "pre-wrap" }}>
                {q.prompts.filter((p) => p).join("\n")}
              </span>
            )}
          </span>
          {onDouble ? (
            <Checkbox
              aria-label={`第 ${q.number} 題雙倍分數`}
              checked={q.multiplier === 2}
              onChange={(e) => onDouble(q.number, e.target.checked)}
            >
              雙倍分數
            </Checkbox>
          ) : (
            <DoubleTag multiplier={q.multiplier} />
          )}
          {onTimeLimit && (
            <label className="inline">
              時限
              <Input
                type="number"
                min={5}
                max={120}
                aria-label={`第 ${q.number} 題時限`}
                defaultValue={q.time_limit ?? 20}
                onBlur={(e) => onTimeLimit(q.number, Number(e.target.value))}
                style={{ width: 80 }}
              />
              秒
            </label>
          )}
        </li>
      ))}
    </ol>
  );
}
