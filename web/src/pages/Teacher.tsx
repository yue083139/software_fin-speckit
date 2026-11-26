import {
  AppstoreOutlined,
  FileTextOutlined,
  GoogleOutlined,
  PlayCircleOutlined,
  QrcodeOutlined,
  TableOutlined,
  TeamOutlined,
} from "@ant-design/icons";
import { Alert, Checkbox, Input, Menu, QRCode, Radio, Tag } from "antd";
import { useCallback, useEffect, useRef, useState } from "react";
import { type GoogleStatus, googleStatus, teacherDownload, teacherPost, teacherUpload } from "../api";
import { GooglePanel } from "./GooglePanel";
import { ImportPanel } from "./ImportPanel";
import { Board, type Judge } from "./Results";
import { Leaderboard, RoundStatus } from "./Round";
import { useLiveView } from "../live";
import { PHASE_LABEL, type TeacherView } from "../types";
import { Btn, GlassHeader, PhaseTag, Section } from "../ui";
import { Shell } from "../Shell";

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
    <Section id="control" title="活動控制" extra={<PhaseTag phase={view.phase} />}>
      <div className="stack">
        <p className="phase" style={{ margin: 0 }}>
          目前階段：<strong>{PHASE_LABEL[view.phase]}</strong>
        </p>
        <div className="row">
          <Btn type="primary" disabled={view.phase !== "preparing"} onClick={() => act("start")}>
            開始搶答
          </Btn>
          {view.mode?.sequential && (
            <>
              <Btn type="primary" ghost disabled={view.phase !== "answering" || !!view.round} onClick={() => act("open-next")}>
                開放下一題
              </Btn>
              <Btn disabled={view.round?.state !== "open"} onClick={() => act("close-question")}>
                提早結束本題
              </Btn>
              <Btn disabled={view.round?.state !== "closed"} onClick={() => act("accept-suggestions")}>
                採用全部建議
              </Btn>
              <Btn
                disabled={view.round?.state !== "closed" || (view.pending_judgments ?? 0) > 0}
                onClick={() => act("reveal-question")}
              >
                揭曉本題
              </Btn>
            </>
          )}
          <Btn danger disabled={view.phase !== "answering" || !!view.round} onClick={() => act("end")}>
            {view.mode?.sequential ? "結束活動" : "結束搶答"}
          </Btn>
          {view.mode?.judged && (
            <>
              <Btn disabled={view.phase !== "judging"} onClick={() => act("accept-suggestions")}>
                採用全部建議
              </Btn>
              <Btn
                type="primary"
                disabled={view.phase !== "judging" || (view.pending_judgments ?? 0) > 0}
                onClick={() => act("reveal")}
              >
                揭曉結果
              </Btn>
            </>
          )}
          <Btn disabled={view.phase !== "ended"} onClick={() => act("reset")}>
            重置活動
          </Btn>
        </div>
        <div className="row">
          {exportSheet && (
            <Btn type="primary" disabled={view.phase !== "ended" || !view.source} onClick={exportSheet}>
              匯出到 Google 試算表
            </Btn>
          )}
          <Btn disabled={view.phase !== "ended" || !view.source} onClick={download}>
            下載 xlsx（備援）
          </Btn>
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
          <p className="muted" style={{ margin: 0 }}>
            「匯出到 Google 試算表」把每題搶答成功的答案寫進匯入時建立的副本（原試算表不動）；下載的 xlsx
            為備援，從 Google 匯入時只含值與合併、不含格式。
          </p>
        )}
      </div>
    </Section>
  );
}

