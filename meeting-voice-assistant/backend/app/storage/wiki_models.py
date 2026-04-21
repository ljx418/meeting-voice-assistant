"""
Wiki 存储模型

基于 ADR-002 设计文档实现 SQLAlchemy 模型
"""

from typing import Optional
from sqlalchemy import String, Integer, Text, Boolean, TIMESTAMP, ForeignKey, text, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime


class Base(DeclarativeBase):
    pass


class WikiPage(Base):
    """Wiki 页面"""
    __tablename__ = "wiki_pages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("categories.id"), nullable=True)
    meeting_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), onupdate=text("CURRENT_TIMESTAMP"))
    created_by: Mapped[str] = mapped_column(String, default="system")
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="pages")
    versions: Mapped[list["PageVersion"]] = relationship("PageVersion", back_populates="page", cascade="all, delete-orphan")
    page_tags: Mapped[list["PageTag"]] = relationship("PageTag", back_populates="page", cascade="all, delete-orphan")


class Category(Base):
    """Wiki 分类"""
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    parent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("categories.id"), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side=[id], back_populates="children")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
    pages: Mapped[list["WikiPage"]] = relationship("WikiPage", back_populates="category")


class Tag(Base):
    """Wiki 标签"""
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    color: Mapped[str] = mapped_column(String, default="#6B7280")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    page_tags: Mapped[list["PageTag"]] = relationship("PageTag", back_populates="tag", cascade="all, delete-orphan")


class PageTag(Base):
    """页面-标签关联表"""
    __tablename__ = "page_tags"

    page_id: Mapped[str] = mapped_column(String, ForeignKey("wiki_pages.id", ondelete="CASCADE"), primary_key=True)
    tag_id: Mapped[str] = mapped_column(String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    page: Mapped["WikiPage"] = relationship("WikiPage", back_populates="page_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="page_tags")


class PageVersion(Base):
    """页面版本历史"""
    __tablename__ = "page_versions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    page_id: Mapped[str] = mapped_column(String, ForeignKey("wiki_pages.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String, default="system")
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    page: Mapped["WikiPage"] = relationship("WikiPage", back_populates="versions")
