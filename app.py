from flask import Flask, render_template, redirect, url_for, request, session
from dotenv import load_dotenv
from supabase import Client, create_client
from functools import wraps
import os  

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

supabase: Client = create_client(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))    

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def redirect_if_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' in session:
            return redirect(url_for('profile'))
        return f(*args, **kwargs)
    return decorated_function 


@app.route("/", methods=['POST', 'GET'])
@redirect_if_logged_in
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            try:
                result = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                session['user'] = result.user.id
                return redirect(url_for('profile'))
            except Exception as e:
                app.logger.error(f"login failed: {e}")
                error = "An error occured. Please try again"
                return render_template('02-login.html', error=error)
    return render_template('02-login.html')


@app.route("/profile")
@login_required
def profile():
    return render_template('03-profile.html')

@app.route("/signup", methods=['POST', 'GET'])
@redirect_if_logged_in
def signup():
    if request.method == 'POST':
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirmed_password = request.form.get('confirm Password')
        if  first_name and last_name and email and password and confirmed_password:
            if confirmed_password != password:
                error ="Passwords do not match"
                return render_template('03-signup.html', error=error)
            else:
                try:
                    result = supabase.auth.sign_up({
                        "email": email,
                        "password": password
                    })
                    return redirect(url_for('login'))
                except Exception as e:
                    app.logger.error(f"login failed: {e}")
                    error = "An error occured. Please try again"
                    return render_template('03-signup.html', error=e)
    return render_template('03-signup.html')

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/api/tasks", methods=["POST"]) 
@login_required
def create_task():
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status')
    due_date = request.form.get('due-date')
    user_id = session.get('user')

    task = {
        "title": title,
        "description": description,
        "status": status,
        "due_date": due_date,
        "user_id": user_id,
    }

    response = supabase.table("tasks").insert(task).execute()
    if response.status_code == 201:
        return redirect(url_for('view_tasks'))
    else:
        return "Task creation failed", 400
    


    pass
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
