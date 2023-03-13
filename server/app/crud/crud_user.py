from typing import Any, Dict, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.crud.base import CRUDBase
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            name=obj_in.name,
            email=obj_in.email,
            hashed_password=hash_password(obj_in.password),
        )

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        return db_obj

    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)

        if update_data["password"]:
            hashed_password = hash_password(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user_by_email = self.get_by_email(db, email=email)
        if not user_by_email:
            return None

        if not verify_password(password, user_by_email.hashed_password):
            return None

        return user_by_email


user = CRUDUser(User)
