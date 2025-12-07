from unittest.mock import patch, AsyncMock
from app.schemas.spoonacular import DailyPlanResponse, Nutrients, RecipeResponse

def test_meal_status_notification(client):
    client.post("/api/v1/users/", json={
        "user_data": {"name": "Carer", "surname": "Boss", "login": "carer_notif"},
        "user_auth_data": {"email": "carer@n.com", "password": "pass"}
    })

    carer_token = client.post("/api/v1/auth/session", json={"email": "carer@n.com", "password": "pass"}).json()["access_token"]
    carer_headers = {"Authorization": f"Bearer {carer_token}"}

    dep_res = client.post("/api/v1/dependents/create", headers=carer_headers, json={
        "user_data": {"name": "Dep", "surname": "Kid", "login": "dep_notif"},
        "user_auth_data": {"email": "dep@n.com", "password": "pass"}
    })
    assert dep_res.status_code == 201
    dep_id = dep_res.json()["id"]

    dep_token = client.post("/api/v1/auth/session", json={"email": "dep@n.com", "password": "pass"}).json()["access_token"]
    dep_headers = {"Authorization": f"Bearer {dep_token}"}

    hf_res = client.put(f"/api/v1/health-form/{dep_id}", headers=carer_headers, json={
        "height": 150, "weight": 40, "age": 10, "gender": "male",
        "activity_level": "moderate", "calorie_goal": "maintain",
        "number_of_meals_per_day": 3, "medicament_usage": ""
    })
    assert hf_res.status_code == 200

    with patch("app.services.spoonacular.Spoonacular.generate_structured_plan", new_callable=AsyncMock) as mock_gen:
        mock_gen.return_value = DailyPlanResponse(
            meals=[
                {"id": 100, "title": "Test Soup", "readyInMinutes": 15, "servings": 1, "sourceUrl": "http://test.com"},
                {"id": 101, "title": "Test Pasta", "readyInMinutes": 15, "servings": 1, "sourceUrl": "http://test.com"}
            ],
            nutrients=Nutrients(calories=2000, protein=100, fat=50, carbohydrates=250)
        )
        plan_res = client.post(f"/api/v1/dependents/{dep_id}/plan/generate", headers=carer_headers)
        if plan_res.status_code != 200:
            print(f"BŁĄD SERWERA: {plan_res.json()}")
            
        assert plan_res.status_code == 200
        plan_id = plan_res.json()["id"]
        meal_id = plan_res.json()["meals"][0]["id"]

    patch_res = client.patch(f"/api/v1/meals/{meal_id}", headers=dep_headers, json={
        "eaten": True,
        "comment": "Yummy"
    })
    assert patch_res.status_code == 200
    notif_res = client.get("/api/v1/notifications/me", headers=carer_headers)
    assert notif_res.status_code == 200
    notifications = notif_res.json()
    assert len(notifications) > 0
    assert "eaten" in notifications[0]["message"]
    assert "Test Soup" in notifications[0]["message"]