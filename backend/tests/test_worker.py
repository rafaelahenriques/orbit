from app.worker.tasks import ping


def test_ping_task_returns_pong() -> None:
    # Calling a task directly runs it in-process, without a broker.
    assert ping() == "pong"
