import type { ReactNode } from "react";
import { Backdrop } from "./ui";

/** 頁面外殼：背景光暈＋內容層。 */
export function Shell({ children }: { children: ReactNode }) {
  return (
    <>
      <Backdrop />
      <div className="qz-shell">{children}</div>
    </>
  );
}
