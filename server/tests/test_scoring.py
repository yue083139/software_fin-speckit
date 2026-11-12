"""經典搶答規則（buzz-answering D2）。"""
import pytest

from quiz_server.scoring import (
    AccuracyRule,
    ClassicBuzzRule,
    QuestionAttrs,
    Submission,
    TimedRule,
    timed_points,
)


def sub(team: str, seq: int) -> Submission:
    return Submission(team, 1, (f"{team}答案",), seq, seq * 10)


def test_rank_by_server_sequence():
    ranked = ClassicBuzzRule().rank([sub("第3組", 7), sub("第1組", 2), sub("第2組", 5)])
    assert [(r.team, r.rank, r.is_winner, r.score) for r in ranked] == [
        ("第1組", 1, True, 1), ("第2組", 2, False, 0), ("第3組", 3, False, 0),
    ]


def test_no_submissions_no_winner():
    assert ClassicBuzzRule().rank([]) == []


def test_judgments_do_not_change_classic():
    """經典規則不判對錯；倍率則乘進得主分數（question-settings 改寫第一期的預留輸入測試）。"""
    rule = ClassicBuzzRule()
    subs = [sub("第2組", 1), sub("第1組", 2)]
    assert rule.rank(subs) == rule.rank(subs, judgments={"第2組": False})
    doubled = rule.rank(subs, judgments={"第2組": False}, attrs=QuestionAttrs(2))
    assert [(r.team, r.is_winner, r.score) for r in doubled] == [("第2組", True, 2), ("第1組", False, 0)]


@pytest.mark.parametrize("rule", [ClassicBuzzRule(), AccuracyRule()], ids=["classic", "accuracy"])
def test_multiplier_doubles(rule):
    """同一組送出紀錄在倍率 1 與 2 下每筆分數恰為兩倍、得主不變（TRD §4）。"""
    subs = [sub("第3組", 3), sub("第1組", 1), sub("第2組", 2)]
    judged = {"第1組": False, "第2組": True, "第3組": True}
    single = rule.rank(subs, judged, QuestionAttrs(1))
    double = rule.rank(subs, judged, QuestionAttrs(2))
    assert [r.score * 2 for r in single] == [r.score for r in double]
    assert [r.is_winner for r in single] == [r.is_winner for r in double]
    assert sum(r.score for r in double) > 0


def test_team_scores_count_wins():
    rule = ClassicBuzzRule()
    per_question = [rule.rank([sub("第1組", 1), sub("第2組", 2)]), rule.rank([sub("第1組", 3)]), []]
    assert rule.team_scores(["第1組", "第2組", "第3組"], per_question) == {"第1組": 2, "第2組": 0, "第3組": 0}


@pytest.mark.parametrize(("judgments", "expected", "winner"), [
    # 依 seq：第1組 1、第2組 2、第3組 3
    ({"第1組": True, "第2組": True, "第3組": True}, [1, 1, 1], "第1組"),
    ({"第1組": False, "第2組": False, "第3組": False}, [0, 0, 0], None),
    ({"第1組": False, "第2組": True, "第3組": True}, [0, 1, 1], "第2組"),
    ({"第2組": True}, [0, 1, 0], "第2組"),          # 部分未判定
    ({}, [0, 0, 0], None),
])
def test_accuracy_rule(judgments, expected, winner):
    ranked = AccuracyRule().rank([sub("第3組", 3), sub("第1組", 1), sub("第2組", 2)], judgments)
    assert [r.team for r in ranked] == ["第1組", "第2組", "第3組"]
    assert [r.rank for r in ranked] == [1, 2, 3]
    assert [r.score for r in ranked] == expected
    assert [r.correct for r in ranked] == [judgments.get(t) for t in ("第1組", "第2組", "第3組")]
    assert [r.team for r in ranked if r.is_winner] == ([winner] if winner else [])


def test_accuracy_no_submissions():
    assert AccuracyRule().rank([], {}) == []


def test_classic_correct_is_none():
    assert all(r.correct is None for r in ClassicBuzzRule().rank([sub("第1組", 1)], {"第1組": False}))


@pytest.mark.parametrize(("elapsed_ms", "limit", "multiplier", "expected"), [
    (400, 20, 1, 1000),      # 0.5 秒內滿分
    (500, 20, 1, 1000),
    (20000, 20, 1, 500),     # t = T
    (2000, 30, 1, 967),      # Kahoot 官方範例
    (1285, 5, 1, 872),       # 剛好點五：浮點寫法會得 871
    (400, 20, 2, 2000),      # 雙倍
    (25000, 20, 1, 500),     # 超過時限夾在 T（送出路徑已擋，防禦用）
])
def test_timed_points(elapsed_ms, limit, multiplier, expected):
    assert timed_points(elapsed_ms, limit, multiplier) == expected


def test_timed_rule():
    subs = [Submission("第2組", 1, ("乙",), 2, 3000), Submission("第1組", 1, ("甲",), 1, 1000),
            Submission("第3組", 1, ("丙",), 3, 9000)]
    ranked = TimedRule().rank(subs, {"第1組": False, "第2組": True, "第3組": True}, QuestionAttrs(1, 20))
    assert [(r.team, r.rank, r.is_winner, r.score) for r in ranked] == [
        ("第1組", 1, False, 0),
        ("第2組", 2, True, timed_points(3000, 20, 1)),
        ("第3組", 3, False, timed_points(9000, 20, 1)),
    ]
