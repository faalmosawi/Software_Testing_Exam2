"""
Exam 2 - Bookstore API Integration Tests
==========================================
Write your tests below. Each section (Part B and Part D) is marked.
Follow the instructions in each part carefully.

Run your tests with:
    pytest test_bookstore.py -v

Run with coverage:
    pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
"""

import pytest
from bookstore_app import app


# ============================================================
# FIXTURE: Test client with isolated database (provided)
# ============================================================

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client with a temporary database."""
    db_path = str(tmp_path / "test_bookstore.db")
    monkeypatch.setattr("bookstore_db.DB_NAME", db_path)

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ============================================================
# HELPER: Create a book (provided for convenience)
# ============================================================

def create_sample_book(client, title="The Great Gatsby", author="F. Scott Fitzgerald", price=12.99):
    """Helper to create a book and return the response JSON."""
    response = client.post("/books", json={
        "title": title,
        "author": author,
        "price": price,
    })
    return response


# ============================================================
# PART B - Integration Tests (20 marks)
# Write at least 14 tests covering ALL of the following:
#
# POST /books:
#   - Create a valid book (check 201 and response body)
#   - Create with missing title (check 400)
#   - Create with empty author (check 400)
#   - Create with invalid price (check 400)
#
# GET /books:
#   - List books when empty (check 200, empty list)
#   - List books after adding 2+ books (check count)
#
# GET /books/<id>:
#   - Get an existing book (check 200)
#   - Get a non-existing book (check 404)
#
# PUT /books/<id>:
#   - Update a book's title (check 200 and new value)
#   - Update with invalid price (check 400)
#   - Update a non-existing book (check 404)
#
# DELETE /books/<id>:
#   - Delete an existing book (check 200, then confirm 404)
#   - Delete a non-existing book (check 404)
#
# Full workflow:
#   - Create -> Read -> Update -> Read again -> Delete -> Confirm gone
# ============================================================

# TODO: Write your Part B tests here

# 1. Create a valid book
def test_create_valid_book(client):
    response = create_sample_book(client)
    assert response.status_code == 201
    data = response.get_json()
    assert "book" in data
    assert data["book"]["title"] == "The Great Gatsby"
    assert data["book"]["author"] == "F. Scott Fitzgerald"
    assert data["book"]["price"] == 12.99

# 2. Create with missing title
def test_create_book_with_missing_title(client):
    response = client.post("/books", json={
        "author": "F. Scott Fitzgerald",
        "price": 12.99
    })

    data = response.get_json()
    assert response.status_code == 400
    assert data["error"] == "title, author, and price are required"

# 3. Create with empty author
def test_create_book_with_empty_author(client):
    response = client.post("/books", json={
        "title": "The Great Gatsby",
        "price": 12.99
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "title, author, and price are required"

# 4. Create with invalid price
def test_create_book_with_invalid_price(client):
    response = client.post("/books", json={
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "price": -5
    })
    
    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Price must be positive"

# 5. List books when empty (check 200, empty list)
def test_list_books_when_empty(client):
    response = client.get("/books")
    
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data["books"]) == 0

# 6. List books after adding 2+ books (check count)
def test_list_books_after_adding_books(client):
    create_sample_book(client)
    create_sample_book(client)
    
    response = client.get("/books")
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data["books"]) == 2

# 7. Get an existing book (check 200)
def test_get_existing_book(client):
    test_book = create_sample_book(client)
    book_id = test_book.get_json()["book"]["id"]
    
    response = client.get(f"/books/{book_id}")
    data = response.get_json()
    
    assert response.status_code == 200
    assert data["book"]["id"] == book_id
    assert data["book"]["title"] == "The Great Gatsby"
    assert data["book"]["author"] == "F. Scott Fitzgerald"
    assert data["book"]["price"] == 12.99

# 8. Get a non-existing book (check 404)
def test_get_non_existing_book(client):
    response = client.get("/books/100")
    data = response.get_json()
    
    assert response.status_code == 404
    assert data["error"] == "Book not found"


# 9. Update a book's title (check 200 and new value)
def test_update_book_title(client):
    test_book = create_sample_book(client)
    book_id = test_book.get_json()["book"]["id"]
    
    response = client.put(f"/books/{book_id}", json={"title": "UPDATED TITLE"})
    data = response.get_json()
    
    assert response.status_code == 200
    assert data["book"]["title"] == "UPDATED TITLE"

# 10. Update with invalid price (check 400)
def test_update_with_invalid_price(client):
    test_book = create_sample_book(client)
    book_id = test_book.get_json()["book"]["id"]
    
    response = client.put(f"/books/{book_id}", json={"price": -5})
    data = response.get_json()
    
    assert response.status_code == 400
    assert data["error"] == "Price must be positive"

# 11. Update a non-existing book (check 404)
def test_update_non_existing_book(client):
    response = client.put("/books/100", json={"title": "New Title"})
    data = response.get_json()
    
    assert response.status_code == 404
    assert data["error"] == "Book 100 not found"

# 12. Delete an existing book (check 200, then confirm 404)
def test_delete_existing_book(client):
    test_book = create_sample_book(client)
    book_id = test_book.get_json()["book"]["id"]
    
    response = client.delete(f"/books/{book_id}")
    data = response.get_json()
    
    assert response.status_code == 200
    assert data["message"] == "Book deleted"
    
    # Confirm GET returns 404
    response = client.get(f"/books/{book_id}")
    data = response.get_json()
    assert response.status_code == 404
    assert data["error"] == "Book not found"


# 13. Delete a non-existing book (check 404)
def test_delete_non_existing_book(client):
    response = client.delete("/books/100")
    data = response.get_json()
    
    assert response.status_code == 404
    assert data["error"] == "Book 100 not found"

# 14.Full workflow:
#   - Create -> Read -> Update -> Read again -> Delete -> Confirm gone
def test_full_workflow(client):
    # 1. Create
    response = create_sample_book(client)
    data = response.get_json()
    book_id = data["book"]["id"]
    
    # 2. Read
    response = client.get(f"/books/{book_id}")
    data = response.get_json()
    assert response.status_code == 200
    assert data["book"]["title"] == "The Great Gatsby"
    
    # 3. Update
    response = client.put(f"/books/{book_id}", json={"title": "UPDATED TITLE"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["book"]["title"] == "UPDATED TITLE"
    
    # 4. Read again
    response = client.get(f"/books/{book_id}")
    data = response.get_json()
    assert response.status_code == 200
    assert data["book"]["title"] == "UPDATED TITLE"
    
    # 5. Delete
    response = client.delete(f"/books/{book_id}")
    data = response.get_json()
    assert response.status_code == 200
    assert data["message"] == "Book deleted"
    
    # 6.Confirm gone
    response = client.get(f"/books/{book_id}")
    data = response.get_json()
    assert response.status_code == 404
    assert data["error"] == "Book not found"




# ============================================================
# PART D - Coverage (5 marks)
# Run: pytest test_bookstore.py --cov=bookstore_db --cov=bookstore_app --cov-report=term-missing -v
# You must achieve 85%+ coverage across both files.
# If lines are missed, add more tests above to cover them.
# ============================================================

"""
Coverage Report:
Name               Stmts   Miss  Cover   Missing
------------------------------------------------
bookstore_app.py      58      3    95%   64, 101, 107
bookstore_db.py       60      2    97%   37, 39
------------------------------------------------
TOTAL                118      5    96%
"""

# ============================================================
# BONUS (5 extra marks)
# 1. Add a search endpoint to bookstore_app.py:
#    GET /books/search?q=<query>
#    - Uses search_books() from bookstore_db.py
#    - Returns {"books": [...]} with status 200
#    - Returns {"error": "Search query is required"} with 400 if q is missing
#
# 2. Write 3 integration tests for the search endpoint:
#    - Search by title (partial match)
#    - Search by author (partial match)
#    - Search with no results (empty list)
# ============================================================

# TODO: Write your bonus tests here (optional)
# 15. Returns {"books": [...]} with status 200
def test_search_books_by_title(client):
    create_sample_book(client, title="Test Book 1")
    create_sample_book(client, title="Test Book 2")
    create_sample_book(client, title="Random Book 1")
    
    response = client.get("/books/search?q=Test")
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data["books"]) == 2

# 16. Search by author (partial match)
def test_search_books_by_author(client):
    create_sample_book(client, author="Test Author")
    create_sample_book(client, author="Test Author")
    create_sample_book(client, author="Random Author")
    
    response = client.get("/books/search?q=Random")
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data["books"]) == 1

# 17. Search with no results (empty list)
def test_search_books_no_results(client):
    create_sample_book(client, title="Test Book 1")
    create_sample_book(client, title="Test Book 2")
    
    response = client.get("/books/search?q=random")
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data["books"]) == 0
    assert data["books"] == []
