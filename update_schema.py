from app import app, db
from sqlalchemy import text

def add_columns():
    with app.app_context():
        # List of columns to add and their types (SQLite/MySQL compatible broadly)
        # Note: syntax might vary slightly depending on DB. Assuming SQLite based on lack of complex config seen so far, 
        # but if it uses MySQL (from previous inference of 'library' potentially using XAMPP/local), 
        # I should use standard SQL.
        
        # Check if we are using MySQL or SQLite
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Database: {db_uri}")
        
        queries = [
            "ALTER TABLE users ADD COLUMN contact_number VARCHAR(20)",
            "ALTER TABLE users ADD COLUMN joining_date DATE",
            "ALTER TABLE users ADD COLUMN address TEXT",
            "ALTER TABLE users ADD COLUMN enrollment_number VARCHAR(50)",
            "ALTER TABLE users ADD COLUMN semester VARCHAR(20)",
            "ALTER TABLE users ADD COLUMN program VARCHAR(100)"
        ]
        
        for q in queries:
            try:
                print(f"Executing: {q}")
                db.session.execute(text(q))
                db.session.commit()
                print("Success.")
            except Exception as e:
                # Column might already exist
                print(f"Skipped (likely exists): {e}")
                db.session.rollback()

if __name__ == "__main__":
    add_columns()
