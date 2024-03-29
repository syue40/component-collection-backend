from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from utils.dao import get_command_data
from utils.functions import split_columns_into_arrays, split_sales_data, movies_to_object
from config.flask_config import get_db
from config.flask_config import limiter

portfolio = Blueprint("portfolio", __name__)

PAYMENTS_TABLE_HEADERS = ["Payment ID", "Amount Paid", "Customer ID",
                          "Customer Name", "Staff ID", "Payment Date", "Customer Email"]
FILM_DETAILS_HEADERS = ["Film Title", "Release Year", "Rental Rate",
                        "Rental Duration Days", "Replacement Cost", "Rating", "Genre", "Language"]


@portfolio.route("/user/<user_id>", methods=['GET'])
def get_user_info(user_id):
    """Get information about a user using 'id' property."""
    # conn = get_db()
    print(user_id)
    # print(request.json)
    return jsonify({"alert": "successfully fetched"})

@portfolio.route("/profile", methods=['GET'])
@limiter.limit("5 per minute")
@jwt_required()
def get_profile():
    """Fetch profile data about a user from the db."""
    conn = get_db()
    commands = {
        "sales_data": """select date_trunc('day', payment_date) as payment_day, sum(amount) 
                        as daily_sum, count(amount) as daily_units
                        from public.payment group by payment_day order by payment_day""",
        "genre_ratios": """select category.name, count(category.name) as name_count 
                        from public.film_category left join public.category on 
                        film_category.category_id = category.category_id group by category.name""",
        "rentals_by_staff": """select concat(staff.first_name, ' ', staff.last_name) as 
                            Name, count(*) as count_entries from public.rental 
                            right join public.staff on rental.staff_id = staff.staff_id group by staff.staff_id,
                            staff.first_name, staff.last_name, rental.staff_id""",
        "popular_films": """select count(rental.inventory_id) as times_rented, film.title from
                            public.rental left join public.inventory on rental.inventory_id = inventory.inventory_id
                            left join public.film on inventory.film_id = film.film_id group by 
                            inventory.film_id,film.title order by times_rented desc""",
        "active_customers": """select case when active = 1 then 'Active' else 'Inactive' END,
                            count(active) as entries from public.customer group by active 
                            order by entries desc""",
        "total_clients": """select count(distinct(customer.customer_id)) from public.customer""",
        "lifetime_sales": """select sum(amount) from public.payment""",
        "operational_countries": """select count(distinct(country_id)) from public.country""",
        "total_genres": """select count(distinct(category_id)) from public.category""",
        "different_languages": """select count(language_id) from public.language""",
        "movies": """select count(inventory_id) from public.inventory""",
        "payment_data": """select payment.payment_id, payment.amount, payment.customer_id, 
                        concat(customer.first_name, ' ', customer.last_name) as Name, payment.staff_id, 
                        date_trunc('day', payment.payment_date) as payment_date, customer.email 
                        from public.payment left join public.customer on 
                        payment.customer_id = customer.customer_id order by payment_date""",
        "films_table": """select film.title, film.release_year, film.rental_rate, 
                        film.rental_duration, film.replacement_cost, film.rating, 
                        category.name, language.name from public.film 
                        left join public.language on film.language_id = language.language_id
                        left join public.film_category on film.film_id = film_category.film_id 
                        left join public.category on film_category.category_id = 
                        category.category_id"""
    }
    return_data = {}

    try:
        movie_array_container = get_command_data(
            conn,
            """select film.film_id, film.title, count(film.title) as num_copies, 
            film.description, film.release_year, film.rental_rate, film.length, 
            film.rating, category.name as "category", language.name as "language"
            from public.inventory left join public.film on 
            inventory.film_id = film.film_id left join public.film_category on 
            film.film_id = film_category.film_id
            left join public.category on film_category.category_id = category.category_id 
            left join public.language on film.language_id = language.language_id
            group by film.title, film.film_id, category.name, language.name order by film_id"""
        )
        catalogue = movies_to_object(movie_array_container)

        for name, command in commands.items():
            temp_data = get_command_data(conn, command)
            num_columns = len(temp_data[0])
            match num_columns:
                case 2:
                    split_data = split_columns_into_arrays(temp_data)
                    return_data[name] = split_data
                case 3:
                    column_data = split_sales_data(temp_data)
                    return_data[name] = column_data
                case _:
                    return_data[name] = temp_data

        return_data["movies"] = catalogue
        return_data["payment_data"].insert(0, PAYMENTS_TABLE_HEADERS)
        return_data["films_table"].insert(0, FILM_DETAILS_HEADERS)
    except Exception: # pylint: disable=broad-except
        print("Error Fetching Data")

    return jsonify({"data": return_data})
