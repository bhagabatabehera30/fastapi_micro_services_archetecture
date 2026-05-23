from sqlalchemy.orm import Mapped, mapped_column, relationship
from packages.shared.database.core import Base
from src.domain.entities.association_tables import role_permissions

class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)

    # Many-to-many relationship to Permission
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="selectin"
    )
