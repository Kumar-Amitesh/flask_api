from flask import request, jsonify
from app.config.db_config import get_pg_connection
from app import bcrypt
from app.utils.validate_register_data_utils import validate_register_data
from app.utils.validate_login_data_utils import validate_login_data
from flask_jwt_extended import create_access_token, set_access_cookies
import datetime
from psycopg2.extras import RealDictCursor

def register():
    print(request)
    data = request.get_json()

    errors = validate_register_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    conn = get_pg_connection()
    if not conn:
        return jsonify({"msg": "Database connection failed"}), 500

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        print(cur)

        cur.execute("SELECT id FROM users WHERE email = %s", (data["email"],))
        if cur.fetchone():
            return jsonify({"msg": "User already exists"}), 409

        hashed_password = bcrypt.generate_password_hash(
            data["password"]
        ).decode("utf-8")

        cur.execute("""
            INSERT INTO users (name, email, phone_number, password)
            VALUES (%s, %s, %s, %s)
        """, (
            data["name"],
            data["email"],
            data.get("phoneNumber"),
            hashed_password
        ))

        conn.commit()
        return jsonify({"msg": "User registered successfully"}), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"msg": "Registration failed", "error": str(e)}), 500
    finally:
        cur.close()
        conn.close()



def login():
    data = request.get_json()

    errors = validate_login_data(data)
    if errors:
        return jsonify({"errors": errors}), 400

    conn = get_pg_connection()
    if not conn:
        return jsonify({"msg": "Database connection failed"}), 500

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT id, name, email, password
            FROM users
            WHERE email = %s
        """, (data["email"],))

        user = cur.fetchone()
        if not user:
            return jsonify({"msg": "User does not exist"}), 400

        if not bcrypt.check_password_hash(
            user["password"],
            data["password"]
        ):
            return jsonify({"msg": "Invalid credentials"}), 401

        access_token = create_access_token(
            identity=str(user["id"]), 
            additional_claims={
                "email": user["email"],
                "name": user["name"]
            },
            expires_delta=datetime.timedelta(hours=1)
        )

        response = jsonify({"msg": "Logged in successfully"})
        set_access_cookies(response, access_token)

        return response, 200

    except Exception as e:
        return jsonify({"msg": "Login failed", "error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

