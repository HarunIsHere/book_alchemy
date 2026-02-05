from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __str__(self):
        return f"Author(id={self.id}, name={self.name})"

    def __repr__(self):
        return self.__str__()


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(db.Integer, nullable=True)

    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    # optional relationship (nice to have)
    author = db.relationship("Author", backref=db.backref("books", lazy=True))

    def __str__(self):
        return f"Book(id={self.id}, title={self.title}, isbn={self.isbn})"

    def __repr__(self):
        return self.__str__()