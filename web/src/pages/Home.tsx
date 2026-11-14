import { useEffect, useState } from "react";
import { joinTeam, publicInfo, saveToken } from "../api";

// 選組：組隊時已加入的組別仍可按，第二台起要輸入該組邀請碼（team-mode D6）
export function TeamPicker({
  teams,
  joined,
  teamPlay,
  onPick,
}: {
  teams: string[];
  joined: string[];
  teamPlay: boolean;
  onPick: (team: string, code: string) => void;
}) {
  const [code, setCode] = useState("");
  return (
    <>
      <p>{teamPlay ? "選擇你的組別（組隊：同組可多台裝置，加入已有組員的組別要輸入邀請碼）：" : "選擇你的組別（每組一台裝置）："}</p>
      {teamPlay && (
        <label>
          邀請碼（向組員或老師索取）
          <input value={code} onChange={(e) => setCode(e.target.value)} aria-label="邀請碼" maxLength={12} />
        </label>
      )}
      <div className="team-grid">
        {teams.map((t) => (
          <button key={t} disabled={!teamPlay && joined.includes(t)} onClick={() => onPick(t, code)}>
            {t}
            {joined.includes(t) && "（已加入）"}
          </button>
        ))}
      </div>
    </>
  );
}

// 首頁：學生選組別取得組別憑證；老師輸入金鑰進場（app-skeleton spec「系統必須區分老師與學生兩種身分」）
export default function Home() {
  const [teams, setTeams] = useState<string[]>([]);
  const [joined, setJoined] = useState<string[]>([]);
  const [teamPlay, setTeamPlay] = useState(false);
  const [key, setKey] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    publicInfo()
      .then((i) => {
        setTeams(i.teams);
        setJoined(i.joined);
        setTeamPlay(!!i.team_play);
      })
      .catch(() => setError("連不上伺服器"));
  }, []);
  const pick = (team: string, code: string) => {
    setError("");
    joinTeam(team, code.trim() || undefined)
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
        <TeamPicker teams={teams} joined={joined} teamPlay={teamPlay} onPick={pick} />
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
