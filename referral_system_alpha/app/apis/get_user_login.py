from models import User,ImageMetadata
from sqlalchemy.orm import Session

def get_user(email: str,db: Session):

    user = db.query(User).filter(User.email == email).first()
    return user

def get_image_path(user_id:int,db: Session):
    print("Id:",user_id)
    image = db.query(ImageMetadata).filter(ImageMetadata.user_id == str(user_id)).first()
    return image.file_name

def get_ref_code(user_id:int,db: Session):

    referral = db.query(User.referral_code).filter(User.id == user_id).first()

    return referral