from unittest.mock import AsyncMock, patch
from app.schemas.spoonacular import DailyPlanResponse, Nutrients

mock_plan_response = DailyPlanResponse(
    meals=[
        {"id": 1, "title": "Test Meal 1", "readyInMinutes": 30, "servings": 1, "sourceUrl": "http://test.com"},
        {"id": 2, "title": "Test Meal 2", "readyInMinutes": 30, "servings": 1, "sourceUrl": "http://test.com"},
        {"id": 3, "title": "Test Meal 3", "readyInMinutes": 30, "servings": 1, "sourceUrl": "http://test.com"}
    ],
    nutrients=Nutrients(calories=2000, protein=100, fat=70, carbohydrates=250)
)

def test_create_dependent_and_plan(client):
    client.post("/api/v1/users/", json={
        "user_data": {"name": "Carer", "surname": "User", "login": "carer"},
        "user_auth_data": {"email": "carer@test.com", "password": "pass"}
    })
    token = client.post("/api/v1/auth/session", json={"email": "carer@test.com", "password": "pass"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    dep_res = client.post("/api/v1/dependents/create", headers=headers, json={
        "user_data": {"name": "Dependent", "surname": "User", "login": "dep1"},
        "user_auth_data": {"email": "dep@test.com", "password": "pass"}
    })
    assert dep_res.status_code == 201
    dependent_id = dep_res.json()["id"]

    client.put(f"/api/v1/health-form/{dependent_id}", headers=headers, json={
        "height": 180, "weight": 80, "age": 30, "gender": "male",
        "activity_level": "moderate", "calorie_goal": "maintain",
        "number_of_meals_per_day": 3, "medicament_usage": ""
    })
    with patch("app.services.spoonacular.Spoonacular.generate_structured_plan", new_callable=AsyncMock) as mock_spoon:
        mock_spoon.return_value = mock_plan_response
        
        plan_res = client.post(
            f"/api/v1/dependents/{dependent_id}/plan/generate?plan_date=2025-01-01", 
            headers=headers
        )
        
    assert plan_res.status_code == 200
    data = plan_res.json()
    assert data["user_id"] == dependent_id
    assert data["created_by"] != dependent_id
    assert len(data["meals"]) == 3
    assert data["meals"][0]["description"] == "Test Meal 1"