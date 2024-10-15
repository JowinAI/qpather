
from db.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def as_dict(model):
    """
    Convert an SQLAlchemy model to a dictionary.

    Args:
        model: An instance of an SQLAlchemy model.

    Returns:
        dict: A dictionary representation of the model.
    """
    return {
        "Id": model.Id,
        "Name": model.Name,
    }
