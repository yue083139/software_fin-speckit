// 伺服器推來的畫面狀態（contracts/api.md）；前端只顯示，不判定、不過濾。
export type Phase = "preparing" | "answering" | "judging" | "ended";

// 模式（game-mode-framework）；新欄位皆可選，舊伺服器或測試資料缺欄時以經典模式顯示
export interface ModeInfo {
  key: string;
  label: string;
  judged?: boolean;
}

export interface QuestionOutline {
  number: number;
  labels: string[];
}

export interface TeacherView {
  role: "teacher";
  phase: Phase;
  teams: string[];
  joined: string[];
  source: string | null;
  questions: QuestionOutline[];
  board: QuestionResult[];
  team_scores: Record<string, number>;
  mode?: ModeInfo;
  modes?: ModeInfo[];
  score_label?: string;
  pending_judgments?: number;
}

export interface StudentView {
  role: "student";
  phase: Phase;
  team: string | null;
  team_valid: boolean;
  questions?: QuestionOutline[];
  my_submissions?: { question: number; answers: string[] }[];
  results?: QuestionResult[];
  team_scores?: Record<string, number>;
  mode?: ModeInfo;
  score_label?: string;
}

export interface RankedAnswer {
  team: string;
  answers: string[];
  rank: number;
  is_winner: boolean;
  score: number;
  correct?: boolean | null; // 經典為 null；判定模式為老師判定
  suggestion?: boolean | null; // 只在老師 view
}

export interface QuestionResult {
  number: number;
  labels: string[];
  ranking: RankedAnswer[];
  winner: { team: string; answers: string[] } | null;
  reference?: (string | null)[]; // 只在老師 view
}

export type View = TeacherView | StudentView;

export const PHASE_LABEL: Record<Phase, string> = {
  preparing: "準備中",
  answering: "搶答中",
  judging: "判定中",
  ended: "已結束",
};
