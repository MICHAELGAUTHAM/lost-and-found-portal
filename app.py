import os
import pg8000.native
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecret")

# In Vercel environment, static folders are read-only.
# We direct uploads to /tmp and serve them dynamically from there.
if os.environ.get("VERCEL"):
    app.config['UPLOAD_FOLDER'] = '/tmp'
else:
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", 5432))
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_NAME = os.environ.get("DB_NAME", "lost_and_found")
DB_SSL = os.environ.get("DB_SSL", "false").lower() in ("true", "1", "yes")

def get_db_connection():
    ssl_context = True if DB_SSL else None
    return pg8000.native.Connection(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        ssl_context=ssl_context
    )

@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    folder = '/tmp' if os.environ.get("VERCEL") else os.path.join(app.root_path, 'static/uploads')
    from flask import send_from_directory
    return send_from_directory(folder, filename)

@app.route('/')
def index():
    try:
        con = get_db_connection()
        # pg8000 native returns lists of lists
        lost_items_data = con.run("SELECT id, name, description, category, location, date_lost, status, image_filename, created_at FROM lost_items ORDER BY created_at DESC LIMIT 5")
        found_items_data = con.run("SELECT id, name, description, category, location, date_found, status, image_filename, created_at FROM found_items ORDER BY created_at DESC LIMIT 5")
        
        # We map columns manually for easier templating since pg8000 returns lists, not dicts
        lost_items = [{"id": r[0], "name": r[1], "description": r[2], "category": r[3], "location": r[4], "date_lost": r[5], "status": r[6], "image_filename": r[7], "created_at": r[8]} for r in lost_items_data]
        found_items = [{"id": r[0], "name": r[1], "description": r[2], "category": r[3], "location": r[4], "date_found": r[5], "status": r[6], "image_filename": r[7], "created_at": r[8]} for r in found_items_data]
        
        con.close()
    except Exception as e:
        print(e)
        lost_items, found_items = [], []
    return render_template('index.html', lost_items=lost_items, found_items=found_items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'student')
        
        con = get_db_connection()
        try:
            con.run("INSERT INTO users (username, email, password_hash, role) VALUES (:u, :e, :p, :r)", 
                    u=username, e=email, p=generate_password_hash(password), r=role)
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('Username or email already exists.', 'danger')
        finally:
            con.close()
    return render_template('auth.html', action='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        con = get_db_connection()
        try:
            user = con.run("SELECT id, username, email, password_hash, role FROM users WHERE username = :u", u=username)
            if user and check_password_hash(user[0][3], password):
                session['user_id'] = user[0][0]
                session['username'] = user[0][1]
                session['role'] = user[0][4]
                flash('Logged in successfully.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid credentials.', 'danger')
        except Exception as e:
            print(e)
        finally:
            con.close()
    return render_template('auth.html', action='login')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/add_item/<type>', methods=['GET', 'POST'])
def add_item(type):
    if 'user_id' not in session:
        flash('Please login to add an item.', 'warning')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category']
        location = request.form['location']
        date_param = request.form['date']
        
        file = request.files.get('image')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
        con = get_db_connection()
        try:
            if type == 'lost':
                con.run("""INSERT INTO lost_items (user_id, name, description, category, location, date_lost, image_filename) 
                           VALUES (:uid, :n, :d, :c, :l, :dt, :img)""",
                        uid=session['user_id'], n=name, d=description, c=category, l=location, dt=date_param, img=filename)
            else:
                con.run("""INSERT INTO found_items (user_id, name, description, category, location, date_found, image_filename) 
                           VALUES (:uid, :n, :d, :c, :l, :dt, :img)""",
                        uid=session['user_id'], n=name, d=description, c=category, l=location, dt=date_param, img=filename)
            flash(f'{type.capitalize()} item added successfully.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            flash('Error adding item.', 'danger')
        finally:
            con.close()
            
    return render_template('add_item.html', type=type)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    con = get_db_connection()
    try:
        q_wild = f"%{query}%"
        lost_data = con.run("SELECT id, name, description, category, location, date_lost, status, image_filename, created_at FROM lost_items WHERE name ILIKE :q OR location ILIKE :q OR description ILIKE :q", q=q_wild)
        found_data = con.run("SELECT id, name, description, category, location, date_found, status, image_filename, created_at FROM found_items WHERE name ILIKE :q OR location ILIKE :q OR description ILIKE :q", q=q_wild)
        
        lost = [{"id": r[0], "name": r[1], "description": r[2], "category": r[3], "location": r[4], "date_lost": r[5], "status": r[6], "image_filename": r[7], "created_at": r[8]} for r in lost_data]
        found = [{"id": r[0], "name": r[1], "description": r[2], "category": r[3], "location": r[4], "date_found": r[5], "status": r[6], "image_filename": r[7], "created_at": r[8]} for r in found_data]
        
    except Exception as e:
        print(e)
        lost, found = [], []
    finally:
        con.close()
        
    return render_template('search.html', lost=lost, found=found, query=query)

@app.route('/claim/<int:found_item_id>', methods=['GET', 'POST'])
def claim(found_item_id):
    if 'user_id' not in session:
        flash('Please login to claim an item.', 'warning')
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        proof = request.form['proof_description']
        con = get_db_connection()
        try:
            con.run("INSERT INTO claims (user_id, found_item_id, proof_description) VALUES (:uid, :fid, :p)",
                    uid=session['user_id'], fid=found_item_id, p=proof)
            flash('Claim submitted for approval.', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
            flash('Error submitting claim.', 'danger')
        finally:
            con.close()
            
    return render_template('claim.html', found_item_id=found_item_id)

@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('index'))
        
    con = get_db_connection()
    try:
        claims_data = con.run("""
            SELECT c.id, u.username, f.name, c.proof_description, c.status, c.created_at, f.id
            FROM claims c
            JOIN users u ON c.user_id = u.id
            JOIN found_items f ON c.found_item_id = f.id
            ORDER BY c.created_at DESC
        """)
        claims = [{"id": r[0], "username": r[1], "item_name": r[2], "proof": r[3], "status": r[4], "date": r[5], "found_item_id": r[6]} for r in claims_data]
    except Exception as e:
        print(e)
        claims = []
    finally:
        con.close()
        
    return render_template('admin.html', claims=claims)

@app.route('/admin/claim/<int:claim_id>/<action>')
def resolve_claim(claim_id, action):
    if session.get('role') != 'admin':
        return redirect(url_for('index'))
        
    status = 'approved' if action == 'approve' else 'rejected'
    con = get_db_connection()
    try:
        con.run("UPDATE claims SET status = :s WHERE id = :cid", s=status, cid=claim_id)
        if status == 'approved':
            # Also update the found item status
            claim_rec = con.run("SELECT found_item_id FROM claims WHERE id = :cid", cid=claim_id)
            if claim_rec:
                con.run("UPDATE found_items SET status = 'claimed' WHERE id = :fid", fid=claim_rec[0][0])
        flash(f'Claim {status}.', 'success')
    except Exception as e:
        print(e)
        flash('Error updating claim.', 'danger')
    finally:
        con.close()
        
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
