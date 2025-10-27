from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.models.organization import Organization

router = APIRouter(prefix="", tags=["organizations"])


@router.post("/createOrganization", response_model=OrganizationResponse)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new organization.
    White agents use this endpoint to create their organization.
    Returns the organization with an auth_token for future API calls.
    """
    # Create new organization
    db_organization = Organization(name=organization.name)
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    
    return db_organization
