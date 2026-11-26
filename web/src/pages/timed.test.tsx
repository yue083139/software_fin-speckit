import { btn } from "../test-utils";
import { render, screen } from "@testing-library/react";
import { TeacherPanel } from "./Teacher";
import { StudentPanel } from "./Student";
import type { StudentView, TeacherView } from "../types";

const timedMode = { key: "timed", label: "時間計分", judged: false, sequential: true };

const teacher: TeacherView = {
  role: "teacher",
  phase: "answering",
  teams: ["第1組", "第2組"],
  joined: [],
  source: "group.xlsx",
  questions: [
    { number: 3, labels: [""], multiplier: 1, time_limit: 20 },
    { number: 4, labels: [""], multiplier: 1, time_limit: 20 },
  ],
  board: [
    {
      number: 3,
      labels: [""],
      ranking: [{ team: "第1組", answers: ["位址"], rank: 1, is_winner: false, score: 0, correct: null }],
      winner: null,
    },
    {
      number: 4,
      labels: [""],
      ranking: [{ team: "第1組", answers: ["堆疊"], rank: 1, is_winner: false, score: 0, correct: null }],
      winner: null,
    },
  ],
  team_scores: {},
  mode: timedMode,
  round: null,
  pending_judgments: 0,
  leaderboard: [
    { team: "第1組", rank: 1, score: 967 },
    { team: "第2組", rank: 2, score: 0 },
  ],
};

describe("時間計分：老師", () => {
  it("沒有進行中題目時只能開放下一題或結束活動", () => {
    const calls: string[] = [];
    render(<TeacherPanel view={teacher} act={(p) => calls.push(p)} upload={() => {}} />);
    expect(btn("提早結束本題")).toBeDisabled();
    expect(btn("揭曉本題")).toBeDisabled();
    screen.getByText("開放下一題").click();
    expect(calls).toEqual(["open-next"]);
    expect(screen.getByText("967")).toBeInTheDocument();
  });

  it("本題已關閉：只能判定這一題，判完才可揭曉", () => {
    const closed = { ...teacher, round: { question: 3, state: "closed" as const, deadline_epoch_ms: 0 }, pending_judgments: 1 };
    const { unmount } = render(<TeacherPanel view={closed} act={() => {}} upload={() => {}} />);
    expect(screen.getByLabelText("第 3 題 第1組 正確")).toBeInTheDocument();
    expect(screen.queryByLabelText("第 4 題 第1組 正確")).toBeNull();
    expect(btn("揭曉本題")).toBeDisabled();
    expect(btn("結束活動")).toBeDisabled();
    unmount();
    const calls: string[] = [];
    render(<TeacherPanel view={{ ...closed, pending_judgments: 0 }} act={(p) => calls.push(p)} upload={() => {}} />);
    screen.getByText("揭曉本題").click();
    expect(calls).toEqual(["reveal-question"]);
  });

  it("準備階段可設時限", () => {
    const calls: [string, unknown][] = [];
    render(
      <TeacherPanel view={{ ...teacher, phase: "preparing" }} act={(p, b) => calls.push([p, b])} upload={() => {}} />,
    );
    const input = screen.getByLabelText("第 3 題時限") as HTMLInputElement;
    input.value = "30";
    input.focus();
    input.blur();
    expect(calls).toContainEqual(["question-settings", { question: 3, time_limit: 30 }]);
  });
});

describe("時間計分：學生", () => {
  const base: StudentView = {
    role: "student",
    phase: "answering",
    team: "第2組",
    team_valid: true,
    mode: { key: "timed", label: "時間計分", sequential: true },
    questions: [
      { number: 3, labels: [""] },
      { number: 4, labels: [""] },
    ],
    my_submissions: [],
    round: { question: 3, state: "open", deadline_epoch_ms: Date.now() + 15_000 },
    revealed: [],
    my_total: 0,
    leaderboard: [],
  };

  it("只顯示進行中那一題與倒數", () => {
    // 截止時刻以渲染當下起算：antd 首次渲染可能耗掉數秒，模組載入時算的截止會讓倒數提早變少
    render(<StudentPanel view={{ ...base, round: { question: 3, state: "open", deadline_epoch_ms: Date.now() + 15_000 } }} />);
    expect(screen.getByText("第 3 題")).toBeInTheDocument();
    expect(screen.queryByText("第 4 題")).toBeNull();
    expect(screen.getByLabelText("剩餘秒數").textContent).toMatch(/1[45] 秒/);
  });

  it("揭曉後顯示本組結果與名次（沒有他組分數）", () => {
    render(
      <StudentPanel
        view={{
          ...base,
          round: null,
          revealed: [{ question: 3, submitted: true, correct: false, score: 0 }],
          leaderboard: [
            { team: "第1組", rank: 1 },
            { team: "第2組", rank: 2 },
          ],
        }}
      />,
    );
    expect(screen.getByText("第 3 題揭曉")).toBeInTheDocument();
    expect(screen.getByText(/本組答錯，\+0 分/)).toBeInTheDocument();
    expect(screen.queryByText("累積分數")).toBeNull();
    expect(screen.getByText("等待老師開放下一題…")).toBeInTheDocument();
  });
});
