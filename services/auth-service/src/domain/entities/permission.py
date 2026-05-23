from sqlalchemy.orm import Mapped, mapped_column, relationship
from packages.shared.database.core import Base
from src.domain.entities.association_tables import role_permissions

class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    module: Mapped[str] = mapped_column(index=True, nullable=False)

    # Many-to-many relationship to Role
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )
