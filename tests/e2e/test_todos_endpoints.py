from fastapi.testclient import TestClient
from uuid import uuid4

def test_todo_crud_operations(client: TestClient, auth_headers):
    # Create todo
    create_response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"description": "Test todo item"}
    )
    assert create_response.status_code == 201
    todo_data = create_response.json()
    todo_id = todo_data["id"]
    assert todo_data["description"] == "Test todo item"
    assert not todo_data["is_completed"]

    # Get all todos
    list_response = client.get("/todos/", headers=auth_headers)
    assert list_response.status_code == 200
    todos = list_response.json()
    assert len(todos) > 0
    assert any(todo["id"] == todo_id for todo in todos)

    # Get specific todo
    get_response = client.get(f"/todos/{todo_id}", headers=auth_headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == todo_id

    # Update todo
    update_response = client.put(
        f"/todos/{todo_id}",
        headers=auth_headers,
        json={"description": "Updated todo description"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated todo description"

    # Complete todo
    complete_response = client.put(f"/todos/{todo_id}/complete", headers=auth_headers)
    assert complete_response.status_code == 200
    assert complete_response.json()["is_completed"]
    assert complete_response.json()["completed_at"] is not None

    # Delete todo
    delete_response = client.delete(f"/todos/{todo_id}", headers=auth_headers)
    assert delete_response.status_code == 204

    # Verify deletion
    get_deleted_response = client.get(f"/todos/{todo_id}", headers=auth_headers)
    assert get_deleted_response.status_code == 404

def test_todo_authorization(client: TestClient, auth_headers):
    # Create a todo
    create_response = client.post(
        "/todos/",
        headers=auth_headers,
        json={"description": "Test todo"}
    )
    todo_id = create_response.json()["id"]

    # Try accessing without auth
    endpoints = [
        ("GET", f"/todos/"),
        ("GET", f"/todos/{todo_id}"),
        ("POST", f"/todos/"),
        ("PUT", f"/todos/{todo_id}"),
        ("PUT", f"/todos/{todo_id}/complete"),
        ("DELETE", f"/todos/{todo_id}")
    ]

    for method, endpoint in endpoints:
        response = client.request(method, endpoint)
        assert response.status_code == 401

def test_todo_not_found(client: TestClient, auth_headers):
    non_existent_id = str(uuid4())
    
    response = client.get(f"/todos/{non_existent_id}", headers=auth_headers)
    assert response.status_code == 404

    response = client.put(
        f"/todos/{non_existent_id}",
        headers=auth_headers,
        json={"description": "Update non-existent"}
    )
    assert response.status_code == 404

    response = client.put(
        f"/todos/{non_existent_id}/complete",
        headers=auth_headers
    )
    assert response.status_code == 404

    response = client.delete(f"/todos/{non_existent_id}", headers=auth_headers)
    assert response.status_code == 404 