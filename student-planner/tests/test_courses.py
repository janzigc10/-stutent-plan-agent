import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_course(auth_client: AsyncClient):
    response = await auth_client.post(
        "/api/courses/",
        json={
            "name": "高等数学",
            "teacher": "张老师",
            "location": "教学楼A301",
            "weekday": 1,
            "start_time": "08:00",
            "end_time": "09:40",
            "week_start": 1,
            "week_end": 16,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "高等数学"
    assert data["weekday"] == 1


@pytest.mark.asyncio
async def test_course_api_round_trips_week_pattern_fields(auth_client: AsyncClient):
    response = await auth_client.post(
        "/api/courses/",
        json={
            "name": "practice-course",
            "weekday": 1,
            "start_time": "08:00",
            "end_time": "09:40",
            "week_start": 1,
            "week_end": 18,
            "week_pattern": "odd",
            "week_text": "Week 1-18 (odd)",
        },
    )
    assert response.status_code == 201
    created = response.json()
    assert created["week_pattern"] == "odd"
    assert created["week_text"] == "Week 1-18 (odd)"

    detail = await auth_client.get(f"/api/courses/{created['id']}")
    assert detail.status_code == 200
    assert detail.json()["week_pattern"] == "odd"
    assert detail.json()["week_text"] == "Week 1-18 (odd)"

    listing = await auth_client.get("/api/courses/")
    assert listing.status_code == 200
    assert any(
        course["week_pattern"] == "odd" and course["week_text"] == "Week 1-18 (odd)"
        for course in listing.json()
    )


@pytest.mark.asyncio
async def test_list_courses(auth_client: AsyncClient):
    await auth_client.post(
        "/api/courses/",
        json={"name": "线性代数", "weekday": 2, "start_time": "10:00", "end_time": "11:40"},
    )
    response = await auth_client.get("/api/courses/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


@pytest.mark.asyncio
async def test_update_course(auth_client: AsyncClient):
    create = await auth_client.post(
        "/api/courses/",
        json={"name": "概率论", "weekday": 3, "start_time": "14:00", "end_time": "15:40"},
    )
    course_id = create.json()["id"]
    response = await auth_client.patch(f"/api/courses/{course_id}", json={"location": "教学楼B205"})
    assert response.status_code == 200
    assert response.json()["location"] == "教学楼B205"


@pytest.mark.asyncio
async def test_delete_course(auth_client: AsyncClient):
    create = await auth_client.post(
        "/api/courses/",
        json={"name": "英语", "weekday": 4, "start_time": "08:00", "end_time": "09:40"},
    )
    course_id = create.json()["id"]
    response = await auth_client.delete(f"/api/courses/{course_id}")
    assert response.status_code == 204
    response = await auth_client.get(f"/api/courses/{course_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_course_not_found(auth_client: AsyncClient):
    response = await auth_client.get("/api/courses/nonexistent")
    assert response.status_code == 404
