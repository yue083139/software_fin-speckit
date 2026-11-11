import { render, screen } from "@testing-library/react";
import { Board, StudentResults } from "./Results";
import type { QuestionResult } from "../types";

const results: QuestionResult[] = [
  {
    number: 1,
    labels: ["（1）", "（2）"],
    ranking: [{ team: "第1組", answers: ["CPU", "作業系統"], rank: 1, is_winner: true, score: 1 }],
    winner: { team: "第1組", answers: ["CPU", "作業系統"] },
  },
  {
    number: 3,
    labels: [""],
    ranking: [
      { team: "第2組", answers: ["位址"], rank: 1, is_winner: true, score: 1 },
      { team: "第1組", answers: ["地址"], rank: 2, is_winner: false, score: 0 },
    ],
    winner: { team: "第2組", answers: ["位址"] },
  },
  { number: 4, labels: [""], ranking: [], winner: null },
];
const scores = { 第1組: 1, 第2組: 1 };

describe("老師作答狀況表", () => {
  it("顯示答案、順位與得主", () => {
    render(<Board board={results} teams={["第1組", "第2組"]} scores={scores} />);
    expect(screen.getByText("（1）CPU ／ （2）作業系統")).toBeInTheDocument();
    expect(screen.getByText("第 2 順位")).toBeInTheDocument();
    expect(screen.getAllByText("搶答成功")).toHaveLength(2);
  });
});

describe("學生結果畫面", () => {
  it("顯示得主、本組順位與未搶答題", () => {
    render(<StudentResults team="第1組" results={results} scores={scores} />);
    expect(screen.getByText("搶答成功：第2組（位址）")).toBeInTheDocument();
    expect(screen.getByText("本組：第 2 順位（地址）")).toBeInTheDocument();
    expect(screen.getByText("沒有組別搶答")).toBeInTheDocument();
  });
});
