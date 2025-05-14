from models import User,ImageMetadata,PointsLedger
from sqlalchemy.orm import Session

def get_user(email: str,db: Session):

    user = db.query(User).filter(User.email == email).first()
    return user

def get_user_id(id: int,db: Session):

    if id:
        user = db.query(User).filter(User.id == int(id)).first()
        return user

def get_image_path(user_id:int,db: Session):

    image = db.query(ImageMetadata).filter(ImageMetadata.user_id == str(user_id)).first()
    return image.file_name

def get_ref_code(user_id:int,db: Session):

    referral = db.query(User.referral_code).filter(User.id == user_id).first()

    return referral

def get_user_points(user_id:int,db:Session):


    points = db.query(PointsLedger.points).filter(PointsLedger.user_id == user_id).first()
    return points.points if points else 0