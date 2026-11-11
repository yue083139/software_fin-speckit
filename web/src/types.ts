// 伺服器推來的畫面狀態（contracts/api.md）；前端只顯示，不判定、不過濾。
export type Phase = "preparing" | "answering" | "judging" | "ended";

export interface TeacherView {
  role: "teacher";
  phase: Phase;
  teams: string[];
  joined: string[];
}

export interface StudentView {
  role: "student";
  phase: Phase;
  team: string | null;
  team_valid: boolean;
}

export type View = TeacherView | StudentView;

export const PHASE_LABEL: Record<Phase, string> = {
  preparing: "準備中",
  answering: "搶答中",
  judging: "判定中",
  ended: "已結束",
};
