"""經典搶答規則（buzz-answering D2）。"""
from quiz_server.scoring import ClassicBuzzRule, Submission


def sub(team: str, seq: int) -> Submission:
    return Submission(team, 1, (f"{team}答案",), seq, seq * 10)


def test_rank_by_server_sequence():
    ranked = ClassicBuzzRule().rank([sub("第3組", 7), sub("第1組", 2), sub("第2組", 5)])
    assert [(r.team, r.rank, r.is_winner, r.score) for r in ranked] == [
        ("第1組", 1, True, 1), ("第2組", 2, False, 0), ("第3組", 3, False, 0),
    ]


def test_no_submissions_no_winner():
    assert ClassicBuzzRule().rank([]) == []


def test_reserved_inputs_do_not_change_classic():
    rule = ClassicBuzzRule()
    subs = [sub("第2組", 1), sub("第1組", 2)]
    assert rule.rank(subs) == rule.rank(subs, judgments={"第2組": False}, attrs={"points_multiplier": 2})


def test_team_scores_count_wins():
    rule = ClassicBuzzRule()
    per_question = [rule.rank([sub("第1組", 1), sub("第2組", 2)]), rule.rank([sub("第1組", 3)]), []]
    assert rule.team_scores(["第1組", "第2組", "第3組"], per_question) == {"第1組": 2, "第2組": 0, "第3組": 0}
