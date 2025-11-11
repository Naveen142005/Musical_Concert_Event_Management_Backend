from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from app.auth.auth_utils import role_requires
from app.dependencies import db
from app.schemas.query import QueryCreate, QueryResponse, RespondQueryResponse
from app.services.query import query_service

router_ = APIRouter(prefix="/admin/queries")

# Get all queries (optionally filtered by status)
@router_.get("/", response_model=List[QueryResponse])
async def get_queries(status: Optional[str] = None, db: Session = Depends(db.get_db),current_user: dict = Depends(role_requires("Admin"))):
    queries = query_service.get_all_queries(db=db, status=status)
    result = []
    for q in queries:
        result.append(QueryResponse(
            query_id=q.query_id,
            user_id=q.user_id,
            summary=q.query_summary,
            priority=q.query_priority,
            date=str(q.query_date) if q.query_date else None,
            status=q.status,
            response=q.admin_response if q.admin_response else "Response will come soon"
        ))
    return result

# Respond to a query
@router_.post("/{query_id}/respond", response_model=RespondQueryResponse)
async def respond_query(query_id: int, response: str = Form(...), db: Session = Depends(db.get_db),current_user: dict = Depends(role_requires("Admin")) ):
    updated_query = query_service.respond_to_query(db=db, query_id=query_id, response=response)
    return RespondQueryResponse(
        message="Response submitted successfully",
        query_id=updated_query.query_id,
        response=updated_query.admin_response,
        status=updated_query.status
    )

# Close a query
@router_.post("/{query_id}/close", response_model=RespondQueryResponse)
async def close_query(query_id: int, db: Session = Depends(db.get_db),current_user: dict = Depends(role_requires("Admin"))):
    closed_query = query_service.close_query(db=db, query_id=query_id)
    return RespondQueryResponse(
        message="Query closed successfully",
        query_id=closed_query.query_id,
        response=closed_query.admin_response if closed_query.admin_response else "No response",
        status=closed_query.status
    )

# View a particular query
@router_.get("/{query_id}", response_model=QueryResponse)
async def view_query(query_id: int, db: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Admin"))):
    q = query_service.get_query(db=db, query_id=query_id)
    return QueryResponse(
        query_id=q.query_id,
        user_id=q.user_id,
        summary=q.query_summary,
        priority=q.query_priority,
        date=str(q.query_date) if q.query_date else None,
        status=q.status,
        response=q.admin_response if q.admin_response else "Response will come soon"
    )



router = APIRouter(prefix="/queries", tags=["User Queries"])

# Post a new query
@router.post("/", response_model=QueryResponse)
async def post_query(query: QueryCreate, db: Session = Depends(db.get_db),current_user: dict = Depends(role_requires("Organizer", "Audience"))
):
    new_query = query_service.create_query(
        db=db,
        user_id=query.user_id,
        summary=query.query_summary,
        priority=query.query_priority
    )
    return QueryResponse(
        query_id=new_query.query_id,
        user_id=new_query.user_id,
        summary=new_query.query_summary,
        priority=new_query.query_priority,
        date=str(new_query.query_date) if new_query.query_date else None,
        status=new_query.status,
        response="Response will come soon"
    )

# Get response for a particular query
@router.get("/{query_id}", response_model=QueryResponse)
async def get_query_response(query_id: int, db: Session = Depends(db.get_db), current_user: dict = Depends(role_requires("Organizer", "Audience"))
):
    q = query_service.get_query(db=db, query_id=query_id)
    return QueryResponse(
        query_id=q.query_id,
        user_id=q.user_id,
        summary=q.query_summary,
        priority=q.query_priority,
        date=str(q.query_date) if q.query_date else None,
        status=q.status,
        response=q.admin_response if q.admin_response else "Response will come soon"
    )
