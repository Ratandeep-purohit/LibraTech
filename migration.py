from app import app, db
from models import User, UserRole, Category, Author, Book, Issue, Fine, AuditLog
from werkzeug.security import generate_password_hash
import sys

def init_db():
    """
    Initializes the database:
    1. Drops all tables (optional, for fresh start)
    2. Creates all tables
    3. Seeds initial admin data if not exists
    """
    with app.app_context():
        # Check database connection first
        try:
            # Create Database if it doesn't exist
            # Note: SQLAlchemy Engine is bound to the DB in config. 
            # If DB doesn't exist, connection might fail.
            # We will try to create the tables. If it fails due to unknown database, we hint.
            # Ideally, one should create the DB schema manually in Workbench as per standard practice,
            # but we can try to be "Smart" and creating it via a raw connection if possible,
            # but that complicates the dependency on app.context.
            
            # Let's rely on standard create_all.
            print("Creating database tables...")
            db.create_all()
            print("Tables created successfully.")
            
            # Seed Admin
            if not User.query.filter_by(role=UserRole.ADMIN).first():
                print("Seeding initial admin user...")
                admin = User(
                    username='admin',
                    email='admin@library.com',
                    full_name='System Administrator',
                    role=UserRole.ADMIN
                )
                admin.set_password('admin123') # Default password
                db.session.add(admin)
                
                # Sudo Librarian
                librarian = User(
                    username='librarian',
                    email='librarian@library.com',
                    full_name='Head Librarian',
                    role=UserRole.LIBRARIAN
                )
                librarian.set_password('lib123')
                db.session.add(librarian)
                
                # Sample Categories
                cats = ['Fiction', 'Science', 'Technology', 'History', 'Philosophy']
                for c_name in cats:
                    db.session.add(Category(name=c_name, description=f'Books related to {c_name}'))
                
                db.session.commit()
                print("Seeding complete. Admin: admin/admin123")
            else:
                print("Admin already exists. Skipping seed.")
                
        except Exception as e:
            print(f"Error during migration: {e}")
            sys.exit(1)

if __name__ == '__main__':
    print("Starting database migration...")
    init_db()
    print("Migration finished.")
