import { Alert, Tag } from "antd";
import { Shell } from "../Shell";
import { GlassHeader, PhaseTag, Section } from "../ui";
import { studentDraft, studentSubmit } from "../api";
import { useLiveView } from "../live";
import { PHASE_LABEL, type StudentView } from "../types";
import { AnswerForm, type Draft, type Submit } from "./AnswerForm";
import { QuestionList } from "./ImportPanel";
import { StudentResults } from "./Results";
import { MODE_HINT } from "./Teacher";
import { Leaderboard, RoundStatus } from "./Round";

export function StudentPanel({
  view,
  onSubmit = async () => {},
  onDraft,
}: {
  view: StudentView;
  onSubmit?: Submit;
  onDraft?: Draft;
}) {
  if (!view.team_valid)
    return (
      <Alert
        type="warning"
        showIcon
        message={
          <span className="error">
            尚未加入組別或組別已被老師釋放，請<a href="#/">回首頁</a>重新選擇。
          </span>
        }
      />
    );
  const questions = view.questions ?? [];
  const mine = view.my_submissions ?? [];
  return (
    <>
      <Section>
        <div className="row" style={{ justifyContent: "space-between" }}>
          <span>
            組別：<strong>{view.team}</strong>
          </span>
          <span className="phase">
            目前階段：<strong>{PHASE_LABEL[view.phase]}</strong>
          </span>
        </div>
        {view.team_play && (
          <p className="muted">
            組隊：組內任一人送出即代表全組，每題只能送出一次。
            {view.invite_code ? (
              <>
                {" "}本組邀請碼：<strong>{view.invite_code}</strong>（給組員加入用）
              </>
            ) : (
              " 開始搶答後邀請碼會換新，組員要加入請向老師索取。"
            )}
          </p>
        )}
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
      </Section>
      {view.phase === "answering" && view.mode?.sequential && (
        <TimedPanel view={view} onSubmit={onSubmit} onDraft={onDraft} />
      )}
      {view.phase === "answering" && !view.mode?.sequential && (
        <AnswerForm
          questions={questions}
          submitted={mine}
          onSubmit={onSubmit}
          drafts={view.drafts}
          onDraft={view.team_play ? onDraft : undefined}
        />
      )}
      {view.phase === "ended" && view.results && view.team && (
        <StudentResults
          team={view.team}
          results={view.results}
          scores={view.team_scores ?? {}}
          scoreLabel={view.score_label}
          winnerTag={view.mode?.key === "classic" || !view.mode ? "搶答成功" : "最早答對"}
          questions={view.questions}
        />
      )}
    </>
  );
}

// 時間計分：只顯示進行中那一題；揭曉後顯示本組結果與各組名次（伺服器不送他組分數）
export function TimedPanel({ view, onSubmit, onDraft }: { view: StudentView; onSubmit: Submit; onDraft?: Draft }) {
  const round = view.round;
  const current = round ? (view.questions ?? []).filter((q) => q.number === round.question) : [];
  const last = view.revealed?.[view.revealed.length - 1];
  return (
    <>
      <Section>
        <RoundStatus round={round} />
        {!round && <p>等待老師開放下一題…</p>}
      </Section>
      {round?.state === "open" && (
        <AnswerForm
          questions={current}
          submitted={view.my_submissions ?? []}
          onSubmit={onSubmit}
          drafts={view.drafts}
          onDraft={view.team_play ? onDraft : undefined}
        />
      )}
      {last && (
        <Section>
          <h3>第 {last.question} 題揭曉</h3>
          <p>
            {!last.submitted ? "本組未作答" : last.correct ? "本組答對" : "本組答錯"}，+{last.score} 分；本組累積{" "}
            <strong>{view.my_total ?? 0}</strong> 分
          </p>
          <Leaderboard rows={view.leaderboard ?? []} team={view.team ?? undefined} />
        </Section>
      )}
    </>
  );
}

export default function Student({ token }: { token: string }) {
  const { view } = useLiveView(`role=student&token=${encodeURIComponent(token)}`);
  const submit: Submit = (question, answers) => studentSubmit(token, question, answers);
  // 草稿失敗（例如組員剛好送出）不打擾作答者：畫面以伺服器推來的狀態為準
  const draft: Draft = (question, answers) => {
    studentDraft(token, question, answers).catch(() => {});
  };
  const sv = view?.role === "student" ? view : null;
  return (
    <Shell>
      <GlassHeader title="課堂搶答">
        {sv?.team && <Tag className="qz-pill">{sv.team}</Tag>}
        {sv && <PhaseTag phase={sv.phase} />}
      </GlassHeader>
      <main className="qz-narrow">
        {sv ? (
          <StudentPanel view={sv} onSubmit={submit} onDraft={draft} />
        ) : (
          <Section>
            <p>連線中…</p>
          </Section>
        )}
      </main>
    </Shell>
  );
}
