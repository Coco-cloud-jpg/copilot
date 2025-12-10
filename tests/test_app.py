"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that GET /activities returns a 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_has_expected_keys(self):
        """Test that each activity has expected keys"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

    def test_get_activities_has_known_activities(self):
        """Test that known activities are present"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in activities


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup"""
        response = client.post(
            "/activities/Tennis Team/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert "newstudent@mergington.edu" in response.json()["message"]

    def test_signup_nonexistent_activity(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate(self):
        """Test that duplicate signup is rejected"""
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_adds_participant(self):
        """Test that signup adds participant to activity"""
        activity_name = "Tennis Team"
        email = "testsignup@mergington.edu"
        
        # Signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister"""
        activity_name = "Drama Club"
        email = "sarah@mergington.edu"  # Already registered
        
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert "message" in response.json()
        assert email in response.json()["message"]

    def test_unregister_nonexistent_activity(self):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_not_registered(self):
        """Test unregister for student not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_removes_participant(self):
        """Test that unregister removes participant from activity"""
        activity_name = "Science Club"
        email = "avery@mergington.edu"  # Already registered
        
        # Verify participant exists
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
        
        # Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]


class TestSignupAndUnregisterFlow:
    """Integration tests for signup and unregister flow"""

    def test_signup_then_unregister(self):
        """Test signing up and then unregistering"""
        activity_name = "Art Studio"
        email = "flowtest@mergington.edu"
        
        # Verify not registered
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify registered
        activities_response = client.get("/activities")
        assert email in activities_response.json()[activity_name]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        # Verify unregistered
        activities_response = client.get("/activities")
        assert email not in activities_response.json()[activity_name]["participants"]
