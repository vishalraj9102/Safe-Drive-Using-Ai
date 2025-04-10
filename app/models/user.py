from app import db

class User(db.Model):
    __tablename__ = 'users'  # good practice to name the table

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)  # better size for hashed password

    def __repr__(self):
        return f"<Users {self.username}>"
