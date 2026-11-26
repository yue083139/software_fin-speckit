import { CheckCircleFilled, CloseCircleFilled, ExclamationCircleFilled, LoadingOutlined } from "@ant-design/icons";
import type { ReactNode } from "react";
import type { GoogleStatus } from "../api";
import type { TeacherView } from "../types";
import { Section } from "../ui";

type Mark = "ok" | "todo" | "warn" | "busy" | "optional";

const ICON: Record<Mark, ReactNode> = {
  ok: <CheckCircleFilled style={{ color: "var(--qz-ok-text)" }} />,
  todo: <CloseCircleFilled style={{ color: "var(--qz-danger)" }} />,
  warn: <ExclamationCircleFilled style={{ color: "var(--qz-accent)" }} />,
  busy: <LoadingOutlined />,
  optional: <ExclamationCircleFilled style={{ color: "var(--qz-text2)" }} />,
};

function googleRow(status: GoogleStatus | null): [Mark, string] {
  if (status === null) return ["busy", "讀取中…"];
  if (!status.configured) return ["todo", "未設定"];
  if (!status.signed_in) return ["warn", "已設定，尚未登入"];
  return ["ok", `已登入 ${status.email ?? ""}`.trim()];
}

function tunnelRow(state: TeacherView["tunnel"]): [Mark, string] {
  if (state === "on") return ["ok", "已開啟"];
  if (state === "starting") return ["busy", "建立中…"];
  return ["optional", "關閉（選用：要讓手機掃碼時再開）"];
}

// 開始前的設定（easy-setup D4）：只讀既有 view 與 Google 狀態，點了捲到對應分區；只在準備階段顯示
export function SetupChecklist({
  view,
  google,
  onJump,
}: {
  view: TeacherView;
  google: GoogleStatus | null;
  onJump: (section: string) => void;
}) {
  if (view.phase !== "preparing") return null;
  const count = view.questions.length;
  const rows: { key: string; label: string; mark: Mark; text: string }[] = [
    { key: "google", label: "Google 帳號", ...pair(googleRow(google)) },
    { key: "link", label: "手機連線", ...pair(tunnelRow(view.tunnel)) },
    { key: "import", label: "題目", ...pair(count > 0 ? ["ok", `已匯入 ${count} 題`] : ["todo", "尚未匯入"]) },
  ];
  return (
    <Section id="setup" title="開始前的設定">
      <ul className="qz-checklist" aria-label="開始前的設定">
        {rows.map((r) => (
          <li key={r.key}>
            <button type="button" className="qz-check-row" data-testid={`setup-${r.key}`} onClick={() => onJump(r.key)}>
              {ICON[r.mark]}
              <span className="qz-check-label">{r.label}</span>
              <span className="muted">{r.text}</span>
            </button>
          </li>
        ))}
      </ul>
    </Section>
  );
}

function pair([mark, text]: [Mark, string]): { mark: Mark; text: string } {
  return { mark, text };
}
