from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from dotenv import load_dotenv
from supabase import Client, create_client
from functools import wraps
from datetime import timedelta
import os  
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)
#Setup Json web token
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

supabase: Client = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))    



@app.route("/api/login", methods=['POST'])
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
        if not result.user:
            return jsonify({"error":"Invalid credentials"}), 401
        
        token = create_access_token(identity=result.user.id)
        return jsonify({"token":token, "user_id": result.user.id, "redirect":"/frontend/index.html"}), 200
    except Exception as e:
        app.logger.error(f"login failed: {e}")
        return jsonify({"error": "could not login"}), 500


@app.route("/api/signup", methods=['POST'])
def signup():
    data = request.get_json()

    first_name = data.get('firstName')
    last_name = data.get('lastName')
    email = data.get('email')
    password = data.get('password')
    confirmed_password = data.get('confirmPassword')
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
            return jsonify({"message":"Sign up successful, please login", "redirect": "/frontend/login.html"})
        except Exception as e:
            app.logger.error(f"login failed: {e}")
            return jsonify({"error":"Sign up failed"}), 402

@app.route("/api/logout")
def logout():
    session.clear()
    return jsonify({"message":"Logout successful", "redirect":"/frontend/login.html"}), 200


@app.route("/api/tasks", methods=["POST"]) 
@jwt_required()
def create_task():
    data = request.get_json()
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
        response = supabase.table("tasks").insert([task]).execute()
        return jsonify({"success":"True"}), 201 
    except Exception as e:
        app.logger.error(f"login failed: {e}")
        return jsonify({"error": "Could not create task"})

@app.route("/api/tasks", methods=["GET"])
@jwt_required()
def view_tasks():
    try:
        response = supabase.table("tasks").select("title", "description", "due_date").execute()
        return jsonify(response.data), 200

    except Exception as e:
        app.logger.error(f"GET request failed:{e}")
        return jsonify({"error": "Could not retrieve your tasks"}), 500
    

@app.route("/api/tasks", methods=["PUT"])
@jwt_required()
def update_task():
    try:
        data = request.get_json()
        title = None if not data.get('title') else data.get('title')
        description = None if not data.get('description') else data.get('description')
        due_date = None if not data.get('dueDate') else data.get('dueDate')
        task_id = data.get("taskId")

        task = {
            "title": title,
            "description": description,
            "due_date": due_date,
        }

    except Exception as e:
        app.logger.error(f"PUT request failed:{e}")
        return jsonify({"error":"Could not update task. Please try again"})

@app.route("/api/tasks", methods=["DELETE"])
@jwt_required()
def delete_task():
    try:
        pass
    except Exception as e:
        app.logger.error(f"DELETE request failed:{e}")
        return jsonify({"error":"Could not delete task. Please try again"})

if __name__ == '__main__':
    app.run(debug=True)
