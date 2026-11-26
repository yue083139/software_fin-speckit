// 伺服器推來的畫面狀態（contracts/api.md）；前端只顯示，不判定、不過濾。
export type Phase = "preparing" | "answering" | "judging" | "ended";

// 模式（game-mode-framework）；新欄位皆可選，舊伺服器或測試資料缺欄時以經典模式顯示
export interface ModeInfo {
  key: string;
  label: string;
  judged?: boolean;
  sequential?: boolean; // 逐題開放（時間計分）
}

// 目前回合（mode-timed-scoring）：同一時間對所有人相同
export interface RoundInfo {
  question: number;
  state: "open" | "closed";
  deadline_epoch_ms: number;
}

// 名次：學生版沒有 score
export interface LeaderRow {
  team: string;
  rank: number;
  score?: number;
}

export interface QuestionOutline {
  number: number;
  labels: string[];
  multiplier?: number; // question-settings：1 或 2
  time_limit?: number; // 秒，時間計分模式使用
  prompts?: string[]; // question-text：每個子題的題目敘述；伺服器只在學生可看時才帶
}

export interface TeacherView {
  role: "teacher";
  phase: Phase;
  student_url?: string; // student-qr：伺服器給的學生公開網址；沒有就用本頁網址
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
  round?: RoundInfo | null;
  leaderboard?: LeaderRow[];
  team_play?: boolean; // team-mode：組隊開關
  devices?: Record<string, number>;
  invite_codes?: Record<string, string>;
}

export interface Draft {
  question: number;
  answers: string[];
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
  round?: RoundInfo | null;
  revealed?: { question: number; submitted: boolean; correct: boolean | null; score: number }[];
  my_total?: number;
  leaderboard?: LeaderRow[];
  team_play?: boolean;
  invite_code?: string | null; // 只有本組
  drafts?: Draft[]; // 組內草稿：只在搶答中、只含本組
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
  multiplier?: number;
  reference?: (string | null)[]; // 只在老師 view
}

export type View = TeacherView | StudentView;

export const PHASE_LABEL: Record<Phase, string> = {
  preparing: "準備中",
  answering: "搶答中",
  judging: "判定中",
  ended: "已結束",
};
