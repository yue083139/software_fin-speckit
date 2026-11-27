import { Tag } from "antd";
import type React from "react";
import { Section } from "../ui";

export interface PodiumPlace {
  rank: 1 | 2 | 3;
  score: number;
  teams: string[];
}

const MEDAL: Record<PodiumPlace["rank"], string> = { 1: "🥇", 2: "🥈", 3: "🥉" };
// 領獎台慣例：亞軍在左、冠軍居中、季軍在右
const STAND_ORDER: PodiumPlace["rank"][] = [2, 1, 3];

/**
 * 只用伺服器在結束後送來的 `team_scores` 排名次，口徑同伺服器 `results.leaderboard`：
 * 同分同名次、下一名跳號（1、1、3），同名次內依 `team_scores` 的鍵序（＝伺服器組別順序）。
 * 0 分不上台：沒得分的組別站上領獎台沒有意義。
 */
export function podiumPlaces(scores: Record<string, number>): PodiumPlace[] {
  const entries = Object.entries(scores).filter(([, s]) => s > 0);
  const places: PodiumPlace[] = [];
  for (const [team, score] of entries) {
    const rank = 1 + entries.filter(([, s]) => s > score).length;
    if (rank > 3) continue;
    const place = places.find((p) => p.rank === rank);
    if (place) place.teams.push(team);
    else places.push({ rank: rank as PodiumPlace["rank"], score, teams: [team] });
  }
  return places.sort((a, b) => a.rank - b.rank);
}

export const CONFETTI_COUNT = 36;
const CONFETTI_COLORS = ["--qz-accent", "--qz-accent-bright", "--qz-danger", "--qz-ok-text", "--qz-glow-3", "--qz-glow-4"];

/**
 * 揭曉時灑一次彩帶（podium-confetti）。位置與時間用索引算出固定值，不在 render 內取亂數：
 * 同一份 view 重繪時 DOM 不變，動畫不會重播；只有領獎台重新掛上（揭曉、重新整理）才再灑一次。
 * 減少動態效果的使用者由 CSS 直接隱藏。
 */
function Confetti() {
  return (
    <div className="qz-confetti" aria-hidden="true" data-testid="confetti">
      {Array.from({ length: CONFETTI_COUNT }, (_, i) => (
        <span
          key={i}
          style={
            {
              left: `${(i * 37) % 100}%`,
              background: `var(${CONFETTI_COLORS[i % CONFETTI_COLORS.length]})`,
              animationDelay: `${(i % 9) * 0.12}s`,
              animationDuration: `${2.2 + (i % 5) * 0.3}s`,
              "--qz-confetti-drift": `${((i * 53) % 61) - 30}px`,
              "--qz-confetti-spin": `${((i * 97) % 720) - 360}deg`,
            } as React.CSSProperties
          }
        />
      ))}
    </div>
  );
}

// 活動結束後的前三名領獎台（results-podium）；沒有組別得分就不顯示
export function Podium({
  scores,
  scoreLabel = "得題數",
  team,
}: {
  scores: Record<string, number>;
  scoreLabel?: string;
  team?: string; // 學生端：標出本組
}) {
  const places = podiumPlaces(scores);
  if (places.length === 0) return null;
  return (
    <Section id="podium" title="領獎台">
      <Confetti />
      <div className="qz-podium" role="list" aria-label="前三名">
        {STAND_ORDER.map((rank) => {
          const place = places.find((p) => p.rank === rank);
          if (!place) return null;
          return (
            <div key={rank} className={`qz-podium-place qz-podium-${rank}`} role="listitem" aria-label={`第 ${rank} 名`}>
              <div className="qz-podium-teams">
                {place.teams.map((t) => (
                  <div key={t} className="qz-podium-team">
                    <strong>{t}</strong>
                    {t === team && <Tag color="gold">本組</Tag>}
                  </div>
                ))}
                <span className="muted">
                  {scoreLabel} {place.score}
                </span>
              </div>
              <div className="qz-podium-stand">
                <span className="qz-podium-medal" aria-hidden="true">
                  {MEDAL[rank]}
                </span>
                <span>第 {rank} 名</span>
              </div>
            </div>
          );
        })}
      </div>
    </Section>
  );
}
