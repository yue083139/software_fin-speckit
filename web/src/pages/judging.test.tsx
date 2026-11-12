import { render, screen } from "@testing-library/react";
import { TeacherPanel } from "./Teacher";
import { StudentPanel } from "./Student";
import type { QuestionResult, TeacherView } from "../types";

const board: QuestionResult[] = [
  {
    number: 3,
    labels: [""],
    reference: ["位址"],
    ranking: [
      { team: "第1組", answers: ["地址"], rank: 1, is_winner: false, score: 0, correct: null, suggestion: false },
      { team: "第2組", answers: ["位址"], rank: 2, is_winner: false, score: 0, correct: true, suggestion: true },
    ],
    winner: null,
  },
];

const base: TeacherView = {
  role: "teacher",
  phase: "judging",
  teams: ["第1組", "第2組"],
  joined: [],
  source: "group.xlsx",
  questions: [],
  board,
  team_scores: { 第1組: 0, 第2組: 1 },
  mode: { key: "accuracy", label: "只計對錯", judged: true },
  modes: [
    { key: "classic", label: "經典搶答" },
    { key: "accuracy", label: "只計對錯" },
  ],
  score_label: "得分",
  pending_judgments: 1,
};

describe("判定畫面", () => {
  it("判定鈕送出判定、顯示建議與參考答案", () => {
    const calls: [string, unknown][] = [];
    render(<TeacherPanel view={base} act={(p, b) => calls.push([p, b])} upload={() => {}} />);
    expect(screen.getByText("參考答案：位址")).toBeInTheDocument();
    expect(screen.getByText("建議：錯誤")).toBeInTheDocument();
    screen.getByLabelText("第 3 題 第1組 正確").click();
    expect(calls).toContainEqual(["judge", { question: 3, team: "第1組", correct: true }]);
    screen.getByText("採用全部建議").click();
    expect(calls).toContainEqual(["accept-suggestions", undefined]);
  });

  it("尚有未判定時揭曉鈕停用，判完才可按", () => {
    const { unmount } = render(<TeacherPanel view={base} act={() => {}} upload={() => {}} />);
    expect(screen.getByText("揭曉結果")).toBeDisabled();
    expect(screen.getByText("得分")).toBeInTheDocument();
    unmount();
    const calls: string[] = [];
    render(<TeacherPanel view={{ ...base, pending_judgments: 0 }} act={(p) => calls.push(p)} upload={() => {}} />);
    screen.getByText("揭曉結果").click();
    expect(calls).toEqual(["reveal"]);
  });

  it("模式單選只在準備階段可按", () => {
    const { unmount } = render(<TeacherPanel view={base} act={() => {}} upload={() => {}} />);
    expect(screen.getByLabelText("經典搶答")).toBeDisabled();
    unmount();
    const calls: [string, unknown][] = [];
    render(
      <TeacherPanel view={{ ...base, phase: "preparing" }} act={(p, b) => calls.push([p, b])} upload={() => {}} />,
    );
    screen.getByLabelText("經典搶答").click();
    expect(calls).toEqual([["mode", { mode: "classic" }]]);
  });
});

describe("學生端模式", () => {
  it("判定中顯示提示、結果顯示對錯與最早答對", () => {
    const { unmount } = render(
      <StudentPanel
        view={{ role: "student", phase: "judging", team: "第1組", team_valid: true, mode: { key: "accuracy", label: "只計對錯" } }}
      />,
    );
    expect(screen.getByText("老師判定中，揭曉前看不到其他組的答案。")).toBeInTheDocument();
    expect(screen.getByText(/模式：只計對錯/)).toBeInTheDocument();
    unmount();
    const ended: QuestionResult[] = [
      {
        number: 3,
        labels: [""],
        ranking: [
          { team: "第1組", answers: ["地址"], rank: 1, is_winner: false, score: 0, correct: false },
          { team: "第2組", answers: ["位址"], rank: 2, is_winner: true, score: 1, correct: true },
        ],
        winner: { team: "第2組", answers: ["位址"] },
      },
    ];
    render(
      <StudentPanel
        view={{
          role: "student",
          phase: "ended",
          team: "第1組",
          team_valid: true,
          mode: { key: "accuracy", label: "只計對錯" },
          score_label: "得分",
          results: ended,
          team_scores: { 第1組: 0, 第2組: 1 },
        }}
      />,
    );
    expect(screen.getByText("最早答對：第2組（位址）")).toBeInTheDocument();
    expect(screen.getByText("本組：第 1 順位（地址） ✗ 錯誤")).toBeInTheDocument();
  });
});
