import { useCallback, useEffect, useRef, useState } from "react";
import { type GoogleStatus, googleStatus, teacherDownload, teacherPost, teacherUpload } from "../api";
import { GooglePanel } from "./GooglePanel";
import { ImportPanel } from "./ImportPanel";
import { Board, type Judge } from "./Results";
import { Leaderboard, RoundStatus } from "./Round";
import { useLiveView } from "../live";
import { PHASE_LABEL, type TeacherView } from "../types";

type Act = (path: string, body?: unknown) => void;

export function PhaseControls({
  view,
  act,
  download,
  exportSheet,
}: {
  view: TeacherView;
  act: Act;
  download: () => void;
  exportSheet?: () => void;
}) {
  return (
    <section className="card">
      <p className="phase">
        目前階段：<strong>{PHASE_LABEL[view.phase]}</strong>
      </p>
      <div className="row">
        <button disabled={view.phase !== "preparing"} onClick={() => act("start")}>
          開始搶答
        </button>
        {view.mode?.sequential && (
          <>
            <button disabled={view.phase !== "answering" || !!view.round} onClick={() => act("open-next")}>
              開放下一題
            </button>
            <button disabled={view.round?.state !== "open"} onClick={() => act("close-question")}>
              提早結束本題
            </button>
            <button disabled={view.round?.state !== "closed"} onClick={() => act("accept-suggestions")}>
              採用全部建議
            </button>
            <button
              disabled={view.round?.state !== "closed" || (view.pending_judgments ?? 0) > 0}
              onClick={() => act("reveal-question")}
            >
              揭曉本題
            </button>
          </>
        )}
        <button disabled={view.phase !== "answering" || !!view.round} onClick={() => act("end")}>
          {view.mode?.sequential ? "結束活動" : "結束搶答"}
        </button>
        {view.mode?.judged && (
          <>
            <button disabled={view.phase !== "judging"} onClick={() => act("accept-suggestions")}>
              採用全部建議
            </button>
            <button
              disabled={view.phase !== "judging" || (view.pending_judgments ?? 0) > 0}
              onClick={() => act("reveal")}
            >
              揭曉結果
            </button>
          </>
        )}
        <button disabled={view.phase !== "ended"} onClick={() => act("reset")}>
          重置活動
        </button>
        {exportSheet && (
          <button disabled={view.phase !== "ended" || !view.source} onClick={exportSheet}>
            匯出到 Google 試算表
          </button>
        )}
        <button disabled={view.phase !== "ended" || !view.source} onClick={download}>
          下載 xlsx（備援）
        </button>
      </div>
      {view.mode?.sequential && view.phase === "answering" && (
        <>
          <RoundStatus round={view.round} />
          {view.round?.state === "closed" && (
            <p>
              尚有 <strong>{view.pending_judgments ?? 0}</strong> 筆未判定，全部判定後才能揭曉本題。
            </p>
          )}
          <Leaderboard rows={view.leaderboard ?? []} />
        </>
      )}
      {view.phase === "judging" && (
        <p>
          判定中：尚有 <strong>{view.pending_judgments ?? 0}</strong> 筆未判定，全部判定後才能揭曉。
        </p>
      )}
      {view.phase === "ended" && (
        <p className="muted">
          「匯出到 Google 試算表」把每題搶答成功的答案寫進匯入時建立的副本（原試算表不動）；下載的 xlsx
          為備援，從 Google 匯入時只含值與合併、不含格式。
        </p>
      )}
    </section>
  );
}

// 模式選擇只在準備階段可按（game-mode-framework D8）
export function ModeSelector({ view, act }: { view: TeacherView; act: Act }) {
  const modes = view.modes ?? [];
  if (modes.length === 0) return null;
  return (
    <section className="card">
      <h2>模式</h2>
      <div className="row" role="radiogroup" aria-label="模式">
        {modes.map((m) => (
          <label key={m.key}>
            <input
              type="radio"
              name="mode"
              value={m.key}
              checked={view.mode?.key === m.key}
              disabled={view.phase !== "preparing"}
              onChange={() => act("mode", { mode: m.key })}
            />
            {m.label}
          </label>
        ))}
      </div>
      <p className="muted">{MODE_HINT[view.mode?.key ?? "classic"] ?? ""}</p>
    </section>
  );
}

export const MODE_HINT: Record<string, string> = {
  classic: "每題最先送出的組別搶答成功，得 1 分。",
  accuracy: "每組每題都可作答；結束後老師判定對錯，答對各得 1 分，最早答對者的答案寫回 Guided Notes。",
  timed:
    "老師逐題開放，每題有時限；答對越快分數越高（最高 1000 分），老師判定後揭曉本題並公布各組名次。",
};

