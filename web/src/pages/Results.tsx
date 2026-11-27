import { Table, Tag } from "antd";
import type { ColumnsType } from "antd/es/table";
import { Podium } from "./Podium";
import { PromptSummary, promptsOf } from "./Prompts";
import type { QuestionOutline, QuestionResult, RankedAnswer } from "../types";
import { Btn, Section } from "../ui";

export type Judge = (question: number, team: string, correct: boolean) => void;
export type ReviewReset = (question: number) => void;

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
      <Btn
        size="small"
        type={r.correct === true ? "primary" : "default"}
        aria-label={`第 ${question} 題 ${r.team} 正確`}
        onClick={() => onJudge(question, r.team, true)}
      >
        正確
      </Btn>
      <Btn
        size="small"
        danger={r.correct === false}
        type={r.correct === false ? "primary" : "default"}
        aria-label={`第 ${question} 題 ${r.team} 錯誤`}
        onClick={() => onJudge(question, r.team, false)}
      >
        錯誤
      </Btn>
    </div>
  );
}

// 經典搶答結束後依順位檢查（answer-review）：只有候選格有「答對／答錯」，狀態全來自伺服器的 review
function ReviewCell({ q, r, onReview }: { q: QuestionResult; r: RankedAnswer; onReview: Judge }) {
  const review = q.review;
  if (!review) return null;
  if (review.rejected.includes(r.team)) return <div className="error">✗ 答錯</div>;
  if (review.candidate !== r.team) return null;
  if (review.locked)
    return (
      <div className="ok">
        ✓ 答對 <Tag color="success">已鎖定</Tag>
      </div>
    );
  return (
    <div className="stack" style={{ gap: 4 }}>
      <Tag color="processing">檢查中</Tag>
      <div className="row">
        <Btn size="small" type="primary" aria-label={`第 ${q.number} 題 ${r.team} 答對`} onClick={() => onReview(q.number, r.team, true)}>
          答對
        </Btn>
        <Btn size="small" danger aria-label={`第 ${q.number} 題 ${r.team} 答錯`} onClick={() => onReview(q.number, r.team, false)}>
          答錯
        </Btn>
      </div>
    </div>
  );
}

function ReviewSummary({ q, onReset }: { q: QuestionResult; onReset: ReviewReset }) {
  const review = q.review;
  if (!review) return null;
  const allWrong = review.candidate === null && q.ranking.length > 0;
  const touched = review.locked || review.rejected.length > 0;
  return (
    <div className="stack" style={{ gap: 4 }}>
      {allWrong && <div className="error">全部答錯，無得主</div>}
      {touched && (
        <Btn size="small" aria-label={`第 ${q.number} 題 重設本題`} onClick={() => onReset(q.number)}>
          重設本題
        </Btn>
      )}
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
  onReview,
  onReviewReset,
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
  onReview?: Judge; // 經典搶答結束後才給（answer-review）
  onReviewReset?: ReviewReset;
}) {
  if (board.length === 0) return <p className="muted">尚未匯入題目。</p>;
  const columns: ColumnsType<QuestionResult> = [
    {
      title: "題號",
      key: "number",
      fixed: "left",
      width: 220,
      render: (_, q) => (
        <div>
          <strong>{q.number}</strong>
          {q.labels.length > 1 && <span className="muted">（題組）</span>}
          {q.multiplier === 2 && <span className="tag">×2</span>}
          <PromptSummary prompts={promptsOf(questions, q.number)} labels={q.labels} />
          {q.reference?.some((x) => x != null) && (
            <div className="muted">參考答案：{q.reference.map((x) => x ?? "—").join(" ／ ")}</div>
          )}
          {onReview && onReviewReset && <ReviewSummary q={q} onReset={onReviewReset} />}
        </div>
      ),
    },
    ...teams.map((t) => ({
      title: t,
      key: t,
      width: 180,
      onCell: (q: QuestionResult) => ({
        className: q.ranking.find((x) => x.team === t)?.is_winner ? "winner" : undefined,
      }),
      render: (_: unknown, q: QuestionResult) => {
        const r = q.ranking.find((x) => x.team === t);
        if (!r) return <span className="muted">—</span>;
        return (
          <div className="stack" style={{ gap: 4 }}>
            <div>{formatAnswers(q.labels, r.answers)}</div>
            <div className="muted">第 {r.rank} 順位</div>
            {r.is_winner && <div className="tag">{winnerTag}</div>}
            {onReview && q.review ? (
              <ReviewCell q={q} r={r} onReview={onReview} />
            ) : onJudge && (judgeQuestion === undefined || judgeQuestion === q.number) ? (
              <JudgeCell question={q.number} r={r} onJudge={onJudge} />
            ) : (
              r.correct != null && <div>{verdict(r.correct)}</div>
            )}
          </div>
        );
      },
    })),
    {
      title: "已送出",
      key: "count",
      width: 90,
      render: (_, q) => (
        <Tag className="qz-pill" color={q.ranking.length === teams.length ? "success" : "default"}>
          {q.ranking.length} / {teams.length}
        </Tag>
      ),
    },
  ];
  return (
    <Table<QuestionResult>
      className="table-wrap"
      rowKey="number"
      size="middle"
      bordered
      pagination={false}
      scroll={{ x: "max-content" }}
      columns={columns}
      dataSource={board}
      summary={() => (
        <Table.Summary.Row>
          <Table.Summary.Cell index={0}>
            <strong>{scoreLabel}</strong>
          </Table.Summary.Cell>
          {teams.map((t, i) => (
            <Table.Summary.Cell index={i + 1} key={t}>
              <strong>{scores[t] ?? 0}</strong>
            </Table.Summary.Cell>
          ))}
          <Table.Summary.Cell index={teams.length + 1} />
        </Table.Summary.Row>
      )}
    />
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
      <Section title="搶答結果">
        <div className="qz-stat">
          <div>
            <span className="muted">本組{scoreLabel}</span>
            <strong>{scores[team] ?? 0}</strong>
          </div>
        </div>
        <p className="muted">
          各組：
          {Object.entries(scores)
            .map(([t, s]) => `${t} ${s}`)
            .join("、")}
        </p>
      </Section>
      <Podium scores={scores} scoreLabel={scoreLabel} team={team} />
      {results.map((q) => {
        const mine = q.ranking.find((r) => r.team === team);
        return (
          <Section key={q.number}>
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
              <ol className="question-list">
                {q.ranking.map((r) => (
                  <li key={r.team} className={r.is_winner ? "winner" : undefined}>
                    {r.team}：{formatAnswers(q.labels, r.answers)}
                    {r.correct != null && ` ${verdict(r.correct)}`}
                  </li>
                ))}
              </ol>
            )}
          </Section>
        );
      })}
    </>
  );
}
