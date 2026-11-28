import { describe, expect, it } from "vitest";
import type { TeacherView } from "./types";
import { buildResultsCsv, resultsCsvFilename } from "./resultsCsv";

const view: TeacherView = {
  role: "teacher",
  phase: "ended",
  teams: ["第1組", "第2組"],
  joined: [],
  source: "group.xlsx",
  questions: [],
  board: [
    {
      number: 1,
      labels: ["（1）", "（2）"],
      ranking: [
        {
          team: "第1組",
          answers: ['CPU, "A"', "作業系統"],
          rank: 1,
          is_winner: true,
          score: 2,
          correct: true,
        },
      ],
      winner: { team: "第1組", answers: ['CPU, "A"', "作業系統"] },
    },
    {
      number: 3,
      labels: [""],
      ranking: [
        {
          team: "第2組",
          answers: [" =1+1"],
          rank: 1,
          is_winner: false,
          score: 0,
          correct: false,
        },
      ],
      winner: null,
    },
  ],
  team_scores: { 第1組: 2, 第2組: 0 },
};

describe("活動結果 CSV", () => {
  it("輸出每題每組一列，使用伺服器結果並保留未作答組別", () => {
    expect(buildResultsCsv(view)).toBe(
      "\uFEFF" +
        [
          '"題號","組別","答案","順位","是否得主","判定結果","本題得分","活動總分"',
          '"1","第1組","（1）CPU, ""A"" ／ （2）作業系統","1","是","正確","2","2"',
          '"1","第2組","","","否","","0","0"',
          '"3","第1組","","","否","","0","2"',
          '"3","第2組","\' =1+1","1","否","錯誤","0","0"',
          "",
        ].join("\r\n"),
    );
  });

  it("依來源產生安全檔名", () => {
    expect(resultsCsvFilename("group.xlsx")).toBe("group_活動結果.csv");
    expect(resultsCsvFilename("Q&A:/活動.xlsx")).toBe("Q&A__活動_活動結果.csv");
    expect(resultsCsvFilename(null)).toBe("活動結果.csv");
  });
});
