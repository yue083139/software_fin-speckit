import type { QuestionResult } from "../types";

function formatAnswers(labels: string[], answers: string[]): string {
  return answers.map((a, i) => `${labels[i] ?? ""}${a}`).join(" ／ ");
}

// 老師即時作答狀況表：列＝題號、欄＝組別，格內為答案與順位，得主加底色（results-view D4）
export function Board({
  board,
  teams,
  scores,
}: {
  board: QuestionResult[];
  teams: string[];
  scores: Record<string, number>;
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
                    {r.is_winner && <div className="tag">搶答成功</div>}
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
            <th>得題數</th>
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
}: {
  team: string;
  results: QuestionResult[];
  scores: Record<string, number>;
}) {
  return (
    <>
      <section className="card">
        <h2>搶答結果</h2>
        <p>
          本組得題數：<strong>{scores[team] ?? 0}</strong>
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
            <h3>第 {q.number} 題</h3>
            {q.winner ? (
              <p className={q.winner.team === team ? "ok" : undefined}>
                搶答成功：{q.winner.team}（{formatAnswers(q.labels, q.winner.answers)}）
              </p>
            ) : (
              <p className="muted">沒有組別搶答</p>
            )}
            <p>本組：{mine ? `第 ${mine.rank} 順位（${formatAnswers(q.labels, mine.answers)}）` : "未作答"}</p>
            {q.ranking.length > 0 && (
              <ol>
                {q.ranking.map((r) => (
                  <li key={r.team}>
                    {r.team}：{formatAnswers(q.labels, r.answers)}
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
