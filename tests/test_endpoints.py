"""Tests for FastAPI activity registration endpoints."""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Verify that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_includes_activity_details(self, client):
        """Verify that activities include all required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_shows_correct_participant_count(self, client):
        """Verify that activities show the correct number of participants."""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        # Tennis Club should have 0 participants
        assert len(activities["Tennis Club"]["participants"]) == 0


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successful(self, client):
        """Verify successful signup to an activity."""
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "john.doe@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant(self, client):
        """Verify that signup actually adds the participant to the activity."""
        # Sign up a student
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "john.doe@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "john.doe@mergington.edu" in activities["Tennis Club"]["participants"]

    def test_signup_duplicate_email_rejected(self, client):
        """Verify that duplicate signups are rejected."""
        # Try to sign up someone already registered
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_at_capacity_rejected(self, client):
        """Verify that signup is rejected when activity is at max capacity."""
        # Tennis Club has max 8 participants and is empty, so we need to fill it
        for i in range(8):
            client.post(
                "/activities/Tennis Club/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
        
        # Try to sign up when full
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "extra.student@mergington.edu"}
        )
        assert response.status_code == 400
        assert "maximum capacity" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client):
        """Verify that signup fails for non-existent activities."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_students_to_same_activity(self, client):
        """Verify that multiple students can sign up to the same activity."""
        # Sign up first student
        response1 = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "student1@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "student2@mergington.edu"}
        )
        assert response2.status_code == 200
        
        # Verify both are registered
        activities_response = client.get("/activities")
        participants = activities_response.json()["Tennis Club"]["participants"]
        assert "student1@mergington.edu" in participants
        assert "student2@mergington.edu" in participants
        assert len(participants) == 2


class TestUnregister:
    """Tests for the POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successful(self, client):
        """Verify successful unregistration from an activity."""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self, client):
        """Verify that unregister actually removes the participant."""
        # Unregister a student
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_not_registered_student(self, client):
        """Verify that unregister fails for students not registered."""
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity(self, client):
        """Verify that unregister fails for non-existent activities."""
        response = client.post(
            "/activities/Nonexistent Club/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_frees_up_spots(self, client):
        """Verify that unregistering frees up spots for new signups."""
        # Tennis Club starts empty (max 8)
        # Fill it up
        for i in range(8):
            client.post(
                "/activities/Tennis Club/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
        
        # Try to add one more (should fail - at capacity)
        response_full = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "extra@mergington.edu"}
        )
        assert response_full.status_code == 400
        
        # Unregister one student
        client.post(
            "/activities/Tennis Club/unregister",
            params={"email": "student0@mergington.edu"}
        )
        
        # Now adding a new student should work
        response_after = client.post(
            "/activities/Tennis Club/signup",
            params={"email": "extra@mergington.edu"}
        )
        assert response_after.status_code == 200

    def test_unregister_specific_participant_only(self, client):
        """Verify that unregitering one participant doesn't affect others."""
        # Chess Club has michael and daniel
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": "michael@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify only michael was removed, not daniel
        activities_response = client.get("/activities")
        participants = activities_response.json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in participants
        assert "daniel@mergington.edu" in participants


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_index(self, client):
        """Verify that GET / redirects to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
