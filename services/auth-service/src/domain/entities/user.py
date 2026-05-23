from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from packages.shared.database.core import Base
from src.domain.entities.association_tables import user_roles
from src.domain.entities.role import Role

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

    # Many-to-many relationship to Role
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary=user_roles,
        lazy="selectin"
    )
