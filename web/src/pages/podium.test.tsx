import { render, screen, within } from "@testing-library/react";
import { CONFETTI_COUNT, Podium, podiumPlaces } from "./Podium";
import { StudentResults } from "./Results";
import { StudentPanel } from "./Student";
import { TeacherPanel } from "./Teacher";
import type { StudentView, TeacherView } from "../types";

describe("領獎台名次（podiumPlaces）", () => {
  it("依分數取前三名，0 分不上台", () => {
    expect(podiumPlaces({ 第1組: 2, 第2組: 5, 第3組: 0, 第4組: 3, 第5組: 1 })).toEqual([
      { rank: 1, score: 5, teams: ["第2組"] },
      { rank: 2, score: 3, teams: ["第4組"] },
      { rank: 3, score: 2, teams: ["第1組"] },
    ]);
  });

  it("同分同名次、下一名跳號，同名次依組別順序", () => {
    expect(podiumPlaces({ 第1組: 3, 第2組: 3, 第3組: 1, 第4組: 0 })).toEqual([
      { rank: 1, score: 3, teams: ["第1組", "第2組"] },
      { rank: 3, score: 1, teams: ["第3組"] },
    ]);
  });

  it("第三名同分全部上台；第四名以後不上台", () => {
    expect(podiumPlaces({ 第1組: 9, 第2組: 8, 第3組: 4, 第4組: 4, 第5組: 2 })).toEqual([
      { rank: 1, score: 9, teams: ["第1組"] },
      { rank: 2, score: 8, teams: ["第2組"] },
      { rank: 3, score: 4, teams: ["第3組", "第4組"] },
    ]);
  });

  it("同分搶走前三的名額時不再有第三名", () => {
    expect(podiumPlaces({ 第1組: 2, 第2組: 2, 第3組: 2, 第4組: 1 })).toEqual([
      { rank: 1, score: 2, teams: ["第1組", "第2組", "第3組"] },
    ]);
  });

  it("沒有組別得分 ⇒ 空", () => {
    expect(podiumPlaces({ 第1組: 0, 第2組: 0 })).toEqual([]);
    expect(podiumPlaces({})).toEqual([]);
  });
});

describe("領獎台畫面", () => {
  it("顯示各名次組別與分數，亞軍、冠軍、季軍由左到右", () => {
    render(<Podium scores={{ 第1組: 1, 第2組: 3, 第3組: 2 }} scoreLabel="得分" />);
    const places = within(screen.getByRole("list", { name: "前三名" })).getAllByRole("listitem");
    expect(places.map((p) => p.getAttribute("aria-label"))).toEqual(["第 2 名", "第 1 名", "第 3 名"]);
    expect(within(screen.getByRole("listitem", { name: "第 1 名" })).getByText("第2組")).toBeInTheDocument();
    expect(within(screen.getByRole("listitem", { name: "第 1 名" })).getByText("得分 3")).toBeInTheDocument();
  });

  it("沒有組別得分就不顯示領獎台", () => {
    render(<Podium scores={{ 第1組: 0 }} />);
    expect(screen.queryByText("領獎台")).not.toBeInTheDocument();
  });

  it("學生結果標出本組", () => {
    render(<StudentResults team="第2組" results={[]} scores={{ 第1組: 1, 第2組: 2 }} />);
    const first = screen.getByRole("listitem", { name: "第 1 名" });
    expect(within(first).getByText("第2組")).toBeInTheDocument();
    expect(within(first).getByText("本組")).toBeInTheDocument();
    expect(within(screen.getByRole("listitem", { name: "第 2 名" })).queryByText("本組")).not.toBeInTheDocument();
  });
});

describe("領獎台彩帶（podium-confetti）", () => {
  it("領獎台出現時灑彩帶，且對讀屏軟體隱藏", () => {
    render(<Podium scores={{ 第1組: 2, 第2組: 1 }} />);
    const confetti = screen.getByTestId("confetti");
    expect(confetti).toHaveAttribute("aria-hidden", "true");
    expect(confetti.querySelectorAll("span")).toHaveLength(CONFETTI_COUNT);
  });

  it("沒有領獎台就沒有彩帶", () => {
    render(<Podium scores={{ 第1組: 0 }} />);
    expect(screen.queryByTestId("confetti")).not.toBeInTheDocument();
  });

  it("分數更新重繪時彩帶不重播（同一批元素）", () => {
    const { rerender } = render(<Podium scores={{ 第1組: 2, 第2組: 1 }} />);
    const first = screen.getByTestId("confetti").querySelector("span");
    rerender(<Podium scores={{ 第1組: 1, 第2組: 1 }} />);
    expect(screen.getByTestId("confetti").querySelector("span")).toBe(first);
  });

  it("每片彩帶位置與顏色固定，只用 --qz-* 變量", () => {
    render(<Podium scores={{ 第1組: 1 }} />);
    const pieces = [...screen.getByTestId("confetti").querySelectorAll("span")];
    expect(pieces.every((p) => p.style.background.startsWith("var(--qz-"))).toBe(true);
    expect(new Set(pieces.map((p) => p.style.left)).size).toBeGreaterThan(10);
  });
});

describe("老師頁領獎台只在結束後出現", () => {
  const view: TeacherView = {
    role: "teacher",
    phase: "answering",
    teams: ["第1組", "第2組"],
    joined: [],
    source: "group.xlsx",
    questions: [],
    board: [],
    team_scores: { 第1組: 1, 第2組: 0 },
  };

  it("搶答中不顯示", () => {
    render(<TeacherPanel view={view} act={() => {}} upload={() => {}} />);
    expect(screen.queryByText("領獎台")).not.toBeInTheDocument();
  });

  it("結束後顯示", () => {
    render(<TeacherPanel view={{ ...view, phase: "ended" }} act={() => {}} upload={() => {}} />);
    expect(screen.getByText("領獎台")).toBeInTheDocument();
    expect(within(screen.getByRole("listitem", { name: "第 1 名" })).getByText("第1組")).toBeInTheDocument();
  });

  it("分數欄名讀伺服器的 score_label", () => {
    render(<TeacherPanel view={{ ...view, phase: "ended", score_label: "得分" }} act={() => {}} upload={() => {}} />);
    expect(within(screen.getByRole("listitem", { name: "第 1 名" })).getByText("得分 1")).toBeInTheDocument();
  });
});

describe("學生頁領獎台只在結束後出現", () => {
  const base: StudentView = {
    role: "student",
    phase: "answering",
    team: "第1組",
    team_valid: true,
    questions: [{ number: 1, labels: [""] }],
    my_submissions: [],
  };

  it("搶答中即使 view 帶了分數也不顯示", () => {
    render(<StudentPanel view={{ ...base, results: [], team_scores: { 第1組: 2 } }} />);
    expect(screen.queryByText("領獎台")).not.toBeInTheDocument();
  });

  it("結束後顯示並標出本組", () => {
    render(<StudentPanel view={{ ...base, phase: "ended", results: [], team_scores: { 第1組: 2, 第2組: 1 } }} />);
    expect(within(screen.getByRole("listitem", { name: "第 1 名" })).getByText("本組")).toBeInTheDocument();
  });
});
