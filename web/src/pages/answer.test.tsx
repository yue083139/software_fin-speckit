import { allBtn } from "../test-utils";
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
    const buttons = allBtn("搶答送出");
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

describe("題目敘述（question-text D5）", () => {
  it("有敘述時顯示在子題輸入欄上方", () => {
    const view: StudentView = {
      ...base,
      questions: [
        { number: 1, labels: ["（1）", "（2）"], prompts: ["大腦英文簡稱？", "作業系統稱為？"] },
        { number: 3, labels: [""], prompts: ["電腦使用幾進位？"] },
      ],
    };
    render(<StudentPanel view={view} onSubmit={async () => {}} />);
    expect(screen.getByText("大腦英文簡稱？")).toBeInTheDocument();
    expect(screen.getByText("作業系統稱為？")).toBeInTheDocument();
    expect(screen.getByText("電腦使用幾進位？")).toBeInTheDocument();
  });

  it("伺服器沒帶或為空字串時不顯示敘述段", () => {
    const view: StudentView = { ...base, questions: [{ number: 3, labels: [""], prompts: [""] }] };
    const { container } = render(<StudentPanel view={view} onSubmit={async () => {}} />);
    expect(container.querySelector(".prompt")).toBeNull();
  });
});
