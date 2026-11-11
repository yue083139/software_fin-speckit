import { studentSubmit } from "../api";
import { useLiveView } from "../live";
import { PHASE_LABEL, type StudentView } from "../types";
import { AnswerForm, type Submit } from "./AnswerForm";
import { QuestionList } from "./ImportPanel";

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
        {view.phase === "preparing" && (
          <>
            <p>等待老師開始搶答…</p>
            <QuestionList questions={questions} />
          </>
        )}
        {view.phase === "answering" && <p>搶答進行中：每題每組只能送出一次，送出後不能修改。</p>}
      </section>
      {view.phase === "answering" && <AnswerForm questions={questions} submitted={mine} onSubmit={onSubmit} />}
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
