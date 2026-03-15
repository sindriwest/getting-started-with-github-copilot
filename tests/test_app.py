import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Create a test client
client = TestClient(app)

# Fixture to reset activities data before each test
@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the activities data to initial state before each test"""
    global activities
    activities = {
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
            "description": "Practice basketball skills and play friendly games",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["mia@mergington.edu", "noah@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and produce school plays and performances",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["ava@mergington.edu", "liam@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu", "elijah@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Prepare for math competitions and solve challenging problems",
            "schedule": "Fridays, 2:00 PM - 3:30 PM",
            "max_participants": 10,
            "participants": ["charlotte@mergington.edu", "benjamin@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["amelia@mergington.edu", "jack@mergington.edu"]
        }
    }

class TestActivitiesAPI:
    """Test suite for the activities API endpoints"""

    def test_get_activities(self):
        """Test GET /activities returns all activities with correct structure"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        
        # Check structure of first activity
        first_activity = next(iter(data.values()))
        required_keys = ["description", "schedule", "max_participants", "participants"]
        for key in required_keys:
            assert key in first_activity
        
        assert isinstance(first_activity["participants"], list)

    def test_get_activities_specific_activity(self):
        """Test that specific activities have expected data"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        chess_club = data["Chess Club"]
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]

    def test_signup_success(self):
        """Test successful signup for an activity"""
        # Arrange
        email = "test@mergington.edu"
        activity = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        
        result = response.json()
        assert "Signed up" in result["message"]
        
        # Verify the participant was added
        get_response = client.get("/activities")
        data = get_response.json()
        assert email in data[activity]["participants"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        activity = "NonExistentActivity"
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_signup_duplicate(self):
        """Test signing up for the same activity twice"""
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Programming Class"
        
        # Act - First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert first signup succeeds
        assert response1.status_code == 200
        
        # Act - Second signup (should fail)
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert second signup fails
        assert response2.status_code == 400
        
        result = response2.json()
        assert "already signed up" in result["detail"]

    def test_unregister_success(self):
        """Test successful unregistration from an activity"""
        # Arrange
        email = "unregister@mergington.edu"
        activity = "Gym Class"
        
        # Sign up first (setup for unregistration)
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200
        
        result = response.json()
        assert "Unregistered" in result["message"]
        
        # Verify the participant was removed
        get_response = client.get("/activities")
        data = get_response.json()
        assert email not in data[activity]["participants"]

    def test_unregister_activity_not_found(self):
        """Test unregister from non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        activity = "NonExistentActivity"
        
        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 404
        
        result = response.json()
        assert "Activity not found" in result["detail"]

    def test_unregister_not_signed_up(self):
        """Test unregistering a student who isn't signed up"""
        # Arrange
        email = "notsignedup@mergington.edu"
        activity = "Drama Club"
        
        # Act
        response = client.delete(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 400
        
        result = response.json()
        assert "not signed up" in result["detail"]

    def test_root_redirect(self):
        """Test that GET / redirects to static HTML"""
        # Arrange - No special setup needed
        
        # Act
        response = client.get("/")
        
        # Assert
        assert response.status_code == 200
        # FastAPI redirects are handled, but in test client it might return the HTML
        # This test ensures the endpoint exists and responds

    def test_signup_with_special_characters(self):
        """Test signup with activity names containing spaces and special chars"""
        # Arrange
        email = "special@mergington.edu"
        activity = "Art Workshop"  # Contains space
        
        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert
        assert response.status_code == 200