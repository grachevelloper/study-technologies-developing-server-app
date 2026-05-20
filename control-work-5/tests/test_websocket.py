from starlette.websockets import WebSocketDisconnect


def test_connect_to_room_with_valid_username(client) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        joined = websocket.receive_json()

    assert joined == {"type": "joined", "room_id": "python", "username": "alice"}


def test_websocket_message_roundtrip(client) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        websocket.send_json({"type": "message", "text": "Всем привет"})
        payload = websocket.receive_json()

    assert payload == {
        "type": "message",
        "room_id": "python",
        "username": "alice",
        "text": "Всем привет",
    }


def test_two_clients_in_same_room_receive_same_message(client) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()
        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            bob.receive_json()
            alice.receive_json()
            alice.send_json({"type": "message", "text": "Общее сообщение"})

            alice_message = alice.receive_json()
            bob_message = bob.receive_json()

    expected = {
        "type": "message",
        "room_id": "python",
        "username": "alice",
        "text": "Общее сообщение",
    }
    assert alice_message == expected
    assert bob_message == expected


def test_different_rooms_do_not_receive_foreign_messages(client) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as python_ws:
        python_ws.receive_json()
        with client.websocket_connect("/ws/rooms/fastapi?username=bob") as fastapi_ws:
            fastapi_ws.receive_json()
            python_ws.send_json({"type": "message", "text": "Только для python"})
            payload = python_ws.receive_json()

    assert payload["room_id"] == "python"


def test_too_long_message_returns_error_event(client) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        websocket.send_json({"type": "message", "text": "x" * 301})
        payload = websocket.receive_json()

    assert payload == {"type": "error", "detail": "Message is too long"}


def test_disconnected_user_removed_from_room_users(client) -> None:
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()
        response = client.get("/rooms/python/users")
        assert response.json() == {"room_id": "python", "users": ["alice"]}

    response = client.get("/rooms/python/users")
    assert response.json() == {"room_id": "python", "users": []}


def test_blank_username_closes_connection(client) -> None:
    try:
        with client.websocket_connect("/ws/rooms/python?username=   "):
            pass
    except WebSocketDisconnect as exc:
        assert exc.code == 1008
    else:
        raise AssertionError("Expected websocket disconnect")
