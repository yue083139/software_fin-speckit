import { CopyOutlined } from "@ant-design/icons";
import { Alert, Input, Steps, Tag } from "antd";
import { useState } from "react";
import type { GoogleStatus } from "../api";
import { Btn, Section } from "../ui";

const DEFAULT_REDIRECT = "http://127.0.0.1:8000/api/google/callback";
const CONSOLE = "https://console.cloud.google.com";

// 設定精靈六步（easy-setup D2）。連結以 2026-11-26 的 Google Cloud Console 為準；改版時照「找不到時」搜尋
const STEPS: { title: string; href: string; detail: string; search: string }[] = [
  { title: "建立專案", href: `${CONSOLE}/projectcreate`, detail: "名稱隨意（例：課堂搶答）。", search: "建立專案" },
  {
    title: "啟用 Google Sheets API",
    href: `${CONSOLE}/apis/library/sheets.googleapis.com`,
    detail: "確認上方選到剛建立的專案，按「啟用」。",
    search: "Google Sheets API",
  },
  {
    title: "啟用 Google Drive API",
    href: `${CONSOLE}/apis/library/drive.googleapis.com`,
    detail: "同上，按「啟用」。",
    search: "Google Drive API",
  },
  {
    title: "設定目標對象與測試使用者",
    href: `${CONSOLE}/auth/audience`,
    detail: "Google Auth Platform：目標對象選「外部」、發布狀態保持「測試中」，把要登入的 Google 帳號加到「測試使用者」。",
    search: "Google Auth Platform",
  },
  {
    title: "建立用戶端",
    href: `${CONSOLE}/auth/clients/create`,
    detail: "類型選「網頁應用程式」，在「已授權的重新導向 URI」貼上下面這行（JavaScript 來源留空），建立後複製用戶端 ID 與密鑰。",
    search: "用戶端",
  },
];

function CopyLine({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <div className="row">
      <code className="qz-url">{text}</code>
      <Btn
        size="small"
        icon={<CopyOutlined />}
        onClick={() => void navigator.clipboard?.writeText(text).then(() => setCopied(true))}
      >
        {copied ? "已複製" : "複製"}
      </Btn>
    </div>
  );
}

export function GoogleWizard({
  redirectUri,
  onSave,
  saving,
}: {
  redirectUri: string;
  onSave: (clientId: string, clientSecret: string) => void;
  saving?: boolean;
}) {
  const [clientId, setClientId] = useState("");
  const [clientSecret, setClientSecret] = useState("");
  const ready = clientId.trim() !== "" && clientSecret.trim() !== "";
  return (
    <div className="stack" data-testid="google-wizard">
      <Steps
        direction="vertical"
        size="small"
        current={-1}
        items={[
          ...STEPS.map((s, i) => ({
            title: (
              <a href={s.href} target="_blank" rel="noreferrer">
                {i + 1}. {s.title}
              </a>
            ),
            description: (
              <div className="stack" style={{ gap: 4 }}>
                <span>{s.detail}</span>
                {i === STEPS.length - 1 && <CopyLine text={redirectUri} />}
                <span className="muted">找不到時：在 Console 上方搜尋列搜尋「{s.search}」。</span>
              </div>
            ),
          })),
          {
            title: "6. 貼上用戶端 ID 與密鑰",
            description: (
              <div className="stack" style={{ gap: 6 }}>
                <Input
                  aria-label="用戶端 ID"
                  placeholder="例：123456789012-xxxx.apps.googleusercontent.com"
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                />
                <Input.Password
                  aria-label="用戶端密鑰"
                  placeholder="GOCSPX-…"
                  value={clientSecret}
                  onChange={(e) => setClientSecret(e.target.value)}
                />
                <div>
                  <Btn
                    type="primary"
                    disabled={!ready || saving}
                    loading={saving}
                    onClick={() => onSave(clientId.trim(), clientSecret.trim())}
                  >
                    儲存設定
                  </Btn>
                </div>
                <span className="muted">設定會寫進本機 repo 根目錄的 .env（不會進版本控制），儲存後不用重新啟動。</span>
              </div>
            ),
          },
        ]}
      />
    </div>
  );
}

// 老師 Google 帳號登入（guided-notes-sheets-sync D1）＋設定精靈（easy-setup D2）：授權頁在新分頁開，登入完成後本頁輪詢狀態
export function GooglePanel({
  status,
  waiting,
  onLogin,
  onLogout,
  onSaveConfig,
  onClearConfig,
  saving,
}: {
  status: GoogleStatus | null;
  waiting?: boolean;
  onLogin: () => void;
  onLogout: () => void;
  onSaveConfig?: (clientId: string, clientSecret: string) => void;
  onClearConfig?: () => void;
  saving?: boolean;
}) {
  const [editing, setEditing] = useState(false);
  const redirectUri = status?.redirect_uri ?? DEFAULT_REDIRECT;
  const save = (id: string, secret: string) => {
    onSaveConfig?.(id, secret);
    setEditing(false);
  };
  return (
    <Section
      id="google"
      title="Google 帳號"
      extra={status?.signed_in ? <Tag color="success" className="qz-pill">已連線</Tag> : undefined}
    >
      {status === null ? (
        <p className="muted">讀取登入狀態中…</p>
      ) : !status.configured ? (
        <div className="stack">
          <Alert
            type="info"
            showIcon
            message="伺服器未設定 Google OAuth 用戶端"
            description="依下列步驟建立一次（約 5 分鐘），完成後不用重新啟動。沒有 Google 設定時仍可上傳與下載 xlsx。"
          />
          {onSaveConfig && <GoogleWizard redirectUri={redirectUri} onSave={save} saving={saving} />}
        </div>
      ) : status.signed_in ? (
        <div className="row">
          <span>
            已登入：<strong>{status.email ?? "Google 帳號"}</strong>
          </span>
          <Btn onClick={onLogout}>登出 Google</Btn>
        </div>
      ) : (
        <div className="stack">
          <div className="row">
            <Btn type="primary" onClick={onLogin}>
              以 Google 帳號登入
            </Btn>
            {waiting && <span className="muted">請在新分頁完成登入，完成後此處會自動更新。</span>}
          </div>
          {status.client_id_hint && (
            <div className="row">
              <span className="muted">
                目前用戶端：<code>{status.client_id_hint}</code>
              </span>
              {onSaveConfig && (
                <Btn size="small" onClick={() => setEditing((v) => !v)}>
                  {editing ? "取消變更" : "變更設定"}
                </Btn>
              )}
              {onClearConfig && (
                <Btn size="small" danger onClick={onClearConfig}>
                  清除設定
                </Btn>
              )}
            </div>
          )}
          {editing && onSaveConfig && <GoogleWizard redirectUri={redirectUri} onSave={save} saving={saving} />}
        </div>
      )}
    </Section>
  );
}
