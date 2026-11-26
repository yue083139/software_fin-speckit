import { PromptSummary, promptsOf } from "./Prompts";
import type { QuestionOutline, QuestionResult, RankedAnswer } from "../types";

export type Judge = (question: number, team: string, correct: boolean) => void;

function formatAnswers(labels: string[], answers: string[]): string {
  return answers.map((a, i) => `${labels[i] ?? ""}${a}`).join(" ／ ");
}

function verdict(correct: boolean | null | undefined): string {
  if (correct === true) return "✓ 正確";
  if (correct === false) return "✗ 錯誤";
  return "";
}

// 判定中每格的建議與「正確／錯誤」鈕（game-mode-framework D8）；建議只來自老師 view
function JudgeCell({ question, r, onJudge }: { question: number; r: RankedAnswer; onJudge: Judge }) {
  return (
    <div className="row">
      {r.suggestion != null && <span className="muted">建議：{r.suggestion ? "正確" : "錯誤"}</span>}
      <button
        className={r.correct === true ? "small selected" : "small"}
        aria-label={`第 ${question} 題 ${r.team} 正確`}
        onClick={() => onJudge(question, r.team, true)}
      >
        正確
      </button>
      <button
        className={r.correct === false ? "small selected" : "small"}
        aria-label={`第 ${question} 題 ${r.team} 錯誤`}
        onClick={() => onJudge(question, r.team, false)}
      >
        錯誤
      </button>
    </div>
  );
}

// 老師即時作答狀況表：列＝題號、欄＝組別，格內為答案與順位，得主加底色（results-view D4）
export function Board({
  board,
  teams,
  scores,
  scoreLabel = "得題數",
  winnerTag = "搶答成功",
  onJudge,
  judgeQuestion,
  questions,
}: {
  board: QuestionResult[];
  questions?: QuestionOutline[];
  teams: string[];
  scores: Record<string, number>;
  scoreLabel?: string;
  winnerTag?: string;
  onJudge?: Judge;
  judgeQuestion?: number; // 逐題模式只能判定目前那一題
}) {
  if (board.length === 0) return <p className="muted">尚未匯入題目。</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>題號</th>
            {teams.map((t) => (
              <th key={t}>{t}</th>
            ))}
            <th>已送出</th>
          </tr>
        </thead>
        <tbody>
          {board.map((q) => (
            <tr key={q.number}>
              <th>
                {q.number}
                {q.labels.length > 1 && <span className="muted">（題組）</span>}
                {q.multiplier === 2 && <span className="tag">×2</span>}
                <PromptSummary prompts={promptsOf(questions, q.number)} labels={q.labels} />
                {q.reference?.some((x) => x != null) && (
                  <div className="muted">參考答案：{q.reference.map((x) => x ?? "—").join(" ／ ")}</div>
                )}
              </th>
              {teams.map((t) => {
                const r = q.ranking.find((x) => x.team === t);
                if (!r)
                  return (
                    <td key={t} className="muted">
                      —
                    </td>
                  );
                return (
                  <td key={t} className={r.is_winner ? "winner" : undefined}>
                    <div>{formatAnswers(q.labels, r.answers)}</div>
                    <div className="muted">第 {r.rank} 順位</div>
                    {r.is_winner && <div className="tag">{winnerTag}</div>}
                    {onJudge && (judgeQuestion === undefined || judgeQuestion === q.number) ? (
                      <JudgeCell question={q.number} r={r} onJudge={onJudge} />
                    ) : (
                      r.correct != null && <div>{verdict(r.correct)}</div>
                    )}
                  </td>
                );
              })}
              <td>
                {q.ranking.length} / {teams.length}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th>{scoreLabel}</th>
            {teams.map((t) => (
              <td key={t}>
                <strong>{scores[t] ?? 0}</strong>
              </td>
            ))}
            <td />
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

// 學生結束後的結果畫面（results-view D3、D4）
export function StudentResults({
  team,
  results,
  scores,
  scoreLabel = "得題數",
  winnerTag = "搶答成功",
  questions,
}: {
  team: string;
  results: QuestionResult[];
  questions?: QuestionOutline[];
  scores: Record<string, number>;
  scoreLabel?: string;
  winnerTag?: string;
}) {
  return (
    <>
      <section className="card">
        <h2>搶答結果</h2>
        <p>
          本組{scoreLabel}：<strong>{scores[team] ?? 0}</strong>
        </p>
        <p className="muted">
          各組：
          {Object.entries(scores)
            .map(([t, s]) => `${t} ${s}`)
            .join("、")}
        </p>
      </section>
      {results.map((q) => {
        const mine = q.ranking.find((r) => r.team === team);
        return (
          <section className="card" key={q.number}>
            <h3>
              第 {q.number} 題{q.multiplier === 2 && <span className="tag">雙倍分數</span>}
            </h3>
            <PromptSummary prompts={promptsOf(questions, q.number)} labels={q.labels} />
            {q.winner ? (
              <p className={q.winner.team === team ? "ok" : undefined}>
                {winnerTag}：{q.winner.team}（{formatAnswers(q.labels, q.winner.answers)}）
              </p>
            ) : (
              <p className="muted">{winnerTag === "搶答成功" ? "沒有組別搶答" : "沒有組別答對"}</p>
            )}
            <p>
              本組：
              {mine
                ? `第 ${mine.rank} 順位（${formatAnswers(q.labels, mine.answers)}）${mine.correct != null ? ` ${verdict(mine.correct)}` : ""}`
                : "未作答"}
            </p>
            {q.ranking.length > 0 && (
              <ol>
                {q.ranking.map((r) => (
                  <li key={r.team}>
                    {r.team}：{formatAnswers(q.labels, r.answers)}
                    {r.correct != null && ` ${verdict(r.correct)}`}
                  </li>
                ))}
              </ol>
            )}
          </section>
        );
      })}
    </>
  );
}
