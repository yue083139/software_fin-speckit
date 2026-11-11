import { useEffect, useState } from "react";
import { joinTeam, publicInfo, saveToken } from "../api";

// 首頁：學生選組別取得組別憑證；老師輸入金鑰進場（app-skeleton spec「系統必須區分老師與學生兩種身分」）
export default function Home() {
  const [teams, setTeams] = useState<string[]>([]);
  const [joined, setJoined] = useState<string[]>([]);
  const [key, setKey] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    publicInfo()
      .then((i) => {
        setTeams(i.teams);
        setJoined(i.joined);
      })
      .catch(() => setError("連不上伺服器"));
  }, []);
  const pick = (team: string) => {
    setError("");
    joinTeam(team)
      .then((r) => {
        saveToken(r.token);
        location.hash = "#/student";
      })
      .catch((e: Error) => setError(e.message));
  };
  return (
    <main className="page">
      <h1>課堂搶答</h1>
      {error && <p className="error">{error}</p>}
      <section className="card">
        <h2>我是學生</h2>
        <p>選擇你的組別（每組一台裝置）：</p>
        <div className="team-grid">
          {teams.map((t) => (
            <button key={t} disabled={joined.includes(t)} onClick={() => pick(t)}>
              {t}
              {joined.includes(t) && "（已加入）"}
            </button>
          ))}
        </div>
      </section>
      <section className="card">
        <h2>我是老師</h2>
        <label>
          老師金鑰（啟動伺服器時印在終端機）
          <input value={key} onChange={(e) => setKey(e.target.value)} aria-label="老師金鑰" />
        </label>
        <a className="button" href={`#/teacher?key=${encodeURIComponent(key)}`}>
          進入老師頁
        </a>
      </section>
    </main>
  );
}
