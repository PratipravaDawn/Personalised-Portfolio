from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


class Store(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    key: Mapped[str] = mapped_column(String(8), nullable=False)
    mail: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    about: Mapped[str] = mapped_column(String(100), nullable=True)
    profile: Mapped[str] = mapped_column(String(100), nullable=True)


class Img(db.Model):
    __bind_key__ = "img"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500))
    image_path: Mapped[str] = mapped_column(String(100))
