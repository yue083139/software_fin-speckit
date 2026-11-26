import { TEACHER_KEY_STORE, clearTeacherKey, takeTeacherKey } from "./route";

// teacher-key-hidden：金鑰只經網址帶入，載入後自網址移除，存本分頁 sessionStorage
describe("老師金鑰不留在網址列", () => {
  beforeEach(() => {
    sessionStorage.clear();
    history.replaceState(null, "", "/");
  });

  it("網址帶 key：取出、存 sessionStorage，網址只剩 #/teacher", () => {
    history.replaceState(null, "", "/#/teacher?key=abc123");
    expect(takeTeacherKey()).toBe("abc123");
    expect(sessionStorage.getItem(TEACHER_KEY_STORE)).toBe("abc123");
    expect(location.hash).toBe("#/teacher");
    expect(location.href).not.toContain("abc123");
  });

  it("重新整理（網址已無 key）仍從 sessionStorage 取得", () => {
    history.replaceState(null, "", "/#/teacher?key=abc123");
    takeTeacherKey();
    expect(takeTeacherKey()).toBe("abc123");
    expect(location.hash).toBe("#/teacher");
  });

  it("網址帶新 key 時以網址為準並覆寫", () => {
    sessionStorage.setItem(TEACHER_KEY_STORE, "old");
    history.replaceState(null, "", "/#/teacher?key=new%2Bkey");
    expect(takeTeacherKey()).toBe("new+key");
    expect(sessionStorage.getItem(TEACHER_KEY_STORE)).toBe("new+key");
  });

  it("其他查詢參數保留，只移除 key", () => {
    history.replaceState(null, "", "/#/teacher?key=abc&x=1");
    takeTeacherKey();
    expect(location.hash).toBe("#/teacher?x=1");
  });

  it("沒有 key 也沒有存過時回空字串，且不寫 localStorage", () => {
    history.replaceState(null, "", "/#/teacher");
    expect(takeTeacherKey()).toBe("");
    expect(localStorage.length).toBe(0);
  });

  it("clearTeacherKey 清掉 sessionStorage", () => {
    sessionStorage.setItem(TEACHER_KEY_STORE, "abc");
    clearTeacherKey();
    expect(sessionStorage.getItem(TEACHER_KEY_STORE)).toBeNull();
  });
});
