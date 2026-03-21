from fastapi import FastAPI, Query
from models import BookingRequest, NewMovie, SeatHoldRequest
from utils import find_movie, calculate_ticket_cost, filter_movies_logic

app = FastAPI()

# ---------------- DATA ----------------

movies = [
    {"id": 1, "title": "Leo", "genre": "Action", "language": "Tamil", "duration_mins": 160, "ticket_price": 200, "seats_available": 28},
    {"id": 2, "title": "Jailer", "genre": "Drama", "language": "Tamil", "duration_mins": 150, "ticket_price": 180, "seats_available": 40},
    {"id": 3, "title": "Avengers", "genre": "Action", "language": "English", "duration_mins": 180, "ticket_price": 300, "seats_available": 60},
    {"id": 4, "title": "The Conjuring", "genre": "Horror", "language": "English", "duration_mins": 120, "ticket_price": 220, "seats_available": 35},
    {"id": 5, "title": "3 Idiots", "genre": "Comedy", "language": "Hindi", "duration_mins": 170, "ticket_price": 150, "seats_available": 45},
    {"id": 6, "title": "Kantara", "genre": "Drama", "language": "Kannada", "duration_mins": 155, "ticket_price": 190, "seats_available": 50}
]

bookings = []
booking_counter = 1

holds = []
hold_counter = 1

# ---------------- BASIC ----------------

@app.get("/")
def home():
    return {"message": "Welcome to Movie Booking API"}

# ---------------- MOVIES ----------------

@app.get("/movies")
def get_movies():
    total_seats = sum(m["seats_available"] for m in movies)
    return {
        "total_movies": len(movies),
        "total_seats_available": total_seats,
        "movies": movies
    }

@app.get("/movies/summary")
def get_summary():
    prices = [m["ticket_price"] for m in movies]
    total_seats = sum(m["seats_available"] for m in movies)

    genre_count = {}
    for m in movies:
        genre_count[m["genre"]] = genre_count.get(m["genre"], 0) + 1

    return {
        "total_movies": len(movies),
        "most_expensive": max(prices),
        "cheapest": min(prices),
        "total_seats": total_seats,
        "genre_count": genre_count
    }

@app.get("/movies/filter")
def filter_movies(
    genre: str = None,
    language: str = None,
    max_price: int = None,
    min_seats: int = None
):
    return {"results": filter_movies_logic(movies, genre, language, max_price, min_seats)}

@app.get("/movies/search")
def search_movies(keyword: str):
    result = [
        m for m in movies
        if keyword.lower() in m["title"].lower()
        or keyword.lower() in m["genre"].lower()
        or keyword.lower() in m["language"].lower()
    ]
    if not result:
        return {"message": "No movies found", "total_found": 0}
    return {"total_found": len(result), "movies": result}

@app.get("/movies/sort")
def sort_movies(sort_by: str = Query("ticket_price"), order: str = Query("asc")):
    valid_fields = ["ticket_price", "title", "duration_mins", "seats_available"]

    if sort_by not in valid_fields:
        return {"error": f"Invalid sort_by. Choose from {valid_fields}"}
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    sorted_list = sorted(movies, key=lambda x: x[sort_by], reverse=(order == "desc"))
    return {"sorted_by": sort_by, "order": order, "movies": sorted_list}

@app.get("/movies/page")
def paginate_movies(page: int = 1, limit: int = 3):
    total = len(movies)
    total_pages = (total + limit - 1) // limit

    if page < 1 or page > total_pages:
        return {"error": "Invalid page number"}

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "movies": movies[start:end]
    }

