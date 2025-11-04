from __future__ import annotations

import types
import pytest

from backend.src.handlers import task_assignment_handler as handler


def make_user(role: str | None):
    return types.SimpleNamespace(role=role)


class TestListTasksByManager:
    def test_manager_not_found_raises(self, monkeypatch):
        monkeypatch.setattr(handler.user_service, "get_user", lambda _id: None)
        with pytest.raises(ValueError, match="Manager not found"):
            handler.list_tasks_by_manager(3)

    def test_user_not_manager_raises(self, monkeypatch):
        monkeypatch.setattr(handler.user_service, "get_user", lambda _id: make_user("staff"))
        with pytest.raises(ValueError, match="User is not a manager"):
            handler.list_tasks_by_manager(3)

    def test_no_teams_returns_empty(self, monkeypatch):
        monkeypatch.setattr(handler.user_service, "get_user", lambda _id: make_user("manager"))
        monkeypatch.setattr(handler.team_service, "get_team_by_manager", lambda _id: [])
        assert handler.list_tasks_by_manager(3) == {}

    def test_aggregates_tasks_by_team_and_subteam(self, monkeypatch):
        monkeypatch.setattr(handler.user_service, "get_user", lambda _id: make_user("manager"))
        teams = [
            {"team_id": 10, "team_number": "010100"},
        ]
        subteams = [
            {"team_id": 11, "team_number": "010101"},
        ]
        monkeypatch.setattr(handler.team_service, "get_team_by_manager", lambda _id: teams)
        monkeypatch.setattr(handler.team_service, "get_users_in_team", lambda tid: ([{"user_id": 1}] if tid == 10 else [{"user_id": 2}]))
        monkeypatch.setattr(handler.team_service, "get_subteam_by_team_number", lambda num: subteams if num == "010100" else [])
        # Users map to task ids (ints); ensure dedupe works
        user_tasks = {1: [101, 102], 2: [102, 103]}
        monkeypatch.setattr(handler.assignment_service, "list_tasks_for_user", lambda uid: user_tasks.get(uid, []))

        result = handler.list_tasks_by_manager(3)
        assert set(result.keys()) == {"010100", "010101"}
        assert result["010100"] == [101, 102]
        assert result["010101"] == [102, 103]


class TestListTasksByDirector:
    def test_director_not_found_raises(self, monkeypatch):
        monkeypatch.setattr(handler.user_service, "get_user", lambda _id: None)
        with pytest.raises(ValueError, match="Director not found"):
            handler.list_tasks_by_director(4)

    def test_user_not_director_raises(self, monkeypatch):
        monkeypatch.setattr(handler.user_service, "get_user", lambda _id: make_user("manager"))
        with pytest.raises(ValueError, match="User is not a director"):
            handler.list_tasks_by_director(4)

    def test_no_department_returns_empty(self, monkeypatch):
        monkeypatch.setattr(handler.user_service, "get_user", lambda _id: make_user("director"))
        monkeypatch.setattr(handler.department_service, "get_department_by_director", lambda _id: None)
        assert handler.list_tasks_by_director(4) == {}

    def test_no_teams_returns_empty(self, monkeypatch):
        monkeypatch.setattr(handler.user_service, "get_user", lambda _id: make_user("director"))
        monkeypatch.setattr(handler.department_service, "get_department_by_director", lambda _id: {"department_id": 1})
        monkeypatch.setattr(handler.team_service, "get_teams_by_department", lambda _id: [])
        assert handler.list_tasks_by_director(4) == {}

    def test_aggregates_tasks_by_team_and_subteam(self, monkeypatch):
        monkeypatch.setattr(handler.user_service, "get_user", lambda _id: make_user("director"))
        monkeypatch.setattr(handler.department_service, "get_department_by_director", lambda _id: {"department_id": 1})
        teams = [
            {"team_id": 21, "team_number": "020200"},
        ]
        subteams = [
            {"team_id": 22, "team_number": "020201"},
        ]
        monkeypatch.setattr(handler.team_service, "get_teams_by_department", lambda _id: teams)
        monkeypatch.setattr(handler.team_service, "get_users_in_team", lambda tid: ([{"user_id": 7}] if tid == 21 else [{"user_id": 8}]))
        monkeypatch.setattr(handler.team_service, "get_subteam_by_team_number", lambda num: subteams if num == "020200" else [])
        user_tasks = {7: [201, 202], 8: [202, 203]}
        monkeypatch.setattr(handler.assignment_service, "list_tasks_for_user", lambda uid: user_tasks.get(uid, []))

        result = handler.list_tasks_by_director(4)
        assert set(result.keys()) == {"020200", "020201"}
        assert result["020200"] == [201, 202]
        assert result["020201"] == [202, 203]


