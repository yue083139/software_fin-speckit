import { render, screen, waitFor } from "@testing-library/react";
import { App as AntApp } from "antd";
import { feedEvents, useLiveFeed } from "./LiveFeed";
import { StudentPanel } from "./Student";
import type { QuestionResult, StudentView, TeacherView } from "../types";

const q = (number: number, teams: string[]): QuestionResult => ({
  number,
  labels: [""],
  ranking: teams.map((team, i) => ({ team, answers: ["祕密答案"], rank: i + 1, is_winner: i === 0, score: i === 0 ? 1 : 0 })),
  winner: teams.length ? { team: teams[0], answers: ["祕密答案"] } : null,
});

const view = (board: QuestionResult[], extra: Partial<TeacherView> = {}): TeacherView => ({
  role: "teacher",
  phase: "answering",
  teams: ["第1組", "第2組", "第3組"],
  joined: [],
  source: "group.xlsx",
  questions: [],
  board,
  team_scores: {},
  ...extra,
});

describe("快訊事件（feedEvents）", () => {
  it("第一次收到 view 只當基準，不出通知", () => {
    expect(feedEvents(null, view([q(1, ["第1組"])]))).toEqual([]);
  });

  it("經典搶答第 1 順位是「搶下」，之後是「送出」", () => {
    const before = view([q(1, []), q(3, ["第2組"])]);
    const after = view([q(1, ["第1組"]), q(3, ["第2組", "第3組"])]);
    expect(feedEvents(before, after).map((e) => e.text)).toEqual(["第1組 搶下第 1 題！", "第3組 送出第 3 題"]);
  });

  it("非經典模式一律「送出」（得主要等判定）", () => {
    const mode = { key: "accuracy", label: "只計對錯", judged: true };
    expect(feedEvents(view([q(2, [])], { mode }), view([q(2, ["第1組"])], { mode })).map((e) => e.text)).toEqual([
      "第1組 送出第 2 題",
    ]);
  });

  it("沒有新送出、或不在搶答中都不出通知", () => {
    const same = view([q(1, ["第1組"])]);
    expect(feedEvents(same, view([q(1, ["第1組"])]))).toEqual([]);
    expect(feedEvents(view([q(1, [])]), view([q(1, ["第1組"])], { phase: "ended" }))).toEqual([]);
  });

  it("文案不含答案", () => {
    const events = feedEvents(view([q(1, [])]), view([q(1, ["第1組"])]));
    expect(events.every((e) => !e.text.includes("祕密答案"))).toBe(true);
  });
});

function Probe({ v, connected = true }: { v: TeacherView | null; connected?: boolean }) {
  useLiveFeed(v, connected);
  return null;
}

const wrap = (v: TeacherView | null, connected = true) => (
  <AntApp>
    <Probe v={v} connected={connected} />
  </AntApp>
);

describe("老師頁快訊通知", () => {
  it("新送出時右上角跳出通知，開頁時不跳", async () => {
    const { rerender } = render(
      <AntApp>
        <Probe v={view([q(1, ["第2組"])])} />
      </AntApp>,
    );
    expect(screen.queryByText(/搶下/)).not.toBeInTheDocument();
    rerender(
      <AntApp>
        <Probe v={view([q(1, ["第2組"]), q(3, ["第1組"])])} />
      </AntApp>,
    );
    expect(await screen.findByText("第1組 搶下第 3 題！")).toBeInTheDocument();
    await waitFor(() => expect(screen.queryByText("第2組 搶下第 1 題！")).not.toBeInTheDocument());
  });

  it("斷線重連後第一個新 view 只當基準，之後的新送出照跳", async () => {
    const v1 = view([q(1, ["第1組"])]);
    const { rerender } = render(wrap(v1));
    rerender(wrap(v1, false)); // 斷線
    rerender(wrap(v1, true)); // 重連：connected 先轉回、view 仍是舊的
    rerender(wrap(view([q(1, ["第1組"]), q(2, ["第2組"])]))); // 重連後第一個新 view（含斷線期間送出）
    rerender(wrap(view([q(1, ["第1組"]), q(2, ["第2組"]), q(3, ["第3組"])])));
    expect(await screen.findByText("第3組 搶下第 3 題！")).toBeInTheDocument();
    expect(screen.queryByText("第2組 搶下第 2 題！")).not.toBeInTheDocument();
  });

  it("伺服器重啟後新一輪的同組同題不被舊基準吞掉", async () => {
    const before = view([q(1, ["第1組"])]);
    const { rerender } = render(wrap(before));
    rerender(wrap(before, false)); // 伺服器重啟、斷線
    rerender(wrap(before, true));
    rerender(wrap(view([q(1, [])]))); // 新一輪，第 1 題還沒人送
    rerender(wrap(view([q(1, ["第1組"])])));
    expect(await screen.findByText("第1組 搶下第 1 題！")).toBeInTheDocument();
  });
});

describe("學生頁沒有快訊", () => {
  it("學生 view 從搶答中變多也不跳通知", () => {
    const base: StudentView = {
      role: "student",
      phase: "answering",
      team: "第1組",
      team_valid: true,
      questions: [{ number: 1, labels: [""] }],
      my_submissions: [],
    };
    const { rerender } = render(
      <AntApp>
        <StudentPanel view={base} />
      </AntApp>,
    );
    rerender(
      <AntApp>
        <StudentPanel view={{ ...base, my_submissions: [{ question: 1, answers: ["甲"] }] }} />
      </AntApp>,
    );
    expect(screen.queryByText(/搶下|送出第/)).not.toBeInTheDocument();
  });
});
