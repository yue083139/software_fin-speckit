import { studentSubmit } from "../api";
import { useLiveView } from "../live";
import { PHASE_LABEL, type StudentView } from "../types";
import { AnswerForm, type Submit } from "./AnswerForm";
import { QuestionList } from "./ImportPanel";
import { StudentResults } from "./Results";
import { MODE_HINT } from "./Teacher";
import { Leaderboard, RoundStatus } from "./Round";

export function StudentPanel({ view, onSubmit = async () => {} }: { view: StudentView; onSubmit?: Submit }) {
  if (!view.team_valid)
    return (
      <p className="error">
        尚未加入組別或組別已被老師釋放，請<a href="#/">回首頁</a>重新選擇。
      </p>
    );
  const questions = view.questions ?? [];
  const mine = view.my_submissions ?? [];
  return (
    <>
      <section className="card">
        <p>
          組別：<strong>{view.team}</strong>
        </p>
        <p className="phase">
          目前階段：<strong>{PHASE_LABEL[view.phase]}</strong>
        </p>
        {view.mode && (
          <p className="muted">
            模式：{view.mode.label}。{MODE_HINT[view.mode.key] ?? ""}
          </p>
        )}
        {view.phase === "preparing" && (
          <>
            <p>等待老師開始搶答…</p>
            <QuestionList questions={questions} />
          </>
        )}
        {view.phase === "answering" && <p>搶答進行中：每題每組只能送出一次，送出後不能修改。</p>}
        {view.phase === "judging" && <p>老師判定中，揭曉前看不到其他組的答案。</p>}
      </section>
      {view.phase === "answering" && view.mode?.sequential && <TimedPanel view={view} onSubmit={onSubmit} />}
      {view.phase === "answering" && !view.mode?.sequential && (
        <AnswerForm questions={questions} submitted={mine} onSubmit={onSubmit} />
      )}
      {view.phase === "ended" && view.results && view.team && (
        <StudentResults
          team={view.team}
          results={view.results}
          scores={view.team_scores ?? {}}
          scoreLabel={view.score_label}
          winnerTag={view.mode?.key === "classic" || !view.mode ? "搶答成功" : "最早答對"}
        />
      )}
    </>
  );
}

// 時間計分：只顯示進行中那一題；揭曉後顯示本組結果與各組名次（伺服器不送他組分數）
export function TimedPanel({ view, onSubmit }: { view: StudentView; onSubmit: Submit }) {
  const round = view.round;
  const current = round ? (view.questions ?? []).filter((q) => q.number === round.question) : [];
  const last = view.revealed?.[view.revealed.length - 1];
  return (
    <>
      <section className="card">
        <RoundStatus round={round} />
        {!round && <p>等待老師開放下一題…</p>}
      </section>
      {round?.state === "open" && (
        <AnswerForm questions={current} submitted={view.my_submissions ?? []} onSubmit={onSubmit} />
      )}
      {last && (
        <section className="card">
          <h2>第 {last.question} 題揭曉</h2>
          <p>
            {!last.submitted ? "本組未作答" : last.correct ? "本組答對" : "本組答錯"}，+{last.score} 分；本組累積{" "}
            <strong>{view.my_total ?? 0}</strong> 分
          </p>
          <Leaderboard rows={view.leaderboard ?? []} team={view.team ?? undefined} />
        </section>
      )}
    </>
  );
}

export default function Student({ token }: { token: string }) {
  const { view } = useLiveView(`role=student&token=${encodeURIComponent(token)}`);
  const submit: Submit = (question, answers) => studentSubmit(token, question, answers);
  return (
    <main className="page">
      <h1>學生頁</h1>
      {view?.role === "student" ? <StudentPanel view={view} onSubmit={submit} /> : <p>連線中…</p>}
    </main>
  );
}
