from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from packages.shared.database.core import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)
    phone_number: Mapped[str] = mapped_column(index=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(index=True, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(index=True, nullable=True)
    deleted_at: Mapped[datetime] = mapped_column(index=True, nullable=True)
