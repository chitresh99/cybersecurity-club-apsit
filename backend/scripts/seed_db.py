"""Database seeding script to create initial admin user and sample data."""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, Event, Resource, EventType, ResourceLevel
from app.security import hash_password
from datetime import date, timedelta

# Create tables
Base.metadata.create_all(bind=engine)


def seed_database():
    """Seed the database with initial data."""
    db: Session = SessionLocal()
    
    try:
        # Create admin user
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == admin_username).first()
        if not existing_admin:
            admin = User(
                username=admin_username,
                password_hash=hash_password(admin_password),
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"✓ Created admin user: {admin_username}")
        else:
            print(f"✓ Admin user already exists: {admin_username}")
        
        # Create sample events
        sample_events = [
            {
                "title": "Web Security Workshop",
                "type": EventType.WORKSHOP,
                "date": date.today() + timedelta(days=30),
                "description": "Introduction to OWASP Top 10 vulnerabilities and secure coding practices."
            },
            {
                "title": "Malware Analysis Bootcamp",
                "type": EventType.BOOTCAMP,
                "date": date.today() + timedelta(days=45),
                "description": "Hands-on training on analyzing malicious binaries safely in a controlled environment."
            },
            {
                "title": "Introduction to Cryptography",
                "type": EventType.LECTURE,
                "date": date.today() - timedelta(days=10),
                "description": "Understanding Public Key Infrastructure (PKI) and encryption fundamentals.",
                "is_active": False  # Past event
            },
            {
                "title": "CyberDefense CTF 2026",
                "type": EventType.HACKATHON,
                "date": date.today() + timedelta(days=60),
                "description": "Join 50+ teams in a 48-hour endurance test of your hacking skills. Challenges include Web Exploitation, Cryptography, Reverse Engineering, and Forensics."
            }
        ]
        
        for event_data in sample_events:
            existing_event = db.query(Event).filter(Event.title == event_data["title"]).first()
            if not existing_event:
                event = Event(**event_data)
                db.add(event)
                print(f"✓ Created event: {event_data['title']}")
            else:
                print(f"✓ Event already exists: {event_data['title']}")
        
        db.commit()
        
        # Create sample resources (note: these won't have actual PDF files, just database records)
        sample_resources = [
            {
                "title": "Linux Command Cheatsheet",
                "level": ResourceLevel.BEGINNER,
                "file_url": "uploads/sample_linux_cheatsheet.pdf",
                "file_size": 102400  # 100KB placeholder
            },
            {
                "title": "Network Security Fundamentals",
                "level": ResourceLevel.BEGINNER,
                "file_url": "uploads/sample_network_security.pdf",
                "file_size": 204800  # 200KB placeholder
            },
            {
                "title": "Advanced Buffer Overflow Exploitation",
                "level": ResourceLevel.ADVANCED,
                "file_url": "uploads/sample_buffer_overflow.pdf",
                "file_size": 512000  # 500KB placeholder
            }
        ]
        
        for resource_data in sample_resources:
            existing_resource = db.query(Resource).filter(Resource.title == resource_data["title"]).first()
            if not existing_resource:
                resource = Resource(**resource_data)
                db.add(resource)
                print(f"✓ Created resource: {resource_data['title']}")
            else:
                print(f"✓ Resource already exists: {resource_data['title']}")
        
        db.commit()
        
        print("\n✓ Database seeding completed successfully!")
        print(f"\nAdmin credentials:")
        print(f"  Username: {admin_username}")
        print(f"  Password: {admin_password}")
        print(f"\n⚠️  IMPORTANT: Change the admin password after first login!")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
