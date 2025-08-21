# Database Service Package
# This package contains all database-related functionality

from .database import database, connect_db, disconnect_db, create_tables, get_database
from .models import User, Session, Contact, UserRecentContact, UserFavorite

__all__ = [
    'database',
    'connect_db', 
    'disconnect_db',
    'create_tables',
    'get_database',
    'User',
    'Session',
    'Contact',
    'UserRecentContact',
    'UserFavorite'
]