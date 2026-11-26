import { btn } from "../test-utils";
import { render, screen } from "@testing-library/react";
import { StudentPanel } from "./Student";
import { TeacherPanel } from "./Teacher";
import type { TeacherView } from "../types";

const view: TeacherView = {
  role: "teacher",
  phase: "preparing",
  teams: ["第1組", "第2組"],
  joined: ["第1組"],
  source: "group.xlsx",
  questions: [
    { number: 1, labels: ["（1）", "（2）"] },
    { number: 3, labels: [""] },
  ],
  board: [],
  team_scores: { 第1組: 0, 第2組: 0 },
};

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

  it("準備中只可按開始", () => {
    render(<TeacherPanel view={view} act={() => {}} upload={() => {}} />);
    expect(btn("開始搶答")).toBeEnabled();
    expect(btn("結束搶答")).toBeDisabled();
  });

  it("已加入的組別可釋放", () => {
    const calls: unknown[] = [];
    render(<TeacherPanel view={view} act={(p, b) => calls.push([p, b])} upload={() => {}} />);
    screen.getByText("釋放").click();
    expect(calls).toEqual([["release", { team: "第1組" }]]);
  });
});

describe("匯入", () => {
  it("老師頁顯示題目來源與題組", () => {
    render(<TeacherPanel view={view} act={() => {}} upload={() => {}} />);
    expect(screen.getByText("group.xlsx")).toBeInTheDocument();
    expect(screen.getByText(/題組，2 個子題/)).toBeInTheDocument();
  });

  it("搶答中不能匯入", () => {
    render(<TeacherPanel view={{ ...view, phase: "answering" }} act={() => {}} upload={() => {}} />);
    expect(btn("從 Google 試算表匯入")).toBeDisabled();
  });

  it("學生準備中看到題號清單", () => {
    render(
      <StudentPanel
        view={{ role: "student", phase: "preparing", team: "第1組", team_valid: true, questions: view.questions }}
      />,
    );
    expect(screen.getByText(/第 3 題/)).toBeInTheDocument();
  });
});
