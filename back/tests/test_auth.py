def test_register_user(client):
    response = client.post("/api/v1/users/", json={
        "user_data": {
            "name": "Test",
            "surname": "User",
            "login": "testuser"
        },
        "user_auth_data": {
            "email": "test@example.com",
            "password": "password123"
        }
    })
    assert response.status_code == 201
    data = response.json()
    assert data["login"] == "testuser"
    assert "id" in data

def test_login_user(client):
    client.post("/api/v1/users/", json={
        "user_data": {"name": "Test", "surname": "User", "login": "loginuser"},
        "user_auth_data": {"email": "login@example.com", "password": "password123"}
    })
    
    response = client.post("/api/v1/auth/session", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_users_me_is_patient_check(client):
    client.post("/api/v1/users/", json={
        "user_data": {"name": "Opiekun", "surname": "Test", "login": "opiekun"},
        "user_auth_data": {"email": "opiekun@test.com", "password": "pass"}
    })
    login_res = client.post("/api/v1/auth/session", json={"email": "opiekun@test.com", "password": "pass"})
    token = login_res.json()["access_token"]
    
    response = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["is_patient"] is False