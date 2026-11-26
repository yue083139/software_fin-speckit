import { fireEvent, render, screen } from "@testing-library/react";
import { btn } from "../test-utils";
import type { TeacherView } from "../types";
import { GooglePanel } from "./GooglePanel";
import { SetupChecklist } from "./SetupChecklist";
import { INSTALL_CLOUDFLARED, StudentLink, TeacherPanel } from "./Teacher";

// easy-setup D2–D4：Google 設定精靈、一鍵手機連線、開始前的設定清單
const view: TeacherView = {
  role: "teacher",
  phase: "preparing",
  teams: ["第1組", "第2組"],
  joined: [],
  source: null,
  questions: [],
  board: [],
  team_scores: {},
  tunnel: "off",
  student_url: null,
};
const unconfigured = {
  configured: false,
  signed_in: false,
  email: null,
  client_id_hint: null,
  redirect_uri: "http://127.0.0.1:8000/api/google/callback",
};
const configured = { ...unconfigured, configured: true, client_id_hint: "123456…apps.googleusercontent.com" };
const ID = "123456789012-" + "a".repeat(32) + ".apps.googleusercontent.com";
const SECRET = "GOCSPX-" + "0".repeat(28);

describe("Google 設定精靈", () => {
  it("未設定時展開六步、可複製重新導向 URI，填齊才可儲存且送出前去頭尾空白", () => {
    const saved: [string, string][] = [];
    render(
      <GooglePanel status={unconfigured} onLogin={() => {}} onLogout={() => {}} onSaveConfig={(a, b) => saved.push([a, b])} />,
    );
    expect(screen.getByTestId("google-wizard")).toBeInTheDocument();
    expect(screen.getByText(/1\. 建立專案/).closest("a")).toHaveAttribute("href", "https://console.cloud.google.com/projectcreate");
    expect(screen.getByText("http://127.0.0.1:8000/api/google/callback")).toBeInTheDocument();
    expect(btn("儲存設定")).toBeDisabled();
    fireEvent.change(screen.getByLabelText("用戶端 ID"), { target: { value: `  ${ID} ` } });
    expect(btn("儲存設定")).toBeDisabled();
    fireEvent.change(screen.getByLabelText("用戶端密鑰"), { target: { value: `${SECRET}\n` } });
    fireEvent.click(btn("儲存設定"));
    expect(saved).toEqual([[ID, SECRET]]);
    expect(screen.queryByText("以 Google 帳號登入")).toBeNull();
  });

  it("已設定未登入：顯示遮罩 ID、可變更與清除，不顯示密鑰", () => {
    let cleared = 0;
    render(
      <GooglePanel
        status={configured}
        onLogin={() => {}}
        onLogout={() => {}}
        onSaveConfig={() => {}}
        onClearConfig={() => cleared++}
      />,
    );
    expect(screen.getByText("以 Google 帳號登入")).toBeInTheDocument();
    expect(screen.getByText("123456…apps.googleusercontent.com")).toBeInTheDocument();
    expect(screen.queryByTestId("google-wizard")).toBeNull();
    fireEvent.click(btn("變更設定"));
    expect(screen.getByTestId("google-wizard")).toBeInTheDocument();
    fireEvent.click(btn("清除設定"));
    expect(cleared).toBe(1);
  });

  it("已登入時沒有變更與清除按鈕", () => {
    render(
      <GooglePanel
        status={{ ...configured, signed_in: true, email: "teacher@example.com" }}
        onLogin={() => {}}
        onLogout={() => {}}
        onSaveConfig={() => {}}
        onClearConfig={() => {}}
      />,
    );
    expect(screen.queryByText("變更設定")).toBeNull();
    expect(screen.queryByText("清除設定")).toBeNull();
  });
});

