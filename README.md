# TaskFlow - Personal Task Manager

A full-featured task management web application built with Django. Create, organize, and track tasks with priorities, statuses, and due dates. Features automatic email reminders and a powerful admin interface.

## Tech Stack
- **Backend:** Django 5.x, Python 3.11+
- **Database:** SQLite (development), PostgreSQL (production)
- **Frontend:** Django Templates, Bootstrap 5
- **Authentication:** Django built-in auth
- **Deployment:** Render 


## Features
### Backend & Admin
- ✅ User authentication (login/register/logout)
- ✅ Create, read, update, and delete tasks
- ✅ Set task priority (High/Medium/Low)
- ✅ Track task status (Pending/In Progress/Done)
- ✅ Set due dates for tasks
- ✅ Search tasks by title/description
- ✅ Filter tasks by priority and status
- ✅ Automatic email reminders (coming in Week 2)
- ✅ REST API (coming in Week 4)
- ✅ CSV export (coming in Week 4)
- ✅ Custom Django admin interface
- ✅ Task model with priority, status, due dates
- ✅ Custom Django admin interface
- ✅ Search, filters, inline editing in admin

### User Interface
- ✅ User authentication (register/login/logout)
- ✅ Task list with search, filter, sort
- ✅ Create, edit, delete tasks
- ✅ Quick status update buttons
- ✅ Pagination (10 tasks per page)
- ✅ Bootstrap 5 responsive design
- ✅ Success/error messages


## Setup Instructions

### Prerequisites
- Python 3.11 or higher installed
- Git (optional, for cloning)

### Installation

1. **Clone the repository**:-
   
2. **Create virtual environment**:-
    python -m venv myenv
3. **Activate virtual environment**:-
    myenv\Scripts\activate
4. **Install dependencies**:-
    pip install -r requirements.txt
5. **Run migrations**:-
    python manage.py migrate
6. **Create superuser (admin account)**:-
    python manage.py createsuperuser
7. **Run development server**:-
    python manage.py runserver



## Author

**Deeksha Sharma**
- GitHub: [@dkss-4](https://github.com/dkss-4)
- LinkedIn: [dkssharma](https://www.linkedin.com/in/dkssharma/)
- Email: dkss.deeksha@gmail.com

## License
This project is for portfolio purposes.

## Email Reminders

TaskFlow automatically sends email reminders 24 hours before a task is due.

### How It Works

1. A Django management command (`send_reminders`) runs daily at 9 AM
2. It finds all incomplete tasks due tomorrow
3. Sends HTML email reminders to users
4. Logs all reminders in the database

## My Journey Building This

### Challenges  Overcame
1. **Email Configuration**: Gmail's app passwords took 2 days to figure out
2. **Pagination with Filters**: Keeping filter parameters across pages was tricky
3. **Multi-user Data Isolation**: Learned about `request.user` the hard way
4. **Template DoesNot Exist error**: Taught me file structure importance hard way
5. **NoReverseMatch**
6. ** **

### Features i am excited about most
- Quick status update buttons (inspired by Trello)
- Productivity insights with emojis (makes dashboard friendly)
- CSV export with filters (requested by my friend who tested this)

### Time Spent
- Week 1-2: Learning Django basics
- Week 3: Email integration (most challenging)
- Week 4-5: API and analytics
- Week 6: Deployment and security

## Reflection
This project taught me more than any course. I wrote 80% of the code myself, 
referencing docs when stuck. The analytics dashboard was my original design.