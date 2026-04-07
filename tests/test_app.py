import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        # Arrange
        expected_activity_count = 9
        expected_activities = ["Chess Club", "Programming Class", "Drama Club"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        for activity in expected_activities:
            assert activity in data

    def test_activities_have_correct_structure(self, client):
        """Test that activities have required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]

        # Assert
        for field in required_fields:
            assert field in activity

    def test_activities_have_correct_participants(self, client):
        """Test that initial participants are correct"""
        # Arrange
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_programming_participants = ["emma@mergington.edu", "sophia@mergington.edu"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for participant in expected_chess_participants:
            assert participant in data["Chess Club"]["participants"]
        for participant in expected_programming_participants:
            assert participant in data["Programming Class"]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        # Arrange
        activity = "Basketball Team"
        email = "alice@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert activity in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity"""
        # Arrange
        activity = "Soccer Club"
        email = "bob@mergington.edu"

        # Act
        client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert email in data[activity]["participants"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signup for activity that doesn't exist returns 404"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        email = "test@mergington.edu"

        # Act
        response = client.post(f"/activities/{nonexistent_activity}/signup?email={email}")
        data = response.json()

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]

    def test_signup_duplicate_email_returns_400(self, client):
        """Test signup with email already in activity returns 400"""
        # Arrange
        activity = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/signup?email={existing_email}")
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"]

    def test_signup_same_email_multiple_activities(self, client):
        """Test same email can signup for multiple different activities"""
        # Arrange
        email = "charlie@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Drama Club"

        # Act
        response1 = client.post(f"/activities/{activity1}/signup?email={email}")
        response2 = client.post(f"/activities/{activity2}/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both activities have the email
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity1]["participants"]
        assert email in data[activity2]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client):
        """Test successful unregister from an activity"""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        data = response.json()

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in data["message"]
        assert email in data["message"]
        assert activity in data["message"]

    def test_unregister_removes_participant_from_activity(self, client):
        """Test that unregister actually removes the participant"""
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity}/unregister?email={email}")
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert email not in data[activity]["participants"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test unregister from activity that doesn't exist returns 404"""
        # Arrange
        nonexistent_activity = "Fake Club"
        email = "test@mergington.edu"

        # Act
        response = client.delete(f"/activities/{nonexistent_activity}/unregister?email={email}")
        data = response.json()

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in data["detail"]

    def test_unregister_not_signed_up_returns_400(self, client):
        """Test unregister when email is not in activity returns 400"""
        # Arrange
        activity = "Soccer Club"
        email = "nothere@mergington.edu"

        # Act
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        data = response.json()

        # Assert
        assert response.status_code == 400
        assert "not signed up" in data["detail"]


class TestIntegration:
    """Integration tests for signup and unregister workflows"""

    def test_signup_then_unregister_complete_flow(self, client):
        """Test complete flow: signup, verify, unregister, verify"""
        # Arrange
        email = "dave@mergington.edu"
        activity = "Art Club"

        # Act 1: Sign up
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        
        # Assert 1: Signup successful
        assert response1.status_code == 200

        # Act 2: Verify signup
        response2 = client.get("/activities")
        data2 = response2.json()

        # Assert 2: Participant added
        assert email in data2[activity]["participants"]

        # Act 3: Unregister
        response3 = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert 3: Unregister successful
        assert response3.status_code == 200

        # Act 4: Verify unregister
        response4 = client.get("/activities")
        data4 = response4.json()

        # Assert 4: Participant removed
        assert email not in data4[activity]["participants"]

    def test_multiple_signups_same_activity(self, client):
        """Test multiple participants signing up for the same activity"""
        # Arrange
        activity = "Debate Club"
        emails = ["test1@mergington.edu", "test2@mergington.edu", "test3@mergington.edu"]

        # Act
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200

        # Assert
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data[activity]["participants"]

    def test_signup_unregister_signup_same_email(self, client):
        """Test that email can re-signup after unregistering"""
        # Arrange
        activity = "Science Club"
        email = "eve@mergington.edu"

        # Act 1: Sign up
        response1 = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert 1
        assert response1.status_code == 200

        # Act 2: Unregister
        response2 = client.delete(f"/activities/{activity}/unregister?email={email}")

        # Assert 2
        assert response2.status_code == 200

        # Act 3: Sign up again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert 3: Can sign up again
        assert response3.status_code == 200

        # Act 4: Verify back in activity
        response4 = client.get("/activities")
        data4 = response4.json()

        # Assert 4
        assert email in data4[activity]["participants"]
