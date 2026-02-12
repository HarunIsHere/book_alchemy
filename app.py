"""Flask application for managing authors and books in a small library."""

import os
from datetime import date

from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/", methods=["GET"])
def home():
    """Render the home page with optional search and sorting."""
    sort = request.args.get("sort", "title")
    q = request.args.get("q", "").strip()
    msg = request.args.get("msg", "").strip()

    query = Book.query.join(Author)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                Book.title.ilike(like),
                Book.isbn.ilike(like),
                Author.name.ilike(like),
            )
        )

    if sort == "author":
        books = query.order_by(Author.name.asc(), Book.title.asc()).all()
    else:
        books = query.order_by(Book.title.asc()).all()

    message = None
    if q and len(books) == 0:
        message = f"No books match: '{q}'"

    if msg:
        message = msg

    return render_template("home.html", books=books, sort=sort, q=q, message=message)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """Add a new author to the database and render the add-author page."""
    message = None

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        birth_date_raw = request.form.get("birth_date", "").strip()
        date_of_death_raw = request.form.get("date_of_death", "").strip()

        birth_date = date.fromisoformat(birth_date_raw) if birth_date_raw else None
        date_of_death = (
            date.fromisoformat(date_of_death_raw) if date_of_death_raw else None
        )

        if not name:
            message = "Name is required."
        else:
            author = Author(
                name=name,
                birth_date=birth_date,
                date_of_death=date_of_death,
            )
            db.session.add(author)
            db.session.commit()
            message = f"Author '{name}' added successfully."

    return render_template("add_author.html", message=message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """Add a new book to the database and render the add-book page."""
    message = None
    authors = Author.query.order_by(Author.name.asc()).all()

    if request.method == "POST":
        isbn = request.form.get("isbn", "").strip()
        title = request.form.get("title", "").strip()
        publication_year_raw = request.form.get("publication_year", "").strip()
        author_id_raw = request.form.get("author_id", "").strip()

        if not isbn or not title or not author_id_raw:
            message = "ISBN, Title, and Author are required."
        else:
            publication_year = (
                int(publication_year_raw) if publication_year_raw else None
            )
            author_id = int(author_id_raw)

            book = Book(
                isbn=isbn,
                title=title,
                publication_year=publication_year,
                author_id=author_id,
            )
            db.session.add(book)

            try:
                db.session.commit()
                message = f"Book '{title}' added successfully."
            except IntegrityError:
                db.session.rollback()
                message = (
                    f"ISBN '{isbn}' already exists. Please use a unique ISBN or edit "
                    "the existing book."
                )

    return render_template("add_book.html", authors=authors, message=message)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id: int):
    """Delete a book; if its author has no remaining books, delete the author."""
    book = Book.query.get_or_404(book_id)

    author_id = book.author_id

    db.session.delete(book)
    db.session.commit()

    remaining = Book.query.filter_by(author_id=author_id).count()
    if remaining == 0:
        author = Author.query.get(author_id)
        if author is not None:
            db.session.delete(author)
            db.session.commit()

    return redirect(url_for("home", msg=f"Deleted book '{book.title}'."))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
