import "@ant-design/v5-patch-for-react-19";
import { App as AntApp, ConfigProvider } from "antd";
import zhTW from "antd/locale/zh_TW";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import { cssVars, quizTheme } from "./theme";
import "./styles.css";

for (const [k, v] of Object.entries(cssVars())) document.documentElement.style.setProperty(k, v);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ConfigProvider locale={zhTW} theme={quizTheme} button={{ autoInsertSpace: false }}>
      {/* live-feed：快訊最多同時疊 4 則，舊的先收 */}
      <AntApp notification={{ maxCount: 4 }}>
        <App />
      </AntApp>
    </ConfigProvider>
  </StrictMode>,
);
