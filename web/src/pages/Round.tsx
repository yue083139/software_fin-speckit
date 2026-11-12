import { useEffect, useState } from "react";
import type { LeaderRow, RoundInfo } from "../types";

// 倒數只影響畫面：以伺服器給的截止時刻換算，截止以伺服器為準（mode-timed-scoring D7）
export function Countdown({ deadline }: { deadline: number }) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 250);
    return () => clearInterval(id);
  }, []);
  const left = Math.max(0, Math.ceil((deadline - now) / 1000));
  return <strong aria-label="剩餘秒數">{left} 秒</strong>;
}

export function RoundStatus({ round }: { round: RoundInfo | null | undefined }) {
  if (!round) return <p className="muted">目前沒有進行中的題目。</p>;
  return (
    <p>
      第 {round.question} 題：
      {round.state === "open" ? (
        <>
          作答中，剩 <Countdown deadline={round.deadline_epoch_ms} />
        </>
      ) : (
        "已結束作答，等待揭曉"
      )}
    </p>
  );
}

// 名次表：學生版只有名次（伺服器不送他組分數），老師版多一欄分數
export function Leaderboard({ rows, team }: { rows: LeaderRow[]; team?: string }) {
  if (rows.length === 0) return null;
  const withScores = rows.some((r) => r.score !== undefined);
  return (
    <table>
      <thead>
        <tr>
          <th>名次</th>
          <th>組別</th>
          {withScores && <th>累積分數</th>}
        </tr>
      </thead>
      <tbody>
        {rows.map((r) => (
          <tr key={r.team} className={r.team === team ? "winner" : undefined}>
            <td>{r.rank}</td>
            <td>{r.team}</td>
            {withScores && <td>{r.score}</td>}
          </tr>
        ))}
      </tbody>
    </table>
  );
}
