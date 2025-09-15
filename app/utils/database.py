import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class PRDDatabase:
    def __init__(self, db_path: str = "prd_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                product_name TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create versions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                version_number INTEGER NOT NULL,
                content TEXT NOT NULL,
                section_name TEXT,
                change_description TEXT,
                user_prompt TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        # Add user_prompt column if it doesn't exist (migration)
        cursor.execute("PRAGMA table_info(versions)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_prompt' not in columns:
            cursor.execute('ALTER TABLE versions ADD COLUMN user_prompt TEXT')
            print("✅ Database migrated: Added user_prompt column to versions table")
        
        # Create chat_messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                message_type TEXT NOT NULL, -- 'user' or 'assistant'
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self, session_id: str, product_name: str) -> bool:
        """Create a new session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (session_id, product_name) VALUES (?, ?)",
                (session_id, product_name)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def save_version(self, session_id: str, content: str, section_name: str = None, 
                    change_description: str = None, user_prompt: str = None) -> int:
        """Save a new version of the PRD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current version number
        cursor.execute(
            "SELECT MAX(version_number) FROM versions WHERE session_id = ?",
            (session_id,)
        )
        result = cursor.fetchone()
        version_number = (result[0] or 0) + 1
        
        # Insert new version
        cursor.execute('''
            INSERT INTO versions (session_id, version_number, content, section_name, change_description, user_prompt)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, version_number, content, section_name, change_description, user_prompt))
        
        # Update session timestamp
        cursor.execute(
            "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
            (session_id,)
        )
        
        conn.commit()
        conn.close()
        return version_number
    
    def get_versions(self, session_id: str) -> List[Dict]:
        """Get all versions for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version_number, content, section_name, change_description, user_prompt, created_at
            FROM versions 
            WHERE session_id = ? 
            ORDER BY version_number DESC
        ''', (session_id,))
        
        versions = []
        for row in cursor.fetchall():
            versions.append({
                'version_number': row[0],
                'content': row[1],
                'section_name': row[2],
                'change_description': row[3],
                'user_prompt': row[4],
                'created_at': row[5]
            })
        
        conn.close()
        return versions
    
    def get_latest_version(self, session_id: str) -> Optional[Dict]:
        """Get the latest version of PRD for a session"""
        versions = self.get_versions(session_id)
        return versions[0] if versions else None
    
    def save_chat_message(self, session_id: str, message_type: str, content: str):
        """Save a chat message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chat_messages (session_id, message_type, content)
            VALUES (?, ?, ?)
        ''', (session_id, message_type, content))
        
        conn.commit()
        conn.close()
    
    def get_chat_history(self, session_id: str) -> List[Dict]:
        """Get chat history for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT message_type, content, created_at
            FROM chat_messages 
            WHERE session_id = ? 
            ORDER BY created_at ASC
        ''', (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'role': row[0],  # Use 'role' instead of 'type' for consistency
                'content': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        return messages
    
    def get_chat_history_until_version(self, session_id: str, version_number: int, context_limit: int = 5) -> Dict:
        """Get chat history up to a specific version with the version message highlighted"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the version data
        cursor.execute('''
            SELECT created_at, user_prompt 
            FROM versions 
            WHERE session_id = ? AND version_number = ?
        ''', (session_id, version_number))
        
        version_result = cursor.fetchone()
        if not version_result:
            conn.close()
            return {'context_messages': [], 'version_message': None, 'assistant_response': None}
        
        version_timestamp = version_result[0]
        version_user_prompt = version_result[1]
        
        # If it's version 1, there's no chat history before it
        if version_number == 1:
            # For version 1, the version message is the initial request
            version_message = None
            if version_user_prompt:
                version_message = {
                    'role': 'user',
                    'content': version_user_prompt,
                    'timestamp': version_timestamp
                }
            
            # Get the first assistant response after version 1 creation
            assistant_response = self._get_assistant_response_for_version(session_id, version_timestamp)
            
            conn.close()
            return {
                'context_messages': [],
                'version_message': version_message,
                'assistant_response': assistant_response
            }
        
        # For versions > 1, get messages up to this version's timestamp
        cursor.execute('''
            SELECT message_type, content, created_at
            FROM chat_messages 
            WHERE session_id = ? AND created_at < ?
            ORDER BY created_at ASC
        ''', (session_id, version_timestamp))
        
        all_messages = []
        for row in cursor.fetchall():
            all_messages.append({
                'role': row[0],
                'content': row[1],
                'timestamp': row[2]
            })
        
        # Now get the version message (the one that triggered this version)
        version_message = None
        if version_user_prompt:
            version_message = {
                'role': 'user',
                'content': version_user_prompt,
                'timestamp': version_timestamp
            }
        
        # Get assistant response for this version
        assistant_response = self._get_assistant_response_for_version(session_id, version_timestamp)
        
        # Get only the last context_limit messages as context
        context_messages = all_messages[-context_limit:] if len(all_messages) > context_limit else all_messages
        
        conn.close()
        
        return {
            'context_messages': context_messages,
            'version_message': version_message,
            'assistant_response': assistant_response
        }
    
    def _get_assistant_response_for_version(self, session_id: str, version_timestamp: str) -> Dict:
        """Get the assistant response that was created after a specific version"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the next assistant message that was created at or after the version timestamp
        # Use >= instead of > to catch messages created at the same timestamp
        cursor.execute('''
            SELECT content, created_at
            FROM chat_messages 
            WHERE session_id = ? AND message_type = 'assistant' AND created_at >= ?
            ORDER BY created_at ASC
            LIMIT 1
        ''', (session_id, version_timestamp))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'role': 'assistant',
                'content': result[0],
                'timestamp': result[1]
            }
        
        return None
    
    def get_all_sessions(self) -> List[Dict]:
        """Get all sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.session_id, s.product_name, s.created_at, s.updated_at,
                   COUNT(v.id) as version_count
            FROM sessions s
            LEFT JOIN versions v ON s.session_id = v.session_id
            GROUP BY s.session_id, s.product_name, s.created_at, s.updated_at
            ORDER BY s.updated_at DESC
        ''')
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                'session_id': row[0],
                'product_name': row[1],
                'created_at': row[2],
                'updated_at': row[3],
                'version_count': row[4]
            })
        
        conn.close()
        return sessions
    
    def get_version_by_number(self, session_id: str, version_number: int) -> Optional[Dict]:
        """Get specific version by number"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version_number, content, section_name, change_description, user_prompt, created_at
            FROM versions 
            WHERE session_id = ? AND version_number = ?
        ''', (session_id, version_number))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'version_number': result[0],
                'content': result[1],
                'section_name': result[2],
                'change_description': result[3],
                'user_prompt': result[4],
                'created_at': result[5]
            }
        return None
    
    def get_max_version_number(self, session_id: str) -> int:
        """Get the highest version number for a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT MAX(version_number) FROM versions WHERE session_id = ?",
            (session_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] or 0
    
    def rollback_to_version(self, session_id: str, target_version: int) -> bool:
        """Rollback to a specific version by deleting all newer versions and related chat messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # First, get the timestamp of the target version
            cursor.execute('''
                SELECT created_at FROM versions 
                WHERE session_id = ? AND version_number = ?
            ''', (session_id, target_version))
            
            target_result = cursor.fetchone()
            if not target_result:
                conn.close()
                return False
            
            target_timestamp = target_result[0]
            
            # Delete all versions newer than the target version
            cursor.execute('''
                DELETE FROM versions 
                WHERE session_id = ? AND version_number > ?
            ''', (session_id, target_version))
            
            # Delete all chat messages created after the target version
            cursor.execute('''
                DELETE FROM chat_messages 
                WHERE session_id = ? AND created_at > ?
            ''', (session_id, target_timestamp))
            
            # Update session's updated_at timestamp
            cursor.execute('''
                UPDATE sessions 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            print(f"Error during rollback: {e}")
            return False
