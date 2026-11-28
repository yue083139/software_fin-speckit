import type { TeacherView } from "./types";

const CSV_HEADERS = ["題號", "組別", "答案", "順位", "是否得主", "判定結果", "本題得分", "活動總分"];

function csvCell(value: string | number): string {
  let text = String(value);
  if (/^[\t\r\n ]*[=+\-@]/.test(text)) text = `'${text}`;
  return `"${text.replace(/"/g, '""')}"`;
}

export function buildResultsCsv(view: TeacherView): string {
  const rows: (string | number)[][] = [CSV_HEADERS];

  for (const question of view.board) {
    const rankedByTeam = new Map(question.ranking.map((ranked) => [ranked.team, ranked]));
    for (const team of view.teams) {
      const ranked = rankedByTeam.get(team);
      const answer = ranked
        ? ranked.answers
            .map((value, index) => `${question.labels[index] ?? ""}${value}`)
            .join(" ／ ")
        : "";
      rows.push([
        question.number,
        team,
        answer,
        ranked?.rank ?? "",
        ranked?.is_winner ? "是" : "否",
        ranked?.correct == null ? "" : ranked.correct ? "正確" : "錯誤",
        ranked?.score ?? 0,
        view.team_scores[team] ?? 0,
      ]);
    }
  }

  return `\uFEFF${rows.map((row) => row.map(csvCell).join(",")).join("\r\n")}\r\n`;
}

export function resultsCsvFilename(source: string | null): string {
  if (!source) return "活動結果.csv";
  const stem = source.replace(/\.[^.]+$/, "");
  const safeStem = stem
    .replace(/[<>:"/\\|?*]/g, "_")
    .split("")
    .map((character) => (character.charCodeAt(0) < 32 ? "_" : character))
    .join("")
    .replace(/[. ]+$/, "");
  return `${safeStem || "活動結果"}_活動結果.csv`;
}

export function downloadResultsCsv(view: TeacherView): void {
  const blob = new Blob([buildResultsCsv(view)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = resultsCsvFilename(view.source);
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 1_000);
}
