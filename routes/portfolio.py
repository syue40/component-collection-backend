from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    decode_token, jwt_required, verify_jwt_in_request
from utils.dao import get_command_data
from utils.functions import split_columns_into_arrays, split_sales_data
from config.flask_config import get_db
from config.flask_config import limiter

portfolio = Blueprint("main", __name__)


@portfolio.route("/profile")
@limiter.limit("5 per minute")
def get_profile():
    # Fetch data from a sql hosted database.
    conn = get_db()
    commands = {
        "sales_data": """select date_trunc('day', payment_date) as payment_day, sum(amount) as daily_sum, count(amount) as daily_units
                        from public.payment group by payment_day order by payment_day""",
        "genre_ratios": """select category.name, count(category.name) as name_count from public.film_category
                        left join public.category on film_category.category_id = category.category_id group by category.name""",
        "rentals_by_staff": """select concat(staff.first_name, ' ', staff.last_name) as Name, count(*) as count_entries from public.rental
                            right join public.staff on rental.staff_id = staff.staff_id group by staff.staff_id,
                            staff.first_name, staff.last_name, rental.staff_id""",
        "popular_films": """select count(rental.inventory_id) as times_rented, film.title from
                            public.rental left join public.inventory on rental.inventory_id = inventory.inventory_id
                            left join public.film on inventory.film_id = film.film_id group by inventory.film_id,film.title
                            order by times_rented desc""",
        "active_customers": """select case when active = 1 then 'Active' else 'Inactive' END,
                            count(active) as entries from public.customer group by active order by entries desc""",
        "total_clients": """select count(distinct(customer.customer_id)) from public.customer""",
        "lifetime_sales": """select sum(amount) from public.payment""",
        "operational_countries": """select count(distinct(country_id)) from public.country""",
        "total_genres": """select count(distinct(category_id)) from public.category""",
        "different_languages": """select count(language_id) from public.language""",
        "movies": """select count(inventory_id) from public.inventory"""
    }

    return_data = {}

    for i in commands:
        temp_data = get_command_data(conn, commands[i])
        num_columns = len(temp_data[0])
        match num_columns:
            case 2:
                split_data = split_columns_into_arrays(temp_data)
                return_data[i] = split_data
            case 3:
                column_data = split_sales_data(temp_data)
                return_data[i] = column_data
            case _:
                return_data[i] = temp_data

    return jsonify({"data": return_data})
