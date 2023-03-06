import time
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    decode_token, jwt_required, verify_jwt_in_request

from utils.dao import get_command_data

from config.flask_config import get_db


portfolio = Blueprint("main", __name__)


@portfolio.route("/profile")
def get_profile():
    # else proceed to fetch data from database
    conn = get_db()
    commands = {
        "sales_data": """select date_trunc('day', payment_date) as payment_day, sum(amount) as daily_sum, count(amount) as daily_units
                        from public.payment group by payment_day order by payment_day""",
        "genre_ratios": """select category.name, count(category.name) as name_count from public.film_category
                        left join public.category on film_category.category_id = category.category_id group by category.name""",
        "rentals_by_staff": """select rental.staff_id, staff.first_name, staff.last_name, count(*) as count_entries from public.rental
                            right join public.staff on rental.staff_id = staff.staff_id group by staff.staff_id,
                            staff.first_name, staff.last_name, rental.staff_id""",
        "popular_films": """select count(rental.inventory_id) as times_rented, film.title from
                            public.rental left join public.inventory on rental.inventory_id = inventory.inventory_id
                            left join public.film on inventory.film_id = film.film_id group by inventory.film_id,film.title
                            order by times_rented desc""",
        "active_customers": """select case when active = 1 then 'Active' else 'Inactive' END,
                            count(active) as entries from public.customer group by active order by entries desc"""
    }
    
    return_data = {}
    
    for i in commands:
        return_data[i] = get_command_data(conn, commands[i])

    return jsonify({"all_data": return_data})
