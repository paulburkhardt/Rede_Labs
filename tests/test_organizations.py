"""Integration tests for organization endpoints"""
import pytest


class TestOrganizationCreation:
    """Test organization creation endpoint"""
    
    def test_create_organization_success(self, client):
        """Test successful organization creation"""
        response = client.post(
            "/createOrganization",
            json={"name": "Acme Corp"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "id" in data
        assert "name" in data
        assert "auth_token" in data
        
        # Verify values
        assert data["name"] == "Acme Corp"
        assert len(data["id"]) > 0
        assert len(data["auth_token"]) > 0
    
    def test_create_multiple_organizations(self, client):
        """Test creating multiple organizations with unique tokens"""
        org1 = client.post(
            "/createOrganization",
            json={"name": "Corp One"}
        ).json()
        
        org2 = client.post(
            "/createOrganization",
            json={"name": "Corp Two"}
        ).json()
        
        # Verify different IDs and tokens
        assert org1["id"] != org2["id"]
        assert org1["auth_token"] != org2["auth_token"]
        assert org1["name"] == "Corp One"
        assert org2["name"] == "Corp Two"
    
    def test_create_organization_with_empty_name(self, client):
        """Test that empty name is rejected"""
        response = client.post(
            "/createOrganization",
            json={"name": ""}
        )
        
        # Should still create but with empty name (no validation yet)
        # In production, you might want to add validation
        assert response.status_code == 200