export function TeamSettings({ view, act }: { view: TeacherView; act: Act }) {
  const [count, setCount] = useState(view.teams.length);
  return (
    <section className="card">
      <h2>組別</h2>
      <label>
        <input
          type="checkbox"
          checked={!!view.team_play}
          disabled={view.phase !== "preparing"}
          onChange={(e) => act("team-play", { enabled: e.target.checked })}
          aria-label="組隊（一組多台裝置）"
        />
        組隊（一組多台裝置）
      </label>
      {view.team_play && (
        <p className="muted">
          同組第二台起要輸入該組邀請碼；開始搶答時邀請碼會換新，搶答中要加入的組員請向老師索取。切換組隊會讓所有裝置重新加入。
        </p>
      )}
      <ul className="team-list">
        {view.teams.map((t) => (
          <li key={t}>
            {t}：
            {view.joined.includes(t) ? (
              view.team_play ? `已加入（${view.devices?.[t] ?? 0} 台）` : "已加入"
            ) : (
              <span className="muted">未加入</span>
            )}
            {view.team_play && view.invite_codes?.[t] && (
              <>
                {" "}邀請碼 <code>{view.invite_codes[t]}</code>
              </>
            )}
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
  exportSheet,
  google,
  sheetUrl,
}: {
  view: TeacherView;
  act: Act;
  upload: Upload;
  download?: () => void;
  exportSheet?: () => void;
  google?: { status: GoogleStatus | null; waiting: boolean; login: () => void; logout: () => void };
  sheetUrl?: string | null;
}) {
  const judge: Judge = (question, team, correct) => act("judge", { question, team, correct });
  return (
    <>
      <PhaseControls view={view} act={act} download={download} exportSheet={exportSheet} />
      <ModeSelector view={view} act={act} />
      <section className="card">
        <h2>作答狀況與結果</h2>
        <Board
          board={view.board}
          questions={view.questions}
          teams={view.teams}
          scores={view.team_scores}
          scoreLabel={view.score_label}
          winnerTag={view.mode?.judged ? "最早答對" : "搶答成功"}
          onJudge={view.phase === "judging" || view.round?.state === "closed" ? judge : undefined}
          judgeQuestion={view.mode?.sequential ? view.round?.question : undefined}
        />
      </section>
      {google && (
        <GooglePanel status={google.status} waiting={google.waiting} onLogin={google.login} onLogout={google.logout} />
      )}
      <ImportPanel
        view={view}
        googleReady={!!google?.status?.signed_in}
        sheetUrl={sheetUrl}
        onUpload={upload}
        onUrl={(url) => act("import-url", { url })}
        onSettings={(question, multiplier) => act("question-settings", { question, multiplier })}
        onTimeLimit={
          view.mode?.sequential ? (question, time_limit) => act("question-settings", { question, time_limit }) : undefined
        }
      />
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
  const [gStatus, setGStatus] = useState<GoogleStatus | null>(null);
  const [waiting, setWaiting] = useState(false);
  const [sheetUrl, setSheetUrl] = useState<string | null>(null);
  const pollUntil = useRef(0);
  const refreshGoogle = useCallback(
    () =>
      googleStatus(teacherKey)
        .then((s) => {
          setGStatus(s);
          if (s.signed_in) setWaiting(false);
        })
        .catch(() => undefined),
    [teacherKey],
  );
  useEffect(() => {
    void refreshGoogle();
  }, [refreshGoogle]);
  useEffect(() => {
    if (!waiting) return;
    // 授權在新分頁完成；這裡每 2 秒查一次，最多等 10 分鐘（state 有效期）
    const timer = window.setInterval(() => {
      if (Date.now() > pollUntil.current) setWaiting(false);
      else void refreshGoogle();
    }, 2000);
    return () => window.clearInterval(timer);
  }, [waiting, refreshGoogle]);
  const google = {
    status: gStatus,
    waiting,
    login: () => {
      setError("");
      // 先同步開分頁（避免被擋彈出視窗），拿到授權網址後再導過去
      const tab = window.open("", "_blank");
      teacherPost("google/login", teacherKey)
        .then((r) => {
          const url = (r as { url: string }).url;
          if (tab) tab.location.href = url;
          else window.location.href = url;
          pollUntil.current = Date.now() + 10 * 60 * 1000;
          setWaiting(true);
        })
        .catch((e: Error) => {
          tab?.close();
          setError(e.message);
        });
    },
    logout: () => {
      setError("");
      teacherPost("google/logout", teacherKey)
        .then(() => refreshGoogle())
        .catch((e: Error) => setError(e.message));
    },
  };
  const actWithGoogle: Act = (path, body) => {
    if (path !== "import-url") return act(path, body);
    setError("");
    teacherPost(path, teacherKey, body)
      .then((r) => setSheetUrl((r as { sheet_url?: string }).sheet_url ?? null))
      .catch((e: Error) => {
        setError(e.message);
        void refreshGoogle();
      });
  };
  const exportSheet = () => {
    setError("");
    teacherPost("export-sheet", teacherKey)
      .then((r) => setSheetUrl((r as { url: string }).url))
      .catch((e: Error) => {
        setError(e.message);
        void refreshGoogle();
      });
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
      {view?.role === "teacher" ? (
        <TeacherPanel
          view={view}
          act={actWithGoogle}
          upload={upload}
          download={download}
          exportSheet={exportSheet}
          google={google}
          sheetUrl={sheetUrl}
        />
      ) : (
        <p>連線中…</p>
      )}
    </main>
  );
}
