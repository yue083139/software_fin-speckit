import { Button, type ButtonProps, Card, Tag } from "antd";
import type { CSSProperties, ReactNode } from "react";
import { PHASE_LABEL, type Phase } from "./types";

/** 兩字中文按鈕不插空白（antd 預設會把「釋放」變「釋 放」，畫面文案須與既有一致）。 */
export function Btn(props: ButtonProps) {
  return <Button autoInsertSpace={false} {...props} />;
}

const PHASE_COLOR: Record<Phase, string> = {
  preparing: "default",
  answering: "processing",
  judging: "warning",
  ended: "success",
};

/** 階段膠囊。 */
export function PhaseTag({ phase }: { phase: Phase }) {
  return (
    <Tag color={PHASE_COLOR[phase]} className="qz-pill">
      {PHASE_LABEL[phase]}
    </Tag>
  );
}

/** 內容卡：`id` 供左側導覽捲動定位。 */
export function Section({
  id,
  title,
  extra,
  children,
  style,
}: {
  id?: string;
  title?: ReactNode;
  extra?: ReactNode;
  children: ReactNode;
  style?: CSSProperties;
}) {
  return (
    <Card id={id} title={title} extra={extra} className="qz-card" style={style} variant="borderless">
      {children}
    </Card>
  );
}

/** 背景光暈：玻璃要透出東西才顯得出來。 */
export function Backdrop() {
  return (
    <div className="qz-backdrop" aria-hidden="true">
      <div className="qz-glow qz-glow-1" />
      <div className="qz-glow qz-glow-2" />
      <div className="qz-glow qz-glow-3" />
      <div className="qz-glow qz-glow-4" />
    </div>
  );
}

/** 玻璃頂欄：左邊品牌，右邊放狀態。 */
export function GlassHeader({ title, children }: { title: ReactNode; children?: ReactNode }) {
  return (
    <header className="qz-glass qz-header">
      <div className="qz-brand">
        <span className="qz-logo" aria-hidden="true">
          搶
        </span>
        <span className="qz-brand-text">{title}</span>
      </div>
      <div className="qz-header-extra">{children}</div>
    </header>
  );
}
