import pytest
from pydantic import ValidationError
from core.schemas.activity import ActivityCreate
from core.schemas.subject import SubjectCreate


def test_subject_create_validation():

    data = SubjectCreate(name="Математика")
    assert data.name == "Математика"


def test_activity_create_defaults():

    data = ActivityCreate(name="Лаба", max_progress=5)
    assert data.name == "Лаба"
    assert data.max_progress == 5



def test_increment_logic_mock():

    class MockActivity:
        def __init__(self, current, max_val):
            self.current_progress = current
            self.max_progress = max_val

    act = MockActivity(current=0, max_val=1)
    if act.current_progress < act.max_progress:
        act.current_progress += 1
    assert act.current_progress == 1

    act_max = MockActivity(current=1, max_val=1)
    if act_max.current_progress < act_max.max_progress:
        act_max.current_progress += 1
    assert act_max.current_progress == 1


def test_decrement_logic_mock():


    class MockActivity:
        def __init__(self, current):
            self.current_progress = current

    act = MockActivity(current=1)
    if act.current_progress > 0:
        act.current_progress -= 1
    assert act.current_progress == 0

    act_zero = MockActivity(current=0)
    if act_zero.current_progress > 0:
        act_zero.current_progress -= 1
    assert act_zero.current_progress == 0  # Не ушло в -1