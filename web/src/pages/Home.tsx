import { Alert, Input } from "antd";
import { Shell } from "../Shell";
import { Btn, GlassHeader, Section } from "../ui";
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
        <label className="field" style={{ marginBottom: 12 }}>
          <span className="field-label">邀請碼（向組員或老師索取）</span>
          <Input size="large" value={code} onChange={(e) => setCode(e.target.value)} aria-label="邀請碼" maxLength={12} />
        </label>
      )}
      <div className="team-grid">
        {teams.map((t) => (
          <Btn key={t} disabled={!teamPlay && joined.includes(t)} onClick={() => onPick(t, code)}>
            {t}
            {joined.includes(t) && "（已加入）"}
          </Btn>
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
    <Shell>
      <GlassHeader title="課堂搶答" />
      <main className="qz-narrow">
        {error && <Alert type="error" showIcon message={error} />}
        <Section title="我是學生">
          <TeamPicker teams={teams} joined={joined} teamPlay={teamPlay} onPick={pick} />
        </Section>
        <Section title="我是老師">
          <div className="stack">
            <label className="field">
              <span className="field-label">老師金鑰（啟動伺服器時印在終端機）</span>
              <Input.Password value={key} onChange={(e) => setKey(e.target.value)} aria-label="老師金鑰" />
            </label>
            <Btn type="primary" href={`#/teacher?key=${encodeURIComponent(key)}`}>
              進入老師頁
            </Btn>
          </div>
        </Section>
      </main>
    </Shell>
  );
}