# 🔥 FINAL ADVANCED API (Task 20)
@app.get("/movies/browse")
def browse_movies(
    keyword: str = None,
    genre: str = None,
    language: str = None,
    sort_by: str = Query("ticket_price"),
    order: str = Query("asc"),
    page: int = 1,
    limit: int = 3
):
    result = movies

    # keyword filter
    if keyword:
        result = [
            m for m in result
            if keyword.lower() in m["title"].lower()
            or keyword.lower() in m["genre"].lower()
            or keyword.lower() in m["language"].lower()
        ]

    # genre/language filter
    if genre:
        result = [m for m in result if m["genre"] == genre]

    if language:
        result = [m for m in result if m["language"] == language]

    # sorting
    valid_fields = ["ticket_price", "title", "duration_mins", "seats_available"]

    if sort_by not in valid_fields:
        return {"error": f"Invalid sort_by. Choose from {valid_fields}"}

    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    # pagination
    total = len(result)
    total_pages = (total + limit - 1) // limit

    if page < 1 or page > total_pages:
        return {"error": "Invalid page"}

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "total_pages": total_pages,
        "page": page,
        "movies": result[start:end]
    }

# ❗ KEEP LAST
@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = find_movie(movie_id, movies)
    return movie if movie else {"error": "Movie not found"}

# ---------------- BOOKINGS ----------------

@app.get("/bookings")
def get_bookings():
    return {"bookings": bookings}

@app.get("/bookings/search")
def search_bookings(customer_name: str):
    result = [b for b in bookings if customer_name.lower() in b["customer_name"].lower()]
    if not result:
        return {"message": "No bookings found", "total_found": 0}
    return {"total_found": len(result), "bookings": result}

@app.get("/bookings/sort")
def sort_bookings(sort_by: str = "total_cost", order: str = "asc"):
    valid_fields = ["total_cost", "seats"]

    if sort_by not in valid_fields:
        return {"error": f"Choose from {valid_fields}"}

    sorted_list = sorted(bookings, key=lambda x: x.get(sort_by, 0), reverse=(order == "desc"))
    return {"bookings": sorted_list}

@app.get("/bookings/page")
def paginate_bookings(page: int = 1, limit: int = 3):
    total = len(bookings)
    total_pages = (total + limit - 1) // limit

    if page < 1 or page > total_pages:
        return {"error": "Invalid page"}

    start = (page - 1) * limit
    end = start + limit

    return {"page": page, "total_pages": total_pages, "bookings": bookings[start:end]}

@app.post("/bookings")
def create_booking(request: BookingRequest):
    global booking_counter

    movie = find_movie(request.movie_id, movies)
    if not movie:
        return {"error": "Movie not found"}

    if movie["seats_available"] < request.seats:
        return {"error": "Not enough seats"}

    pricing = calculate_ticket_cost(
        movie["ticket_price"],
        request.seats,
        request.seat_type,
        request.promo_code
    )

    movie["seats_available"] -= request.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": request.customer_name,
        "movie_title": movie["title"],
        "seats": request.seats,
        "seat_type": request.seat_type,
        "total_cost": pricing["discounted_cost"]
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# ---------------- SEAT HOLD ----------------

@app.get("/seat-hold")
def get_holds():
    return {"holds": holds}

@app.post("/seat-hold")
def create_hold(request: SeatHoldRequest):
    global hold_counter

    movie = find_movie(request.movie_id, movies)
    if not movie:
        return {"error": "Movie not found"}

    if movie["seats_available"] < request.seats:
        return {"error": "Not enough seats"}

    movie["seats_available"] -= request.seats

    hold = {
        "hold_id": hold_counter,
        "customer_name": request.customer_name,
        "movie_id": request.movie_id,
        "seats": request.seats
    }

    holds.append(hold)
    hold_counter += 1

    return hold

@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id: int):
    global booking_counter

    hold = next((h for h in holds if h["hold_id"] == hold_id), None)
    if not hold:
        return {"error": "Hold not found"}

    movie = find_movie(hold["movie_id"], movies)

    booking = {
        "booking_id": booking_counter,
        "customer_name": hold["customer_name"],
        "movie_title": movie["title"],
        "seats": hold["seats"],
        "seat_type": "standard",
        "total_cost": hold["seats"] * movie["ticket_price"]
    }

    bookings.append(booking)
    holds.remove(hold)
    booking_counter += 1

    return booking

@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id: int):
    hold = next((h for h in holds if h["hold_id"] == hold_id), None)
    if not hold:
        return {"error": "Hold not found"}

    movie = find_movie(hold["movie_id"], movies)
    movie["seats_available"] += hold["seats"]

    holds.remove(hold)
    return {"message": "Hold released"}
