import { Tag } from "antd";
import type { GoogleStatus } from "../api";
import { Btn, Section } from "../ui";

// 老師 Google 帳號登入（guided-notes-sheets-sync D1）：授權頁在新分頁開，登入完成後本頁輪詢狀態
export function GooglePanel({
  status,
  waiting,
  onLogin,
  onLogout,
}: {
  status: GoogleStatus | null;
  waiting?: boolean;
  onLogin: () => void;
  onLogout: () => void;
}) {
  return (
    <Section
      id="google"
      title="Google 帳號"
      extra={status?.signed_in ? <Tag color="success" className="qz-pill">已連線</Tag> : undefined}
    >
      {status === null ? (
        <p className="muted">讀取登入狀態中…</p>
      ) : !status.configured ? (
        <p className="muted">
          伺服器未設定 Google OAuth 用戶端（在 repo 根目錄 <code>.env</code> 設定 GOOGLE_CLIENT_ID、GOOGLE_CLIENT_SECRET
          後重新啟動）。仍可上傳與下載 xlsx。
        </p>
      ) : status.signed_in ? (
        <div className="row">
          <span>
            已登入：<strong>{status.email ?? "Google 帳號"}</strong>
          </span>
          <Btn onClick={onLogout}>登出 Google</Btn>
        </div>
      ) : (
        <div className="row">
          <Btn type="primary" onClick={onLogin}>
            以 Google 帳號登入
          </Btn>
          {waiting && <span className="muted">請在新分頁完成登入，完成後此處會自動更新。</span>}
        </div>
      )}
    </Section>
  );
}
