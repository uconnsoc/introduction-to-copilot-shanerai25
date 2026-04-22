"""Pytest configuration and fixtures for FastAPI tests."""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test.
    
    This fixture ensures test isolation by resetting the in-memory
    database to its initial state before each test runs.
    """
    from src.app import activities
    
    # Store the original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball with practice and games",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and play recreational tennis",
            "schedule": "Saturdays, 10:00 AM - 12:00 PM",
            "max_participants": 8,
            "participants": []
        },
        "Art Studio": {
            "description": "Painting, drawing, and sculpture techniques",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Band": {
            "description": "Learn instruments and perform in concerts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Mondays and Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM topics through hands-on experiments",
            "schedule": "Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["ryan@mergington.edu", "mia@mergington.edu"]
        }
    }
    
    yield
    
    # Reset activities after each test
    activities.clear()
    activities.update(original_activities)
