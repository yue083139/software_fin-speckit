import { screen } from "@testing-library/react";

/** antd 按鈕把文字包在 <span> 裡；停用與否看外層 <button>（web-workbench：只改查詢方式，不改斷言）。 */
export function btn(text: string | RegExp): HTMLButtonElement {
  return screen.getByText(text).closest("button") as HTMLButtonElement;
}

export function allBtn(text: string | RegExp): HTMLButtonElement[] {
  return screen.getAllByText(text).map((el) => el.closest("button") as HTMLButtonElement);
}
