import { btn } from "../test-utils";
import { act, fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { TeamPicker } from "./Home";
import { TeacherPanel } from "./Teacher";
import { StudentPanel } from "./Student";
import { AnswerForm } from "./AnswerForm";
import type { StudentView, TeacherView } from "../types";

const teacher: TeacherView = {
  role: "teacher",
  phase: "preparing",
  teams: ["第1組", "第2組"],
  joined: ["第1組"],
  source: "group.xlsx",
  questions: [{ number: 3, labels: [""] }],
  board: [],
  team_scores: {},
  team_play: true,
  devices: { 第1組: 3, 第2組: 0 },
  invite_codes: { 第1組: "ABC234" },
};

describe("組隊：老師", () => {
  it("準備階段可切換組隊，顯示台數與邀請碼", () => {
    const calls: [string, unknown][] = [];
    render(<TeacherPanel view={teacher} act={(p, b) => calls.push([p, b])} upload={() => {}} />);
    const box = screen.getByLabelText("組隊（一組多台裝置）");
    expect(box).toBeChecked();
    box.click();
    expect(calls).toEqual([["team-play", { enabled: false }]]);
    expect(screen.getByText(/已加入（3 台）/)).toBeInTheDocument();
    expect(screen.getByText("ABC234")).toBeInTheDocument();
  });

  it("非準備階段不能切換", () => {
    render(<TeacherPanel view={{ ...teacher, phase: "answering" }} act={() => {}} upload={() => {}} />);
    expect(screen.getByLabelText("組隊（一組多台裝置）")).toBeDisabled();
  });
});

describe("組隊：首頁", () => {
  it("組隊時已加入的組別仍可按，並帶邀請碼", () => {
    const picks: [string, string][] = [];
    render(<TeamPicker teams={["第1組", "第2組"]} joined={["第1組"]} teamPlay onPick={(t, c) => picks.push([t, c])} />);
    fireEvent.change(screen.getByLabelText("邀請碼"), { target: { value: "abc234" } });
    const button = btn(/第1組/);
    expect(button).toBeEnabled();
    button.click();
    expect(picks).toEqual([["第1組", "abc234"]]);
  });

  it("非組隊時已加入的組別停用、沒有邀請碼欄", () => {
    render(<TeamPicker teams={["第1組"]} joined={["第1組"]} teamPlay={false} onPick={() => {}} />);
    expect(btn(/第1組/)).toBeDisabled();
    expect(screen.queryByLabelText("邀請碼")).toBeNull();
  });
});

describe("組隊：學生", () => {
  const view: StudentView = {
    role: "student",
    phase: "answering",
    team: "第1組",
    team_valid: true,
    questions: [{ number: 3, labels: [""] }],
    my_submissions: [],
    team_play: true,
    invite_code: "ABC234",
    drafts: [{ question: 3, answers: ["組員的草稿"] }],
  };

  it("顯示本組邀請碼與組內草稿", () => {
    render(<StudentPanel view={view} onDraft={() => {}} />);
    expect(screen.getByText("ABC234")).toBeInTheDocument();
    expect(screen.getByText(/組內草稿：組員的草稿/)).toBeInTheDocument();
  });

  it("輸入後防抖送草稿；按套用帶入組內草稿", () => {
    vi.useFakeTimers();
    const drafts: [number, string[]][] = [];
    render(
      <AnswerForm
        questions={view.questions ?? []}
        submitted={[]}
        onSubmit={async () => {}}
        drafts={view.drafts}
        onDraft={(q, a) => drafts.push([q, a])}
      />,
    );
    const input = screen.getByLabelText("第 3 題 答案");
    fireEvent.change(input, { target: { value: "我" } });
    fireEvent.change(input, { target: { value: "我的" } });
    expect(drafts).toEqual([]);
    act(() => vi.advanceTimersByTime(400));
    expect(drafts).toEqual([[3, ["我的"]]]);
    fireEvent.click(screen.getByText("套用"));
    expect(input).toHaveValue("組員的草稿");
    vi.useRealTimers();
  });

  it("非組隊時不送草稿", () => {
    vi.useFakeTimers();
    const drafts: unknown[] = [];
    render(<AnswerForm questions={view.questions ?? []} submitted={[]} onSubmit={async () => {}} />);
    fireEvent.change(screen.getByLabelText("第 3 題 答案"), { target: { value: "x" } });
    act(() => vi.advanceTimersByTime(1000));
    expect(drafts).toEqual([]);
    vi.useRealTimers();
  });
});
