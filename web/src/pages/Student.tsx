import { useLiveView } from "../live";
import { PHASE_LABEL, type StudentView } from "../types";

export function StudentPanel({ view }: { view: StudentView }) {
  if (!view.team_valid)
    return (
      <p className="error">
        尚未加入組別或組別已被老師釋放，請<a href="#/">回首頁</a>重新選擇。
      </p>
    );
  return (
    <section className="card">
      <p>
        組別：<strong>{view.team}</strong>
      </p>
      <p className="phase">
        目前階段：<strong>{PHASE_LABEL[view.phase]}</strong>
      </p>
      {view.phase === "preparing" && <p>等待老師開始搶答…</p>}
    </section>
  );
}

export default function Student({ token }: { token: string }) {
  const { view } = useLiveView(`role=student&token=${encodeURIComponent(token)}`);
  return (
    <main className="page">
      <h1>學生頁</h1>
      {view?.role === "student" ? <StudentPanel view={view} /> : <p>連線中…</p>}
    </main>
  );
}
