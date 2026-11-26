import type { QuestionOutline } from "../types";

/** question-text D5：題目敘述以純文字顯示；伺服器沒帶或為空字串就不顯示。 */
export function PromptText({ text }: { text?: string }) {
  if (!text) return null;
  return <p className="prompt">{text}</p>;
}

/** 依題號取伺服器給的敘述；可見性只由伺服器決定，這裡不重算。 */
export function promptsOf(questions: QuestionOutline[] | undefined, number: number): string[] {
  return questions?.find((q) => q.number === number)?.prompts ?? [];
}

/** 題組各子題敘述併成一段（結果表用）。 */
export function PromptSummary({ prompts, labels }: { prompts: string[]; labels: string[] }) {
  const parts = prompts.map((p, i) => (p ? `${labels.length > 1 ? (labels[i] ?? "") : ""}${p}` : "")).filter(Boolean);
  if (parts.length === 0) return null;
  return <div className="prompt">{parts.join("\n")}</div>;
}
