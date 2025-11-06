
from fastapi import HTTPException
from pytest import Session
from sqlalchemy import and_
def model_dumb(model):

    if not model:
        return None
    return {
        column.name: getattr(model, column.name) for column in model.__table__.columns
    }

def commit(db: Session):
    db.commit()

def get_row(db: Session, model_class, **kwargs):
    query = db.query(model_class)
    where_list = []
    
    for key, value in kwargs.items():
        attr = getattr(model_class, key)
        where_list.append(attr == value)     
    
    query = query.filter(and_(*where_list)).first()

    return query if query else None

def get_rows(db: Session, model_class, **kwargs):
    query = db.query(model_class)
    where_list = []
    
    for key, value in kwargs.items():
        attr = getattr(model_class, key)
        where_list.append(attr == value)
    
    query = query.filter(and_(*where_list)).all()

    return query if query else None



def insert_data_flush(db:Session, model_class,  **kwargs):
    new_data = model_class(**kwargs)
    db.add(new_data)
    db.flush()
 
    return new_data

def insert_data(db:Session, model_class,  **kwargs):
    new_data = model_class(**kwargs)
    db.add(new_data)
   
   
    return {key: value for key, value in kwargs.items()}

def update_data(db:Session, model_class, *args ,**kwargs):
   
    query = db.query(model_class).filter(*args).first()
    
    conditions = []
    
    print(args  )
    print(kwargs)
    if not query:
        raise HTTPException(status_code=404, detail="data not found")
    for key, value in kwargs.items():
        if hasattr(query, key):
            setattr(query, key, value)

   
    return query




def delete_data(db: Session, model_class, *args):
    records = db.query(model_class).filter(*args).all()
    if not records:
        raise HTTPException(status_code=404, detail="Data not found")

    for record in records:
        db.delete(record)
        


def create_error(mes: str):
    raise HTTPException(status_code=400, detail={"error": "Validation failed", "message": mes})