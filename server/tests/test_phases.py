"""階段狀態機（app-skeleton D2、D3）。"""
import asyncio
import itertools

import pytest

from quiz_server.activity import Activity, team_names
from quiz_server.phases import TRANSITIONS, Phase, PhaseError, check_transition

LEGAL = {
    (Phase.PREPARING, Phase.ANSWERING),
    (Phase.ANSWERING, Phase.ENDED),
    (Phase.ANSWERING, Phase.JUDGING),
    (Phase.JUDGING, Phase.ENDED),
    (Phase.ENDED, Phase.PREPARING),
}


@pytest.mark.parametrize("src,dst", list(itertools.product(Phase, Phase)))
def test_transition_table_exhaustive(src, dst):
    if (src, dst) in LEGAL:
        check_transition(src, dst)
    else:
        with pytest.raises(PhaseError):
            check_transition(src, dst)


def test_judging_reserved_but_classic_skips_it(ready_activity):
    assert Phase.JUDGING in TRANSITIONS
    a = ready_activity
    asyncio.run(a.start())
    asyncio.run(a.end())
    assert a.phase is Phase.ENDED


def test_concurrent_transitions_serialized(ready_activity):
    a = ready_activity

    async def go():
        return await asyncio.gather(*(a.start() for _ in range(20)), return_exceptions=True)

    results = asyncio.run(go())
    assert sum(r is None for r in results) == 1
    assert sum(isinstance(r, PhaseError) for r in results) == 19
    assert a.phase is Phase.ANSWERING


def test_reset_keeps_teams(ready_activity):
    a = ready_activity
    asyncio.run(a.configure_teams(3))
    asyncio.run(a.start())
    asyncio.run(a.end())
    asyncio.run(a.reset())
    assert a.phase is Phase.PREPARING
    assert a.teams == ["第1組", "第2組", "第3組"]


@pytest.mark.parametrize("n", [1, 51])
def test_team_count_bounds(n):
    with pytest.raises(ValueError):
        asyncio.run(Activity().configure_teams(n))


@pytest.mark.parametrize("n", [2, 12, 13, 50])
def test_team_count_accepts_new_upper_bound(n):
    a = Activity()
    asyncio.run(a.configure_teams(n))
    assert a.teams == [f"第{i}組" for i in range(1, n + 1)]


def test_team_names_50_are_unique_and_numerically_ordered():
    names = team_names(50)
    assert len(names) == len(set(names)) == 50
    assert names[4] == "第5組"
    assert names[-1] == "第50組"


def test_team_count_only_when_preparing(ready_activity):
    a = ready_activity
    asyncio.run(a.start())
    with pytest.raises(PhaseError):
        asyncio.run(a.configure_teams(5))


def test_concurrent_join_same_team_once():
    a = Activity()

    async def go():
        return await asyncio.gather(*(a.join("第1組") for _ in range(10)), return_exceptions=True)

    results = asyncio.run(go())
    assert sum(isinstance(r, str) for r in results) == 1
