"""
Database Migration Script for Stash-Go
Handles schema updates for user data isolation
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_column_exists(db: Session, table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table"""
    try:
        query = f"PRAGMA table_info({table_name})"
        result = db.execute(text(query)).fetchall()
        return any(col[1] == column_name for col in result)
    except Exception as e:
        logger.error(f"Error checking column: {e}")
        return False


def migrate_user_isolation(db: Session):
    """
    Migrate database to add user_id to bills table and 
    ensure all sales/bills have valid user_id
    """
    logger.info("Starting migration: User Data Isolation...")
    
    try:
        # Check if bills table has user_id column
        if not check_column_exists(db, 'bills', 'user_id'):
            logger.info("Adding user_id column to bills table...")
            db.execute(text("ALTER TABLE bills ADD COLUMN user_id INTEGER"))
            db.commit()
        else:
            logger.info("user_id already exists in bills table")
        
        # Check if sales table has user_id column
        if not check_column_exists(db, 'sales', 'user_id'):
            logger.info("Adding user_id column to sales table...")
            db.execute(text("ALTER TABLE sales ADD COLUMN user_id INTEGER"))
            db.commit()
        else:
            logger.info("user_id already exists in sales table")
        
        # Assign default user_id (1 = admin) to existing records
        logger.info("Assigning default user_id to existing sales...")
        db.execute(text("""
            UPDATE sales 
            SET user_id = 1 
            WHERE user_id IS NULL
        """))
        db.commit()
        sales_updated = db.execute(text("SELECT COUNT(*) FROM sales WHERE user_id IS NOT NULL")).scalar()
        logger.info(f"Sales records updated: {sales_updated}")
        
        logger.info("Assigning default user_id to existing bills...")
        db.execute(text("""
            UPDATE bills 
            SET user_id = 1 
            WHERE user_id IS NULL
        """))
        db.commit()
        bills_updated = db.execute(text("SELECT COUNT(*) FROM bills WHERE user_id IS NOT NULL")).scalar()
        logger.info(f"Bills records updated: {bills_updated}")
        
        logger.info("✅ Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def create_tables():
    """Create all tables (idempotent)"""
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tables created successfully!")


def verify_data_isolation():
    """Verify that data isolation is working"""
    db = SessionLocal()
    try:
        logger.info("\n🔍 Verifying Data Isolation...")
        
        # Check sales with NULL user_id
        null_sales = db.execute(text("SELECT COUNT(*) FROM sales WHERE user_id IS NULL")).scalar()
        if null_sales > 0:
            logger.warning(f"⚠️  Found {null_sales} sales with NULL user_id")
        else:
            logger.info("✅ All sales have user_id assigned")
        
        # Check bills with NULL user_id
        null_bills = db.execute(text("SELECT COUNT(*) FROM bills WHERE user_id IS NULL")).scalar()
        if null_bills > 0:
            logger.warning(f"⚠️  Found {null_bills} bills with NULL user_id")
        else:
            logger.info("✅ All bills have user_id assigned")
        
        # Show summary
        total_sales = db.execute(text("SELECT COUNT(*) FROM sales")).scalar()
        total_bills = db.execute(text("SELECT COUNT(*) FROM bills")).scalar()
        
        logger.info(f"\n📊 Database Summary:")
        logger.info(f"   Total Sales: {total_sales}")
        logger.info(f"   Total Bills: {total_bills}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during verification: {e}")
        return False
    finally:
        db.close()


def rollback_migration():
    """Rollback migration (remove user_id columns)"""
    db = SessionLocal()
    try:
        logger.warning("⚠️  Rolling back migration...")
        
        db.execute(text("ALTER TABLE sales DROP COLUMN user_id"))
        db.execute(text("ALTER TABLE bills DROP COLUMN user_id"))
        db.commit()
        
        logger.info("✅ Rollback completed!")
        return True
        
    except Exception as e:
        logger.error(f"Error during rollback: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Run migrations"""
    import sys
    
    logger.info("""
    ╔══════════════════════════════════════╗
    ║    Stash-Go Database Migration        ║
    ║    User Data Isolation Setup          ║
    ╚══════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create":
            create_tables()
        elif sys.argv[1] == "migrate":
            migrate_user_isolation(SessionLocal())
        elif sys.argv[1] == "verify":
            verify_data_isolation()
        elif sys.argv[1] == "rollback":
            rollback_migration()
        else:
            print("Usage: python migrate.py [create|migrate|verify|rollback]")
    else:
        # Default: create tables then migrate
        create_tables()
        migrate_user_isolation(SessionLocal())
        verify_data_isolation()


if __name__ == "__main__":
    main()
