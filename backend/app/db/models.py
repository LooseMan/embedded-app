"""SQLAlchemy models for the application database."""

import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class APILog(Base):
    __tablename__ = "api_log"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    api_name: Mapped[str] = mapped_column(String(255))
    phase: Mapped[str] = mapped_column(String(50))
    result: Mapped[str] = mapped_column(String(50))
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP")
    )


class MachineStatus(Base):
    __tablename__ = "machine_status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    module: Mapped[str] = mapped_column(String(50))
    unit: Mapped[str] = mapped_column(String(50))
    status: Mapped[int] = mapped_column(Integer)


class FileCategory(Base):
    __tablename__ = "file_category"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    files: Mapped[list["File"]] = relationship(back_populates="category")


class File(Base):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("file_category.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(2048))
    size: Mapped[int] = mapped_column(Integer)
    category: Mapped[FileCategory] = relationship(back_populates="files")
    file_set_relations: Mapped[list["FileSetRel"]] = relationship(
        back_populates="file"
    )


class FileSet(Base):
    __tablename__ = "file_set"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    file_relations: Mapped[list["FileSetRel"]] = relationship(
        back_populates="file_set"
    )


class FileSetRel(Base):
    __tablename__ = "file_set_rel"

    file_set_id: Mapped[int] = mapped_column(
        ForeignKey("file_set.id"), primary_key=True
    )
    file_id: Mapped[int] = mapped_column(ForeignKey("file.id"), primary_key=True)
    file_set: Mapped[FileSet] = relationship(back_populates="file_relations")
    file: Mapped[File] = relationship(back_populates="file_set_relations")
