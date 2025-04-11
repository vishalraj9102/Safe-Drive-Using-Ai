from app import create_app
import os

app = create_app()

# Create all tables
with app.app_context():
    from app.models.user import User  
    from app import db
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
