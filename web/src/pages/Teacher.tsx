import { useState } from "react";
import { teacherDownload, teacherPost, teacherUpload } from "../api";
import { ImportPanel } from "./ImportPanel";
import { Board } from "./Results";
import { useLiveView } from "../live";
import { PHASE_LABEL, type TeacherView } from "../types";

type Act = (path: string, body?: unknown) => void;

export function PhaseControls({ view, act, download }: { view: TeacherView; act: Act; download: () => void }) {
  return (
    <section className="card">
      <p className="phase">
        目前階段：<strong>{PHASE_LABEL[view.phase]}</strong>
      </p>
      <div className="row">
        <button disabled={view.phase !== "preparing"} onClick={() => act("start")}>
          開始搶答
        </button>
        <button disabled={view.phase !== "answering"} onClick={() => act("end")}>
          結束搶答
        </button>
        <button disabled={view.phase !== "ended"} onClick={() => act("reset")}>
          重置活動
        </button>
        <button disabled={view.phase !== "ended" || !view.source} onClick={download}>
          匯出 Guided Notes
        </button>
      </div>
      {view.phase === "ended" && (
        <p className="muted">
          匯出的 xlsx 已把每題搶答成功的答案寫入原填空格；放回 Google 試算表：檔案 → 匯入 → 上傳 → 取代試算表。
        </p>
      )}
    </section>
  );
}

export function TeamSettings({ view, act }: { view: TeacherView; act: Act }) {
  const [count, setCount] = useState(view.teams.length);
  return (
    <section className="card">
      <h2>組別</h2>
      <ul className="team-list">
        {view.teams.map((t) => (
          <li key={t}>
            {t}：{view.joined.includes(t) ? "已加入" : <span className="muted">未加入</span>}
            {view.joined.includes(t) && (
              <button className="small" onClick={() => act("release", { team: t })}>
                釋放
              </button>
            )}
          </li>
        ))}
      </ul>
      <label>
        組數（2–12）
        <input
          type="number"
          min={2}
          max={12}
          value={count}
          onChange={(e) => setCount(Number(e.target.value))}
          aria-label="組數"
        />
      </label>
      <button disabled={view.phase !== "preparing"} onClick={() => act("teams", { count })}>
        設定組數
      </button>
    </section>
  );
}

type Upload = (file: File) => void;

export function TeacherPanel({
  view,
  act,
  upload,
  download = () => {},
}: {
  view: TeacherView;
  act: Act;
  upload: Upload;
  download?: () => void;
}) {
  return (
    <>
      <PhaseControls view={view} act={act} download={download} />
      <section className="card">
        <h2>作答狀況與結果</h2>
        <Board board={view.board} teams={view.teams} scores={view.team_scores} />
      </section>
      <ImportPanel view={view} onUpload={upload} onUrl={(url) => act("import-url", { url })} />
      <TeamSettings view={view} act={act} />
    </>
  );
}

export default function Teacher({ teacherKey }: { teacherKey: string }) {
  const { view, closedCode } = useLiveView(`role=teacher&key=${encodeURIComponent(teacherKey)}`);
  const [error, setError] = useState("");
  const act: Act = (path, body) => {
    setError("");
    teacherPost(path, teacherKey, body).catch((e: Error) => setError(e.message));
  };
  const upload: Upload = (file) => {
    setError("");
    teacherUpload(teacherKey, file).catch((e: Error) => setError(e.message));
  };
  const download = () => {
    setError("");
    teacherDownload(teacherKey).catch((e: Error) => setError(e.message));
  };
  if (closedCode === 4401)
    return (
      <main className="page">
        <p className="error">老師金鑰錯誤，請回首頁重新輸入。</p>
      </main>
    );
  return (
    <main className="page">
      <h1>老師頁</h1>
      {error && <p className="error">{error}</p>}
      {view?.role === "teacher" ? <TeacherPanel view={view} act={act} upload={upload} download={download} /> : <p>連線中…</p>}
    </main>
  );
}
