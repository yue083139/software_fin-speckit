import { render, screen } from "@testing-library/react";
import { BadKeyNotice, NotLocalNotice, StudentLink } from "./Teacher";

describe("學生連結（student-qr D3）", () => {
  it("有 student_url 時 QR 值與顯示網址都等於它，不顯示本機提示", () => {
    const url = "https://penny-cheap-centered-fewer.trycloudflare.com/";
    render(<StudentLink studentUrl={url} />);
    expect(screen.getByTestId("student-qr")).toHaveAttribute("data-qr-value", url);
    expect(screen.getByText(url)).toBeInTheDocument();
    expect(screen.queryByText(/目前只在本機可連/)).toBeNull();
    expect(screen.getByText("複製連結")).toBeInTheDocument();
  });

  it("student_url 為 null 時退回本頁網址並提示用通道啟動", () => {
    render(<StudentLink studentUrl={null} />);
    const origin = `${window.location.origin}/`;
    expect(screen.getByTestId("student-qr")).toHaveAttribute("data-qr-value", origin);
    expect(screen.getByText(/目前只在本機可連；要讓手機掃碼請用 start-tunnel.cmd 或 make dev-tunnel 啟動/)).toBeInTheDocument();
  });
});

describe("老師頁不在本機（student-qr D2）", () => {
  it("顯示本機提示與正確網址", () => {
    render(<NotLocalNotice />);
    expect(screen.getByText("老師頁只能在本機開啟")).toBeInTheDocument();
    expect(screen.getByText(/http:\/\/127\.0\.0\.1:8000/)).toBeInTheDocument();
  });
});

describe("老師金鑰錯誤提示（teacher-key-error）", () => {
  it("4401 顯示金鑰錯誤與重開方式", () => {
    render(<BadKeyNotice />);
    expect(screen.getByText("老師金鑰錯誤")).toBeInTheDocument();
    expect(screen.getByText(/終端機印出的完整老師頁網址/)).toBeInTheDocument();
  });
});
