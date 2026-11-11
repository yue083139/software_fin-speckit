import { fireEvent, render, screen } from "@testing-library/react";
import { StudentPanel } from "./Student";
import type { StudentView } from "../types";

const base: StudentView = {
  role: "student",
  phase: "answering",
  team: "第1組",
  team_valid: true,
  questions: [
    { number: 1, labels: ["（1）", "（2）"] },
    { number: 3, labels: [""] },
  ],
  my_submissions: [],
};

describe("學生作答", () => {
  it("題組要填滿全部子題才可送出，送出帶全部答案", () => {
    const calls: [number, string[]][] = [];
    render(<StudentPanel view={base} onSubmit={async (q, a) => void calls.push([q, a])} />);
    const buttons = screen.getAllByText("搶答送出");
    fireEvent.change(screen.getByLabelText("第 1 題 （1）"), { target: { value: "CPU" } });
    expect(buttons[0]).toBeDisabled();
    fireEvent.change(screen.getByLabelText("第 1 題 （2）"), { target: { value: "作業系統" } });
    expect(buttons[0]).toBeEnabled();
    fireEvent.click(buttons[0]);
    expect(calls).toEqual([[1, ["CPU", "作業系統"]]]);
  });

  it("已送出的題目鎖定並顯示本組答案", () => {
    render(<StudentPanel view={{ ...base, my_submissions: [{ question: 3, answers: ["位址"] }] }} />);
    expect(screen.getByText(/已送出：位址/)).toBeInTheDocument();
    expect(screen.getAllByText("搶答送出")).toHaveLength(1);
  });

  it("準備中不顯示作答欄", () => {
    render(<StudentPanel view={{ ...base, phase: "preparing" }} />);
    expect(screen.queryByText("搶答送出")).toBeNull();
  });
});
