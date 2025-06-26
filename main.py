from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "student_planner.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship with tasks
    tasks = db.relationship('Task', backref='user', lazy=True, cascade='all, delete-orphan')
    # Relationship with projects (as creator)
    created_projects = db.relationship('Project', backref='creator', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign key to user (project creator)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationship with project tasks
    project_tasks = db.relationship('ProjectTask', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.title}>'

class ProjectTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False, default='To Do')  # To Do, In Progress, Done
    priority = db.Column(db.String(20), nullable=False, default='Medium')  # Low, Medium, High
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign keys
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Relationship with assigned user
    assigned_user = db.relationship('User', backref='assigned_project_tasks')
    
    def __repr__(self):
        return f'<ProjectTask {self.title}>'

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Foreign key to user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Task {self.title}>'

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role:
                user = User.query.get(session['user_id'])
                if not user or user.role != role:
                    flash('Unauthorized access.')
                    return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            if user.role == 'admin':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('planner'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match')
        elif User.query.filter_by(username=username).first():
            flash('Username already exists')
        elif User.query.filter_by(email=email).first():
            flash('Email already exists')
        else:
            # Hash the password before storing
            hashed_password = generate_password_hash(password)
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                role='user'
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. Please log in.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required(role='admin')
def dashboard():
    users = User.query.all()
    return render_template('dashboard.html', users=users)

@app.route('/planner')
@login_required(role='user')
def planner():
    user = User.query.get(session['user_id'])
    # Get user's personal tasks
    personal_tasks = user.tasks if user else []
    
    # Get user's assigned project tasks
    project_tasks = ProjectTask.query.filter_by(assigned_user_id=user.id).all()
    
    return render_template('planner.html', 
                         personal_tasks=personal_tasks, 
                         project_tasks=project_tasks)

@app.route('/add_task', methods=['GET', 'POST'])
@login_required(role='user')
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        due_date_str = request.form.get('due_date')
        
        # Parse due date if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format')
                return redirect(url_for('add_task'))
        
        if title:
            new_task = Task(
                title=title,
                description=description,
                due_date=due_date,
                user_id=session['user_id']
            )
            db.session.add(new_task)
            db.session.commit()
            flash('Task added successfully!')
            return redirect(url_for('planner'))
        else:
            flash('Task title is required')
    
    return render_template('add_task.html')

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required(role='user')
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Check if the task belongs to the current user
    if task.user_id != session['user_id']:
        flash('Unauthorized access to task')
        return redirect(url_for('planner'))
    
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description', '')
        due_date_str = request.form.get('due_date')
        
        # Parse due date if provided
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format')
                return redirect(url_for('edit_task', task_id=task_id))
        else:
            task.due_date = None
        
        if task.title:
            db.session.commit()
            flash('Task updated successfully!')
            return redirect(url_for('planner'))
        else:
            flash('Task title is required')
    
    return render_template('edit_task.html', task=task)

@app.route('/toggle_task/<int:task_id>', methods=['POST'])
@login_required(role='user')
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Check if the task belongs to the current user
    if task.user_id != session['user_id']:
        flash('Unauthorized access to task')
        return redirect(url_for('planner'))
    
    task.completed = not task.completed
    db.session.commit()
    
    status = 'completed' if task.completed else 'pending'
    flash(f'Task marked as {status}!')
    return redirect(url_for('planner'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required(role='user')
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Check if the task belongs to the current user
    if task.user_id != session['user_id']:
        flash('Unauthorized access to task')
        return redirect(url_for('planner'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!')
    return redirect(url_for('planner'))

# Project routes
@app.route('/projects')
@login_required()
def projects():
    user = User.query.get(session['user_id'])
    # Get projects created by user and projects where user has assigned tasks
    created_projects = user.created_projects
    assigned_projects = db.session.query(Project).join(ProjectTask).filter(
        ProjectTask.assigned_user_id == user.id
    ).distinct().all()
    
    # Combine and remove duplicates
    all_projects = list(set(created_projects + assigned_projects))
    
    return render_template('projects.html', projects=all_projects, user=user)

@app.route('/create_project', methods=['GET', 'POST'])
@login_required()
def create_project():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        
        if title:
            new_project = Project(
                title=title,
                description=description,
                creator_id=session['user_id']
            )
            db.session.add(new_project)
            db.session.commit()
            flash('Project created successfully!')
            return redirect(url_for('project_board', project_id=new_project.id))
        else:
            flash('Project title is required')
    
    return render_template('create_project.html')

@app.route('/project/<int:project_id>')
@login_required()
def project_board(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    user = User.query.get(session['user_id'])
    has_access = (project.creator_id == user.id or 
                 any(task.assigned_user_id == user.id for task in project.project_tasks))
    
    if not has_access:
        flash('You do not have access to this project')
        return redirect(url_for('projects'))
    
    # Organize tasks by category for Kanban board
    tasks_by_category = {
        'To Do': [],
        'In Progress': [],
        'Done': []
    }
    
    for task in project.project_tasks:
        tasks_by_category[task.category].append(task)
    
    # Get all users for task assignment
    all_users = User.query.all()
    
    return render_template('project_board.html', 
                         project=project, 
                         tasks_by_category=tasks_by_category,
                         all_users=all_users,
                         current_user=user)

@app.route('/project/<int:project_id>/add_task', methods=['GET', 'POST'])
@login_required()
def add_project_task(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access to this project
    user = User.query.get(session['user_id'])
    has_access = (project.creator_id == user.id or 
                 any(task.assigned_user_id == user.id for task in project.project_tasks))
    
    if not has_access:
        flash('You do not have access to this project')
        return redirect(url_for('projects'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description', '')
        category = request.form.get('category', 'To Do')
        priority = request.form.get('priority', 'Medium')
        assigned_user_id = request.form.get('assigned_user_id')
        due_date_str = request.form.get('due_date')
        
        # Parse due date if provided
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format')
                return redirect(url_for('add_project_task', project_id=project_id))
        
        if title:
            new_task = ProjectTask(
                title=title,
                description=description,
                category=category,
                priority=priority,
                due_date=due_date,
                project_id=project_id,
                assigned_user_id=assigned_user_id if assigned_user_id else None
            )
            db.session.add(new_task)
            db.session.commit()
            flash('Task added to project successfully!')
            return redirect(url_for('project_board', project_id=project_id))
        else:
            flash('Task title is required')
    
    all_users = User.query.all()
    return render_template('add_project_task.html', project=project, all_users=all_users)

@app.route('/project_task/<int:task_id>/move', methods=['POST'])
@login_required()
def move_project_task(task_id):
    task = ProjectTask.query.get_or_404(task_id)
    project = task.project
    
    # Check if user has access to this project
    user = User.query.get(session['user_id'])
    has_access = (project.creator_id == user.id or 
                 any(t.assigned_user_id == user.id for t in project.project_tasks))
    
    if not has_access:
        flash('You do not have access to this project')
        return redirect(url_for('projects'))
    
    new_category = request.form.get('category')
    if new_category in ['To Do', 'In Progress', 'Done']:
        task.category = new_category
        db.session.commit()
        flash(f'Task moved to {new_category}!')
    
    return redirect(url_for('project_board', project_id=project.id))

@app.route('/project_task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required()
def edit_project_task(task_id):
    task = ProjectTask.query.get_or_404(task_id)
    project = task.project
    
    # Check if user has access to this project
    user = User.query.get(session['user_id'])
    has_access = (project.creator_id == user.id or 
                 any(t.assigned_user_id == user.id for t in project.project_tasks))
    
    if not has_access:
        flash('You do not have access to this project')
        return redirect(url_for('projects'))
    
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description', '')
        task.category = request.form.get('category', 'To Do')
        task.priority = request.form.get('priority', 'Medium')
        assigned_user_id = request.form.get('assigned_user_id')
        task.assigned_user_id = assigned_user_id if assigned_user_id else None
        
        due_date_str = request.form.get('due_date')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format')
                return redirect(url_for('edit_project_task', task_id=task_id))
        else:
            task.due_date = None
        
        if task.title:
            db.session.commit()
            flash('Project task updated successfully!')
            return redirect(url_for('project_board', project_id=project.id))
        else:
            flash('Task title is required')
    
    all_users = User.query.all()
    return render_template('edit_project_task.html', task=task, project=project, all_users=all_users)

@app.route('/project_task/<int:task_id>/delete', methods=['POST'])
@login_required()
def delete_project_task(task_id):
    task = ProjectTask.query.get_or_404(task_id)
    project = task.project
    
    # Check if user has access to this project
    user = User.query.get(session['user_id'])
    has_access = (project.creator_id == user.id or 
                 any(t.assigned_user_id == user.id for t in project.project_tasks))
    
    if not has_access:
        flash('You do not have access to this project')
        return redirect(url_for('projects'))
    
    project_id = project.id
    db.session.delete(task)
    db.session.commit()
    flash('Project task deleted successfully!')
    return redirect(url_for('project_board', project_id=project_id))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

def migrate_passwords():
    """Migrate existing plain text passwords to hashed passwords"""
    users_to_update = []
    
    # Check if there are users with plain text passwords
    all_users = User.query.all()
    for user in all_users:
        # Check if password is not hashed (hashed passwords start with specific prefixes)
        if not (user.password.startswith('pbkdf2:') or user.password.startswith('scrypt:') or user.password.startswith('argon2:')):
            # This is likely a plain text password, hash it
            if user.username == 'admin' and user.password == 'adminpass':
                user.password = generate_password_hash('adminpass')
                users_to_update.append(user)
            elif user.username == 'student' and user.password == 'studentpass':
                user.password = generate_password_hash('studentpass')
                users_to_update.append(user)
            else:
                # For other users, hash their existing password
                user.password = generate_password_hash(user.password)
                users_to_update.append(user)
    
    if users_to_update:
        db.session.commit()
        print(f"Migrated {len(users_to_update)} users to hashed passwords!")

if __name__ == '__main__':
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Migrate existing passwords to hashed format
        migrate_passwords()
        
        # Create sample data if database is empty
        if User.query.count() == 0:
            # Create admin user with hashed password
            admin = User(
                username='admin',
                email='admin@example.com',
                password=generate_password_hash('adminpass'),
                role='admin'
            )
            
            # Create regular user with hashed password
            student = User(
                username='student',
                email='student@example.com',
                password=generate_password_hash('studentpass'),
                role='user'
            )
            
            db.session.add(admin)
            db.session.add(student)
            db.session.commit()
            
            # Create sample tasks for the student
            task1 = Task(
                title='Complete Math Assignment',
                description='Finish chapter 5 exercises',
                due_date=datetime(2025, 7, 1),
                user_id=student.id
            )
            
            task2 = Task(
                title='Study for History Exam',
                description='Review World War II chapter',
                due_date=datetime(2025, 6, 30),
                completed=True,
                user_id=student.id
            )
            
            db.session.add(task1)
            db.session.add(task2)
            
            # Create sample project
            sample_project = Project(
                title='Sample Project',
                description='A sample project to demonstrate the Kanban board functionality',
                creator_id=student.id
            )
            
            db.session.add(sample_project)
            db.session.commit()
            
            # Create sample project tasks
            project_task1 = ProjectTask(
                title='Design Database Schema',
                description='Create the database schema for the application',
                category='Done',
                priority='High',
                project_id=sample_project.id,
                assigned_user_id=student.id
            )
            
            project_task2 = ProjectTask(
                title='Implement User Authentication',
                description='Set up login and registration functionality',
                category='In Progress',
                priority='High',
                due_date=datetime(2025, 7, 5),
                project_id=sample_project.id,
                assigned_user_id=student.id
            )
            
            project_task3 = ProjectTask(
                title='Create UI Components',
                description='Design and implement the user interface',
                category='To Do',
                priority='Medium',
                due_date=datetime(2025, 7, 10),
                project_id=sample_project.id,
                assigned_user_id=admin.id
            )
            
            project_task4 = ProjectTask(
                title='Write Documentation',
                description='Document the API and user guide',
                category='To Do',
                priority='Low',
                project_id=sample_project.id
            )
            
            db.session.add(project_task1)
            db.session.add(project_task2)
            db.session.add(project_task3)
            db.session.add(project_task4)
            db.session.commit()
            
            print("Database initialized with sample data!")
        
        migrate_passwords()  # Run the password migration function
    
    app.run(debug=True)