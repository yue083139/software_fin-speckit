import { btn } from "../test-utils";
import { fireEvent, render, screen } from "@testing-library/react";
import { Board, StudentResults } from "./Results";
import { PhaseControls, TeacherPanel } from "./Teacher";
import type { QuestionResult, TeacherView } from "../types";

// 經典搶答結束後依順位檢查（answer-review）：狀態全來自伺服器 board[].review
const q3 = (review: QuestionResult["review"], correct: (boolean | null)[], winner: string | null): QuestionResult => ({
  number: 3,
  labels: [""],
  ranking: [
    { team: "第2組", answers: ["一"], rank: 1, is_winner: winner === "第2組", score: 0, correct: correct[0] },
    { team: "第1組", answers: ["零"], rank: 2, is_winner: winner === "第1組", score: 0, correct: correct[1] },
  ],
  winner: winner ? { team: winner, answers: [winner === "第2組" ? "一" : "零"] } : null,
  review,
});
const teams = ["第1組", "第2組"];

describe("老師結果表：答對／答錯／重設本題", () => {
  it("只有候選格有答對、答錯，按下帶候選組名", () => {
    const calls: [number, string, boolean][] = [];
    render(
      <Board
        board={[q3({ candidate: "第2組", rejected: [], locked: false }, [null, null], "第2組")]}
        teams={teams}
        scores={{}}
        onReview={(q, t, c) => calls.push([q, t, c])}
        onReviewReset={() => {}}
      />,
    );
    expect(screen.getByText("檢查中")).toBeInTheDocument();
    expect(screen.queryByLabelText("第 3 題 第1組 答錯")).toBeNull();
    expect(screen.queryByLabelText("第 3 題 重設本題")).toBeNull(); // 未檢查不顯示重設
    fireEvent.click(screen.getByLabelText("第 3 題 第2組 答錯"));
    fireEvent.click(screen.getByLabelText("第 3 題 第2組 答對"));
    expect(calls).toEqual([
      [3, "第2組", false],
      [3, "第2組", true],
    ]);
  });

  it("判錯組標 ✗、鎖定組標 ✓ 與已鎖定，可重設", () => {
    const resets: number[] = [];
    render(
      <Board
        board={[q3({ candidate: "第1組", rejected: ["第2組"], locked: true }, [false, true], "第1組")]}
        teams={teams}
        scores={{}}
        onReview={() => {}}
        onReviewReset={(q) => resets.push(q)}
      />,
    );
    expect(screen.getByText("✗ 答錯")).toBeInTheDocument();
    expect(screen.getByText("已鎖定")).toBeInTheDocument();
    expect(screen.queryByText("答對")).toBeNull();
    fireEvent.click(screen.getByLabelText("第 3 題 重設本題"));
    expect(resets).toEqual([3]);
  });

  it("全部答錯顯示無得主", () => {
    render(
      <Board
        board={[q3({ candidate: null, rejected: ["第2組", "第1組"], locked: false }, [false, false], null)]}
        teams={teams}
        scores={{}}
        onReview={() => {}}
        onReviewReset={() => {}}
      />,
    );
    expect(screen.getByText("全部答錯，無得主")).toBeInTheDocument();
    expect(screen.getAllByText("✗ 答錯")).toHaveLength(2);
  });

  const base: TeacherView = {
    role: "teacher",
    phase: "ended",
    teams,
    joined: [],
    source: "group.xlsx",
    questions: [],
    board: [q3({ candidate: "第2組", rejected: [], locked: false }, [null, null], "第2組")],
    team_scores: {},
    mode: { key: "classic", label: "經典搶答" },
  };

  it("經典搶答 ended 才出現按鈕，並呼叫 review／review-reset", () => {
    const acts: [string, unknown][] = [];
    const { unmount } = render(<TeacherPanel view={{ ...base, phase: "answering" }} act={() => {}} upload={() => {}} />);
    expect(screen.queryByLabelText("第 3 題 第2組 答錯")).toBeNull();
    unmount();
    render(<TeacherPanel view={base} act={(p, b) => acts.push([p, b])} upload={() => {}} />);
    fireEvent.click(screen.getByLabelText("第 3 題 第2組 答錯"));
    expect(acts).toEqual([["review", { question: 3, team: "第2組", correct: false }]]);
  });

  it("非經典模式不出現按鈕", () => {
    render(
      <TeacherPanel view={{ ...base, mode: { key: "accuracy", label: "只計對錯", judged: true } }} act={() => {}} upload={() => {}} />,
    );
    expect(screen.queryByLabelText("第 3 題 第2組 答錯")).toBeNull();
  });

  it("匯出進行中兩顆匯出鈕停用", () => {
    render(<PhaseControls view={base} act={() => {}} download={() => {}} exportSheet={() => {}} exporting />);
    expect(btn("下載 xlsx（備援）")).toBeDisabled();
    expect(btn("匯出到 Google 試算表")).toBeDisabled();
  });
});

describe("學生結果：檢查後 ✓／✗", () => {
  it("顯示遞補後得主與判錯組", () => {
    render(
      <StudentResults
        team="第2組"
        results={[q3(undefined, [false, null], "第1組")]}
        scores={{ 第1組: 1, 第2組: 0 }}
      />,
    );
    expect(screen.getByText("搶答成功：第1組（零）")).toBeInTheDocument();
    expect(screen.getByText("本組：第 1 順位（一） ✗ 錯誤")).toBeInTheDocument();
  });
});