describe("一鍵手機連線", () => {
  const control = (missing = false) => {
    const calls: string[] = [];
    return { calls, ctl: { open: () => calls.push("open"), close: () => calls.push("close"), missing } };
  };

  it("關閉時按開啟", () => {
    const { calls, ctl } = control();
    render(<StudentLink studentUrl={null} tunnel="off" control={ctl} />);
    fireEvent.click(btn("開啟手機連線"));
    expect(calls).toEqual(["open"]);
    expect(screen.getByText(/目前只在本機可連；要讓手機掃碼，按上方「開啟手機連線」/)).toBeInTheDocument();
  });

  it("建立中按鈕停用", () => {
    const { ctl } = control();
    render(<StudentLink studentUrl={null} tunnel="starting" control={ctl} />);
    expect(btn("手機連線建立中…")).toBeDisabled();
  });

  it("已開啟時 QR 為公開網址、可關閉；搶答開始後關閉鈕停用", () => {
    const url = "https://abc-def.trycloudflare.com/";
    const { calls, ctl } = control();
    const { rerender } = render(<StudentLink studentUrl={url} tunnel="on" control={ctl} canClose />);
    expect(screen.getByTestId("student-qr")).toHaveAttribute("data-qr-value", url);
    fireEvent.click(btn("關閉手機連線"));
    expect(calls).toEqual(["close"]);
    rerender(<StudentLink studentUrl={url} tunnel="on" control={ctl} canClose={false} />);
    expect(btn("關閉手機連線")).toBeDisabled();
    expect(screen.getByText(/搶答開始後不能關閉手機連線/)).toBeInTheDocument();
  });

  it("找不到 cloudflared 時顯示安裝指令與複製鈕", () => {
    const { ctl } = control(true);
    render(<StudentLink studentUrl={null} tunnel="off" control={ctl} />);
    expect(screen.getByText("找不到 cloudflared")).toBeInTheDocument();
    expect(screen.getByText(INSTALL_CLOUDFLARED)).toBeInTheDocument();
    expect(btn("複製指令")).toBeInTheDocument();
  });
});

describe("開始前的設定清單", () => {
  it("首次進入三項皆未完成，點列跳到對應分區", () => {
    const jumps: string[] = [];
    render(<SetupChecklist view={view} google={unconfigured} onJump={(k) => jumps.push(k)} />);
    expect(screen.getByTestId("setup-google")).toHaveTextContent("未設定");
    expect(screen.getByTestId("setup-link")).toHaveTextContent("關閉");
    expect(screen.getByTestId("setup-import")).toHaveTextContent("尚未匯入");
    fireEvent.click(screen.getByTestId("setup-google"));
    fireEvent.click(screen.getByTestId("setup-link"));
    fireEvent.click(screen.getByTestId("setup-import"));
    expect(jumps).toEqual(["google", "link", "import"]);
  });

  it("完成後顯示已登入、已開啟、已匯入題數", () => {
    const done: TeacherView = { ...view, tunnel: "on", questions: [{ number: 1, labels: [""] }, { number: 2, labels: [""] }] };
    render(
      <SetupChecklist view={done} google={{ ...configured, signed_in: true, email: "t@example.com" }} onJump={() => {}} />,
    );
    expect(screen.getByTestId("setup-google")).toHaveTextContent("已登入 t@example.com");
    expect(screen.getByTestId("setup-link")).toHaveTextContent("已開啟");
    expect(screen.getByTestId("setup-import")).toHaveTextContent("已匯入 2 題");
  });

  it("已設定未登入、建立中", () => {
    render(<SetupChecklist view={{ ...view, tunnel: "starting" }} google={configured} onJump={() => {}} />);
    expect(screen.getByTestId("setup-google")).toHaveTextContent("已設定，尚未登入");
    expect(screen.getByTestId("setup-link")).toHaveTextContent("建立中");
  });

  it("非準備階段不顯示", () => {
    const { container } = render(<SetupChecklist view={{ ...view, phase: "answering" }} google={configured} onJump={() => {}} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("老師頁在準備階段把清單放在最上方", () => {
    render(<TeacherPanel view={view} act={() => {}} upload={() => {}} onJump={() => {}} />);
    expect(screen.getByLabelText("開始前的設定")).toBeInTheDocument();
  });
});