// 模式選擇只在準備階段可按（game-mode-framework D8）
export function ModeSelector({ view, act }: { view: TeacherView; act: Act }) {
  const modes = view.modes ?? [];
  if (modes.length === 0) return null;
  return (
    <Section id="mode" title="模式">
      <Radio.Group
        aria-label="模式"
        value={view.mode?.key}
        disabled={view.phase !== "preparing"}
        onChange={(e) => act("mode", { mode: e.target.value })}
      >
        {modes.map((m) => (
          <Radio key={m.key} value={m.key}>
            {m.label}
          </Radio>
        ))}
      </Radio.Group>
      <p className="muted">{MODE_HINT[view.mode?.key ?? "classic"] ?? ""}</p>
    </Section>
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
    <Section id="teams" title="組別與裝置">
      <Checkbox
        checked={!!view.team_play}
        disabled={view.phase !== "preparing"}
        onChange={(e) => act("team-play", { enabled: e.target.checked })}
        aria-label="組隊（一組多台裝置）"
      >
        組隊（一組多台裝置）
      </Checkbox>
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
              <Btn size="small" onClick={() => act("release", { team: t })}>
                釋放
              </Btn>
            )}
          </li>
        ))}
      </ul>
      <div className="row" style={{ alignItems: "flex-end" }}>
        <label className="field">
          <span className="field-label">組數（2–12）</span>
          <Input
            type="number"
            min={2}
            max={12}
            value={count}
            onChange={(e) => setCount(Number(e.target.value))}
            aria-label="組數"
            style={{ width: 120 }}
          />
        </label>
        <Btn disabled={view.phase !== "preparing"} onClick={() => act("teams", { count })}>
          設定組數
        </Btn>
      </div>
    </Section>
  );
}

// 學生連結：伺服器給公開網址（student-qr）就用它，否則用本頁網址
export function StudentLink({ url }: { url: string }) {
  return (
    <Section id="link" title="學生連結">
      <div className="qz-qr">
        <QRCode value={url} size={168} bordered={false} />
        <div className="stack" style={{ minWidth: 0, flex: 1 }}>
          <span className="muted">學生用手機掃描 QR code，或在瀏覽器輸入：</span>
          <a className="qz-url" href={url} target="_blank" rel="noreferrer">
            {url}
          </a>
        </div>
      </div>
    </Section>
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
      <Section id="board" title="作答狀況與結果">
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
      </Section>
      <StudentLink url={view.student_url ?? `${window.location.origin}/`} />
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

const NAV = [
  { key: "control", label: "活動控制", icon: <PlayCircleOutlined /> },
  { key: "mode", label: "模式", icon: <AppstoreOutlined /> },
  { key: "board", label: "作答狀況與結果", icon: <TableOutlined /> },
  { key: "link", label: "學生連結", icon: <QrcodeOutlined /> },
  { key: "google", label: "Google 帳號", icon: <GoogleOutlined /> },
  { key: "import", label: "題目與匯入", icon: <FileTextOutlined /> },
  { key: "teams", label: "組別與裝置", icon: <TeamOutlined /> },
];

export default function Teacher({ teacherKey }: { teacherKey: string }) {
  const { view, closedCode } = useLiveView(`role=teacher&key=${encodeURIComponent(teacherKey)}`);
  const [error, setError] = useState("");
  const [active, setActive] = useState("control");
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
      <Shell>
        <GlassHeader title="課堂搶答・老師工作檯" />
        <div className="qz-narrow">
          <Alert type="error" showIcon message="老師金鑰錯誤，請回首頁重新輸入。" />
        </div>
      </Shell>
    );
  const teacherView = view?.role === "teacher" ? view : null;
  return (
    <Shell>
      <GlassHeader title="課堂搶答・老師工作檯">
        {teacherView && (
          <>
            <PhaseTag phase={teacherView.phase} />
            {teacherView.mode && <Tag className="qz-pill">{teacherView.mode.label}</Tag>}
            {teacherView.source && <Tag className="qz-pill">{teacherView.source}</Tag>}
          </>
        )}
      </GlassHeader>
      <div className="qz-workbench">
        <nav className="qz-glass qz-sider" aria-label="老師工作檯導覽">
          <Menu
            mode="inline"
            selectedKeys={[active]}
            items={NAV}
            onClick={({ key }) => {
              setActive(key);
              document.getElementById(key)?.scrollIntoView({ behavior: "smooth", block: "start" });
            }}
          />
        </nav>
        <main className="qz-content">
          {error && <Alert type="error" showIcon closable message={error} onClose={() => setError("")} />}
          {teacherView ? (
            <TeacherPanel
              view={teacherView}
              act={actWithGoogle}
              upload={upload}
              download={download}
              exportSheet={exportSheet}
              google={google}
              sheetUrl={sheetUrl}
            />
          ) : (
            <Section>
              <p>連線中…</p>
            </Section>
          )}
        </main>
      </div>
    </Shell>
  );
}
