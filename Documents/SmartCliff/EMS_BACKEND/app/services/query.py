from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from app.models.query import Query

class QueryService:

    # Get all queries (admin)
    def get_all_queries(self, db: Session, status: str = None) -> List[Query]:
        query = db.query(Query)
        if status:
            query = query.filter(Query.status == status)
        return query.all()

    # Respond to query (admin)
    def respond_to_query(self, db: Session, query_id: int, response: str):
        query_obj = db.query(Query).filter(Query.query_id == query_id).first()
        if not query_obj:
            raise HTTPException(status_code=404, detail="Query not found")
        query_obj.admin_response = response
        query_obj.status = "responded"
        db.commit()
        db.refresh(query_obj)
        return query_obj

    # Close query (admin)
    def close_query(self, db: Session, query_id: int):
        query_obj = db.query(Query).filter(Query.query_id == query_id).first()
        if not query_obj:
            raise HTTPException(status_code=404, detail="Query not found")
        query_obj.status = "closed"
        db.commit()
        db.refresh(query_obj)
        return query_obj

    # Create query (user)
    def create_query(self, db: Session, user_id: int, summary: str, priority: str):
        new_query = Query(
            user_id=user_id,
            query_summary=summary,
            query_priority=priority,
            status="pending"
        )
        db.add(new_query)
        db.commit()
        db.refresh(new_query)
        return new_query

    # Get single query
    def get_query(self, db: Session, query_id: int):
        query_obj = db.query(Query).filter(Query.query_id == query_id).first()
        if not query_obj:
            raise HTTPException(status_code=404, detail="Query not found")
        return query_obj


query_service = QueryService()
