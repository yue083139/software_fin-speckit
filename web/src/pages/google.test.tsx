import { btn } from "../test-utils";
import { fireEvent, render, screen } from "@testing-library/react";
import { GooglePanel } from "./GooglePanel";
import { TeacherPanel } from "./Teacher";
import type { TeacherView } from "../types";

// guided-notes-sheets-sync：Google 登入、從試算表匯入（需登入）、匯出到 Google 試算表、xlsx 備援
const view: TeacherView = {
  role: "teacher",
  phase: "preparing",
  teams: ["第1組", "第2組"],
  joined: [],
  source: null,
  questions: [],
  board: [],
  team_scores: {},
};

const signedOut = { configured: true, signed_in: false, email: null };
const signedIn = { configured: true, signed_in: true, email: "teacher@example.com" };

describe("Google 帳號區塊", () => {
  it("未設定用戶端時提示且沒有登入按鈕", () => {
    render(<GooglePanel status={{ configured: false, signed_in: false, email: null }} onLogin={() => {}} onLogout={() => {}} />);
    expect(screen.getByText(/伺服器未設定 Google OAuth 用戶端/)).toBeInTheDocument();
    expect(screen.queryByText("以 Google 帳號登入")).toBeNull();
  });

  it("未登入可按登入；登入後顯示帳號與登出", () => {
    let logins = 0;
    const { rerender } = render(<GooglePanel status={signedOut} onLogin={() => logins++} onLogout={() => {}} />);
    fireEvent.click(screen.getByText("以 Google 帳號登入"));
    expect(logins).toBe(1);
    rerender(<GooglePanel status={signedIn} onLogin={() => {}} onLogout={() => {}} />);
    expect(screen.getByText("teacher@example.com")).toBeInTheDocument();
    expect(screen.getByText("登出 Google")).toBeInTheDocument();
  });
});

describe("老師頁匯入與匯出", () => {
  const google = (status: { configured: boolean; signed_in: boolean; email: string | null }) => ({ status, waiting: false, login: () => {}, logout: () => {} });

  it("未登入時不能從 Google 試算表匯入，上傳 xlsx 仍可用", () => {
    render(<TeacherPanel view={view} act={() => {}} upload={() => {}} google={google(signedOut)} />);
    fireEvent.change(screen.getByLabelText("Google 試算表連結"), {
      target: { value: "https://docs.google.com/spreadsheets/d/x/edit" },
    });
    expect(btn("從 Google 試算表匯入")).toBeDisabled();
    expect(screen.getByText("先以 Google 帳號登入才能從試算表匯入。")).toBeInTheDocument();
    expect(screen.getByText("上傳 xlsx")).toBeInTheDocument();
  });

  it("已登入時送出連結匯入", () => {
    const calls: [string, unknown][] = [];
    render(<TeacherPanel view={view} act={(p, b) => calls.push([p, b])} upload={() => {}} google={google(signedIn)} />);
    const url = "https://docs.google.com/spreadsheets/d/abc/edit";
    fireEvent.change(screen.getByLabelText("Google 試算表連結"), { target: { value: url } });
    fireEvent.click(screen.getByText("從 Google 試算表匯入"));
    expect(calls).toEqual([["import-url", { url }]]);
  });

  it("結束後可匯出到 Google 試算表並顯示副本連結", () => {
    let exported = 0;
    render(
      <TeacherPanel
        view={{ ...view, phase: "ended", source: "題組＋單題範本" }}
        act={() => {}}
        upload={() => {}}
        exportSheet={() => exported++}
        google={google(signedIn)}
        sheetUrl="https://docs.google.com/spreadsheets/d/copy/edit"
      />,
    );
    fireEvent.click(screen.getByText("匯出到 Google 試算表"));
    expect(exported).toBe(1);
    expect(screen.getByText("開啟 Google 試算表副本")).toHaveAttribute(
      "href",
      "https://docs.google.com/spreadsheets/d/copy/edit",
    );
    expect(btn("下載 xlsx（備援）")).toBeEnabled();
  });
});
