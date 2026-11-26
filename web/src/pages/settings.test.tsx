import { render, screen } from "@testing-library/react";
import { TeacherPanel } from "./Teacher";
import { StudentPanel } from "./Student";
import { StudentResults } from "./Results";
import type { TeacherView } from "../types";

const view: TeacherView = {
  role: "teacher",
  phase: "preparing",
  teams: ["第1組", "第2組"],
  joined: [],
  source: "group.xlsx",
  questions: [
    { number: 3, labels: [""], multiplier: 1 },
    { number: 4, labels: [""], multiplier: 2 },
  ],
  board: [],
  team_scores: {},
};

describe("雙倍分數題", () => {
  it("準備階段勾選送出設定", () => {
    const calls: [string, unknown][] = [];
    render(<TeacherPanel view={view} act={(p, b) => calls.push([p, b])} upload={() => {}} />);
    expect(screen.getByLabelText("第 4 題雙倍分數")).toBeChecked();
    screen.getByLabelText("第 3 題雙倍分數").click();
    expect(calls).toEqual([["question-settings", { question: 3, multiplier: 2 }]]);
  });

  it("非準備階段不能改，只顯示標記", () => {
    render(<TeacherPanel view={{ ...view, phase: "answering" }} act={() => {}} upload={() => {}} />);
    expect(screen.queryByLabelText("第 3 題雙倍分數")).toBeNull();
    expect(screen.getAllByText("雙倍分數").length).toBeGreaterThan(0);
  });

  it("學生題目與作答卡顯示雙倍標記", () => {
    render(
      <StudentPanel
        view={{ role: "student", phase: "answering", team: "第1組", team_valid: true, questions: view.questions }}
      />,
    );
    expect(screen.getAllByText("雙倍分數")).toHaveLength(1);
  });

  it("結果畫面用伺服器給的欄名", () => {
    render(
      <StudentResults
        team="第1組"
        results={[{ number: 4, labels: [""], multiplier: 2, ranking: [], winner: null }]}
        scores={{ 第1組: 2 }}
        scoreLabel="得分"
      />,
    );
    expect(screen.getByText(/本組得分/)).toBeInTheDocument();
    expect(screen.getByText("雙倍分數")).toBeInTheDocument();
  });
});
