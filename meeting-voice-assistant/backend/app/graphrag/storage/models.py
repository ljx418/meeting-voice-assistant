from typing import Optional
from sqlalchemy import String, Integer, Float, Text, TIMESTAMP, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    namespace: Mapped[str] = mapped_column(String, nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    indexed_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )
    chunk_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    entity_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    entities: Mapped[list["Entity"]] = relationship(
        "Entity", back_populates="document", foreign_keys="Entity.doc_id"
    )


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    doc_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("documents.id"), nullable=True
    )
    namespace: Mapped[str] = mapped_column(String, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    community_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP")
    )

    document: Mapped[Optional["Document"]] = relationship(
        "Document", back_populates="entities", foreign_keys=[doc_id]
    )
    source_relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        back_populates="source_entity",
        foreign_keys="Relationship.source_entity_id",
    )
    target_relationships: Mapped[list["Relationship"]] = relationship(
        "Relationship",
        back_populates="target_entity",
        foreign_keys="Relationship.target_entity_id",
    )


class Relationship(Base):
    __tablename__ = "relationships"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_entity_id: Mapped[str] = mapped_column(
        String, ForeignKey("entities.id"), nullable=False
    )
    target_entity_id: Mapped[str] = mapped_column(
        String, ForeignKey("entities.id"), nullable=False
    )
    relation_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    namespace: Mapped[str] = mapped_column(String, nullable=False, index=True)

    source_entity: Mapped["Entity"] = relationship(
        "Entity",
        back_populates="source_relationships",
        foreign_keys=[source_entity_id],
    )
    target_entity: Mapped["Entity"] = relationship(
        "Entity",
        back_populates="target_relationships",
        foreign_keys=[target_entity_id],
    )


class Community(Base):
    __tablename__ = "communities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    namespace: Mapped[str] = mapped_column(String, nullable=False, index=True)
    level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
