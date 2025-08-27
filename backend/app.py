from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from dotenv import load_dotenv
from supabase import Client, create_client
from functools import wraps
from datetime import timedelta
import os  
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('SECRET_KEY')
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=31)
jwt = JWTManager(app)

supabase: Client = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))    

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({"status": "error", "error": "User is not logged in", "redirect":"/login"}), 401
        return f(*args, **kwargs)
    return decorated_function

def redirect_if_logged_in(f): 
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' in session:
            return jsonify({"status":"error", "error": "user already logged in", "redirect": "/profile"}), 403
        return f(*args, **kwargs)
    return decorated_function 


@app.route("/api/login", methods=['POST'])
@redirect_if_logged_in
def login(): 
    data = request.get_json()   
    email = data.get("email")
    password = data.get("password")
    if not (email and password):
        return jsonify({"error":"Email and password are required"}), 400
    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        session.permanent = True
        session['user'] = result.user.id
        return jsonify({"message":"Login successful", "user_id": result.user.id, "redirect":"/frontend/index.html"})
    except Exception as e:
        app.logger.error(f"login failed: {e}")
        return jsonify({"Error": "could not login"}), 401


@app.route("/api/signup", methods=['POST'])
@redirect_if_logged_in
def signup():
    first_name = request.form.get('first-name')
    last_name = request.form.get('last-name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirmed_password = request.form.get('confirm-password')
    if not (first_name and last_name and email and password and confirmed_password):
        return jsonify({"error": "Missing credentials"}), 400
    
    if confirmed_password != password:
        return jsonify({"error": "passwords do not match"}), 401
    else:
        try:
            result = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            return jsonify({"message":"Sign up successful, please login", "redirect": "/login"})
        except Exception as e:
            app.logger.error(f"login failed: {e}")
            return render_template('03-signup.html', error=e)


@app.route("/api/logout")
def logout():
    session.clear()
    return jsonify({"message":"Logout successful", "redirect":"/frontend/login.html"})


@app.route("/api/tasks", methods=["POST"]) 
@login_required
def create_task():
    data = request.get_json
    title = data.get('title')
    description = None if not data.get('description') else data.get('description')
    due_date = None if not data.get('dueDate') else data.get('dueDate')

    if not title:
        return jsonify({"error":"title required"})

    task = {
        "title": title,
        "description": description,
        "due_date": due_date,
    }

    try:
        response = supabase.table("tasks").insert(task).execute()
        return jsonify({"success":"True"}), 201 
    except Exception as e:
        return jsonify({"error": f"Error is the following: {e}"})

@app.route("/api/tasks", methods=["GET"])
@login_required
def view_tasks():
    pass

@app.route("/api/tasks", methods=["PUT"])
@login_required
def update_task():
    pass

@app.route("/api/tasks", methods=["DELETE"])
@login_required
def delete_task():
    pass

if __name__ == '__main__':
    app.run(debug=True)
