import { Table } from "antd";
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
    <Table<LeaderRow>
      rowKey="team"
      size="small"
      pagination={false}
      dataSource={rows}
      rowClassName={(r) => (r.team === team ? "winner" : "")}
      columns={[
        { title: "名次", dataIndex: "rank", width: 72 },
        { title: "組別", dataIndex: "team" },
        ...(withScores ? [{ title: "累積分數", dataIndex: "score" }] : []),
      ]}
    />
  );
}
