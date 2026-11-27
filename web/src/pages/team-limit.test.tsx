import { fireEvent, render, screen } from "@testing-library/react";
import type { TeacherView } from "../types";
import { TeamPicker } from "./Home";
import { Board } from "./Results";
import { TeacherPanel } from "./Teacher";

const teams = Array.from({ length: 50 }, (_, index) => `第${index + 1}組`);

describe("50 組介面", () => {
  it("學生可在完整選組清單操作第 50 組", () => {
    const picked: string[] = [];
    render(<TeamPicker teams={teams} joined={[]} teamPlay={false} onPick={(team) => picked.push(team)} />);

    expect(screen.getAllByRole("button")).toHaveLength(50);
    fireEvent.click(screen.getByRole("button", { name: "第50組" }));
    expect(picked).toEqual(["第50組"]);
  });

  it("老師可設定 50 組並釋放第 50 組", () => {
    const calls: unknown[] = [];
    const view: TeacherView = {
      role: "teacher",
      phase: "preparing",
      teams,
      joined: ["第50組"],
      source: null,
      questions: [],
      board: [],
      team_scores: Object.fromEntries(teams.map((team) => [team, 0])),
    };
    render(<TeacherPanel view={view} act={(path, body) => calls.push([path, body])} upload={() => {}} />);

    const count = screen.getByLabelText("組數");
    expect(count).toHaveAttribute("max", "50");
    fireEvent.change(count, { target: { value: "50" } });
    fireEvent.click(screen.getByRole("button", { name: "設定組數" }));
    fireEvent.click(screen.getByRole("button", { name: "釋放" }));
    expect(calls).toEqual([
      ["teams", { count: 50 }],
      ["release", { team: "第50組" }],
    ]);
  });

  it("結果表完整保留第 50 組欄位與答案", () => {
    render(
      <Board
        teams={teams}
        scores={{ 第50組: 1 }}
        board={[
          {
            number: 1,
            labels: [""],
            ranking: [{ team: "第50組", answers: ["第五十組答案"], rank: 1, is_winner: true, score: 1 }],
            winner: { team: "第50組", answers: ["第五十組答案"] },
          },
        ]}
      />,
    );

    expect(screen.getAllByText("第50組").length).toBeGreaterThan(0);
    expect(screen.getByText("第五十組答案")).toBeInTheDocument();
    expect(screen.getByText("1 / 50")).toBeInTheDocument();
  });
});
