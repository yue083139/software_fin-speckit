import { useState } from "react";
import type { QuestionOutline } from "../types";

export type Submit = (question: number, answers: string[]) => Promise<unknown>;

// 學生作答：題組一次送出全部子題；送出後鎖定（buzz-answering D1、D4）。
// 畫面只顯示本組資料，伺服器在搶答結束前不會送任何他組資訊。
export function AnswerForm({
  questions,
  submitted,
  onSubmit,
}: {
  questions: QuestionOutline[];
  submitted: { question: number; answers: string[] }[];
  onSubmit: Submit;
}) {
  return (
    <div>
      {questions.map((q) => {
        const mine = submitted.find((s) => s.question === q.number);
        return (
          <QuestionCard key={q.number} question={q} submitted={mine?.answers} onSubmit={onSubmit} />
        );
      })}
    </div>
  );
}

function QuestionCard({
  question,
  submitted,
  onSubmit,
}: {
  question: QuestionOutline;
  submitted?: string[];
  onSubmit: Submit;
}) {
  const [values, setValues] = useState<string[]>(() => question.labels.map(() => ""));
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const ready = values.every((v) => v.trim() !== "");
  const send = () => {
    setBusy(true);
    setError("");
    onSubmit(question.number, values)
      .catch((e: Error) => setError(e.message))
      .finally(() => setBusy(false));
  };
  return (
    <section className="card">
      <h3>
        第 {question.number} 題{question.labels.length > 1 ? "（題組）" : ""}
      </h3>
      {submitted ? (
        <p className="ok">
          已送出：{submitted.map((a, i) => `${question.labels[i] ?? ""}${a}`).join("　")}
        </p>
      ) : (
        <>
          {question.labels.map((label, i) => (
            <label key={i}>
              {label || "答案"}
              <input
                aria-label={`第 ${question.number} 題 ${label || "答案"}`}
                value={values[i]}
                maxLength={200}
                onChange={(e) => setValues(values.map((v, j) => (j === i ? e.target.value : v)))}
              />
            </label>
          ))}
          <button disabled={!ready || busy} onClick={send}>
            搶答送出
          </button>
          {error && <p className="error">{error}</p>}
        </>
      )}
    </section>
  );
}
