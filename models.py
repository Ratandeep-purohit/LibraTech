from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = 'admin'
    LIBRARIAN = 'librarian'
    STUDENT = 'student'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Student specific fields (nullable for others)
    student_id = db.Column(db.String(20), unique=True, nullable=True) # Legacy Roll/ID
    department = db.Column(db.String(50), nullable=True)
    
    # New Fields requested
    contact_number = db.Column(db.String(20), nullable=True)
    joining_date = db.Column(db.Date, default=datetime.utcnow)
    address = db.Column(db.Text, nullable=True)
    enrollment_number = db.Column(db.String(50), unique=True, nullable=True)
    semester = db.Column(db.String(20), nullable=True)
    program = db.Column(db.String(100), nullable=True)
    profile_picture = db.Column(db.String(255), default='default_user.jpg')
    
    # Relationships
    issues = db.relationship('Issue', backref='student', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True)
    # fees relationship added via backref in StudentFee

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    books = db.relationship('Book', backref='category', lazy=True)

class Author(db.Model):
    __tablename__ = 'authors'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    description = db.Column(db.Text)
    publication_year = db.Column(db.Integer)
    publisher = db.Column(db.String(100))
    rack_number = db.Column(db.String(20))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    cover_image = db.Column(db.String(255), default='default_book.jpg')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False) # Soft delete

    # Foreign Keys
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    issues = db.relationship('Issue', backref='book', lazy=True)

class Issue(db.Model):
    __tablename__ = 'issues'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='issued') # issued, returned, lost
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    fine = db.relationship('Fine', backref='issue', uselist=False, lazy=True)

class Fine(db.Model):
    __tablename__ = 'fines'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.DateTime, nullable=True)
    
    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), unique=True, nullable=False)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

# FEES MODULE MODELS

class FeeHeader(db.Model):
    __tablename__ = 'fee_headers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # Fee Type
    priority = db.Column(db.Integer, default=0)
    due_date = db.Column(db.Date, nullable=True)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    admission_type = db.Column(db.String(20), default='All') # All, New, Old
    applicable_for = db.Column(db.String(20), default='All') # All, Class, Course
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Boolean, default=True) # Active=True

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'priority': self.priority,
            'amount': self.amount,
            'admission_type': self.admission_type,
            'applicable_for': self.applicable_for,
            'status': self.status,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None
        }

class StudentFee(db.Model):
    __tablename__ = 'student_fees'
    
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Pending') # Pending, Paid, Partial
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fee_header_id = db.Column(db.Integer, db.ForeignKey('fee_headers.id'), nullable=False)
    
    fee_header = db.relationship('FeeHeader', backref='student_assignments', lazy=True)
    student = db.relationship('User', backref='fees', lazy=True)

class FeeCollection(db.Model):
    __tablename__ = 'fee_collections'
    
    id = db.Column(db.Integer, primary_key=True)
    voucher_no = db.Column(db.String(50), unique=True, nullable=False)
    collection_date = db.Column(db.DateTime, default=datetime.utcnow)
    academic_year = db.Column(db.String(20))
    payment_mode = db.Column(db.String(20)) # Cash, UPI, Cheque, etc.
    total_amount = db.Column(db.Float, nullable=False)
    late_fees = db.Column(db.Float, default=0.0)
    additional_charges = db.Column(db.Float, default=0.0)
    bank_name = db.Column(db.String(100))
    transaction_no = db.Column(db.String(100)) # Cheque No / Ref ID
    transaction_date = db.Column(db.Date)
    remarks = db.Column(db.Text)
    
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student = db.relationship('User', backref='collections', lazy=True)
    items = db.relationship('FeeCollectionItem', backref='collection', lazy=True, cascade="all, delete-orphan")

class FeeCollectionItem(db.Model):
    __tablename__ = 'fee_collection_items'
    
    id = db.Column(db.Integer, primary_key=True)
    amount_collected = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)
    
    collection_id = db.Column(db.Integer, db.ForeignKey('fee_collections.id'), nullable=False)
    student_fee_id = db.Column(db.Integer, db.ForeignKey('student_fees.id'), nullable=False)
    student_fee = db.relationship('StudentFee', backref='collection_entries', lazy=True)

class BookRequest(db.Model):
    __tablename__ = 'book_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending') # pending, approved, rejected
    
    # Relationships
    student = db.relationship('User', backref='book_requests_list', lazy=True)
    book_obj = db.relationship('Book', backref='book_requests_list', lazy=True)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True) # Receiver
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    receiver = db.relationship('User', backref='notifications_list', lazy=True)
