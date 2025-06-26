# StudentPlanner 📚

A comprehensive web-based task and project management application designed for students. Built with Flask, SQLAlchemy, and Bootstrap, StudentPlanner helps students organize personal tasks and collaborate on group projects using an intuitive Kanban board interface.

## ✨ Features

### 🔐 User Management
- **Secure Authentication** - Password hashing with Werkzeug security
- **User Registration** - Create accounts with email validation
- **Role-based Access** - Admin and regular user roles
- **Session Management** - Secure login/logout functionality

### 📋 Personal Task Management
- **CRUD Operations** - Create, read, update, and delete personal tasks
- **Task Details** - Title, description, due dates, and completion status
- **Visual Status Tracking** - Clear indicators for pending/completed tasks
- **Quick Actions** - Mark tasks complete/incomplete with one click

### 🏗️ Project Collaboration
- **Project Creation** - Create and manage collaborative projects
- **Kanban Board** - Visual task management with drag-and-drop workflow
- **Task Assignment** - Assign tasks to specific team members
- **Priority Levels** - High, Medium, and Low priority indicators
- **Category Management** - To Do, In Progress, and Done columns
- **Project Access Control** - Only project creators and assigned members can access

### 📊 Dashboard & Analytics
- **Unified Task View** - See both personal and project tasks in one place
- **Admin Dashboard** - Comprehensive user and task management for admins
- **Quick Statistics** - Task counts and completion metrics
- **Project Links** - Direct navigation to project Kanban boards

### 🎨 User Interface
- **Responsive Design** - Works seamlessly on desktop and mobile
- **Bootstrap Styling** - Modern, clean, and professional appearance
- **Intuitive Navigation** - Easy-to-use interface with clear visual hierarchy
- **Flash Messages** - Real-time feedback for user actions

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AlfaCollegeTeamICT/StudentPlanner.git
   cd StudentPlanner
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Open your browser and go to `http://127.0.0.1:5000`
   - The application will automatically create sample data on first run

### Default Accounts
The application creates two default accounts for testing:
- **Admin**: Username: `admin`, Password: `adminpass`
- **Student**: Username: `student`, Password: `studentpass`

## 🗃️ Database Schema

### User Table
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password` - Hashed password
- `role` - User role (admin/user)
- `created_at` - Account creation timestamp

### Task Table (Personal Tasks)
- `id` - Primary key
- `title` - Task title
- `description` - Task description
- `due_date` - Optional due date
- `completed` - Completion status
- `user_id` - Foreign key to User

### Project Table
- `id` - Primary key
- `title` - Project title
- `description` - Project description
- `creator_id` - Foreign key to User (project creator)
- `created_at` - Project creation timestamp

### ProjectTask Table
- `id` - Primary key
- `title` - Task title
- `description` - Task description
- `category` - Task status (To Do/In Progress/Done)
- `priority` - Task priority (Low/Medium/High)
- `due_date` - Optional due date
- `project_id` - Foreign key to Project
- `assigned_user_id` - Foreign key to User (assignee)

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Security**: Werkzeug password hashing
- **Session Management**: Flask sessions

## 📱 Usage Guide

### Getting Started
1. **Register** a new account or use the default credentials
2. **Login** to access your dashboard
3. **Create personal tasks** from the "My Planner" section
4. **Create projects** and invite collaborators
5. **Manage tasks** using the Kanban board interface

### Personal Task Management
- Navigate to "My Planner" to see all your tasks
- Click "Add New Personal Task" to create tasks
- Use the action buttons to edit, complete, or delete tasks
- View both personal and assigned project tasks in one place

### Project Collaboration
- Go to "Projects" to see all your projects
- Click "Create New Project" to start a collaborative project
- Use the Kanban board to manage project tasks
- Assign tasks to team members and set priorities
- Move tasks between columns as work progresses

### Admin Features
- Access the admin dashboard to manage all users
- View all tasks across the system
- Monitor user activity and task completion

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production settings:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///production.db
DEBUG=False
```

### Database Configuration
The application uses SQLite by default. To use a different database:
1. Update the `SQLALCHEMY_DATABASE_URI` in `main.py`
2. Install the appropriate database driver
3. Update the connection string

## 🧪 Development

### Project Structure
```
StudentPlanner/
├── main.py                 # Main application file
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── student_planner.db     # SQLite database (created automatically)
└── templates/             # HTML templates
    ├── base.html          # Base template
    ├── index.html         # Home page
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── planner.html       # Personal task manager
    ├── projects.html      # Project listing
    ├── project_board.html # Kanban board
    ├── dashboard.html     # Admin dashboard
    └── ...               # Task management templates
```

### Adding New Features
1. **Models**: Add new database models in `main.py`
2. **Routes**: Create new Flask routes for functionality
3. **Templates**: Design HTML templates in the `templates/` folder
4. **Styling**: Use Bootstrap classes for consistent styling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you have any questions or run into issues:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Include steps to reproduce any bugs

## 🚧 Roadmap

- [ ] Email notifications for task assignments
- [ ] File attachments for tasks
- [ ] Calendar integration
- [ ] Mobile app
- [ ] Real-time collaboration features
- [ ] Advanced reporting and analytics
- [ ] Dark mode theme
- [ ] API endpoints for third-party integrations

---

