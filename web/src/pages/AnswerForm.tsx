import { PromptText } from "./Prompts";
import { useEffect, useRef, useState } from "react";
import type { Draft as DraftRow, QuestionOutline } from "../types";
import { DoubleTag } from "./ImportPanel";
import { Alert, Input } from "antd";
import { Btn, Section } from "../ui";

export type Submit = (question: number, answers: string[]) => Promise<unknown>;
export type Draft = (question: number, answers: string[]) => void;

const DRAFT_DELAY_MS = 400;

// 學生作答：題組一次送出全部子題；送出後鎖定（buzz-answering D1、D4）。
// 畫面只顯示本組資料，伺服器在搶答結束前不會送任何他組資訊。
// 組隊時（onDraft 有值）輸入會防抖送出組內草稿，並顯示伺服器推來的本組草稿（team-mode D6）。
export function AnswerForm({
  questions,
  submitted,
  onSubmit,
  drafts,
  onDraft,
}: {
  questions: QuestionOutline[];
  submitted: { question: number; answers: string[] }[];
  onSubmit: Submit;
  drafts?: DraftRow[];
  onDraft?: Draft;
}) {
  return (
    <div>
      {questions.map((q) => {
        const mine = submitted.find((s) => s.question === q.number);
        return (
          <QuestionCard
            key={q.number}
            question={q}
            submitted={mine?.answers}
            onSubmit={onSubmit}
            teamDraft={drafts?.find((d) => d.question === q.number)?.answers}
            onDraft={onDraft}
          />
        );
      })}
    </div>
  );
}

function QuestionCard({
  question,
  submitted,
  onSubmit,
  teamDraft,
  onDraft,
}: {
  question: QuestionOutline;
  submitted?: string[];
  onSubmit: Submit;
  teamDraft?: string[];
  onDraft?: Draft;
}) {
  const [values, setValues] = useState<string[]>(() => question.labels.map(() => ""));
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelDraft = () => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = null;
  };
  useEffect(() => cancelDraft, []);
  const ready = values.every((v) => v.trim() !== "");
  const change = (next: string[]) => {
    setValues(next);
    if (!onDraft) return;
    cancelDraft();
    timer.current = setTimeout(() => {
      timer.current = null;
      onDraft(question.number, next);
    }, DRAFT_DELAY_MS);
  };
  const send = () => {
    cancelDraft(); // 送出後不再補送草稿
    setBusy(true);
    setError("");
    onSubmit(question.number, values)
      .catch((e: Error) => setError(e.message))
      .finally(() => setBusy(false));
  };
  const showDraft = onDraft && teamDraft && teamDraft.some((v) => v !== "") && teamDraft.join("\u0000") !== values.join("\u0000");
  return (
    <Section>
      <h3>
        第 {question.number} 題{question.labels.length > 1 ? "（題組）" : ""}
        <DoubleTag multiplier={question.multiplier} />
      </h3>
      {submitted ? (
        <Alert
          type="success"
          showIcon
          message={<span className="ok">已送出：{submitted.map((a, i) => `${question.labels[i] ?? ""}${a}`).join(" ／ ")}</span>}
        />
      ) : (
        <div className="stack">
          {question.labels.map((label, i) => (
            <label key={i} className="qz-answer-row">
              <PromptText text={question.prompts?.[i]} />
              <span className="qz-answer-label">{label || "答案"}</span>
              <Input
                size="large"
                aria-label={`第 ${question.number} 題 ${label || "答案"}`}
                value={values[i]}
                maxLength={200}
                onChange={(e) => change(values.map((v, j) => (j === i ? e.target.value : v)))}
              />
            </label>
          ))}
          {showDraft && (
            <p className="muted" style={{ margin: 0 }}>
              組內草稿：{teamDraft.map((a, i) => `${question.labels[i] ?? ""}${a}`).join(" ／ ")}{" "}
              <Btn size="small" onClick={() => setValues([...teamDraft])}>
                套用
              </Btn>
            </p>
          )}
          <Btn type="primary" size="large" block disabled={!ready || busy} loading={busy} onClick={send}>
            搶答送出
          </Btn>
          {error && <Alert type="error" showIcon message={<span className="error">{error}</span>} />}
        </div>
      )}
    </Section>
  );
}
