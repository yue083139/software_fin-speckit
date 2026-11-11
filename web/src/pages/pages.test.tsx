import { render, screen } from "@testing-library/react";
import { StudentPanel } from "./Student";
import { TeacherPanel } from "./Teacher";

describe("學生頁", () => {
  it("顯示組別與目前階段", () => {
    render(<StudentPanel view={{ role: "student", phase: "preparing", team: "第2組", team_valid: true }} />);
    expect(screen.getByText("第2組")).toBeInTheDocument();
    expect(screen.getByText("準備中")).toBeInTheDocument();
  });

  it("無效憑證提示回首頁", () => {
    render(<StudentPanel view={{ role: "student", phase: "preparing", team: null, team_valid: false }} />);
    expect(screen.getByText(/尚未加入組別/)).toBeInTheDocument();
  });
});

describe("老師頁", () => {
  const view = { role: "teacher" as const, phase: "preparing" as const, teams: ["第1組", "第2組"], joined: ["第1組"] };

  it("準備中只可按開始", () => {
    render(<TeacherPanel view={view} act={() => {}} />);
    expect(screen.getByText("開始搶答")).toBeEnabled();
    expect(screen.getByText("結束搶答")).toBeDisabled();
  });

  it("已加入的組別可釋放", () => {
    const calls: unknown[] = [];
    render(<TeacherPanel view={view} act={(p, b) => calls.push([p, b])} />);
    screen.getByText("釋放").click();
    expect(calls).toEqual([["release", { team: "第1組" }]]);
  });
});
