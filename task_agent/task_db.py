import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class TaskDatabase:
    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with tasks table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT CHECK(priority IN ('High', 'Medium', 'Low')) DEFAULT 'Medium',
                status TEXT CHECK(status IN ('pending', 'completed')) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    
    def create_task(self, title: str, description: str = "", priority: str = "Medium") -> Dict:
        """Create a new task"""
        if priority not in ['High', 'Medium', 'Low']:
            priority = 'Medium'
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)",
            (title, description, priority)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "id": task_id,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending"
        }
    
    def list_tasks(self, status: Optional[str] = None, priority: Optional[str] = None) -> List[Dict]:
        """List tasks with optional filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        
        query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END, created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """Get a single task by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = 'completed', completed_at = ? WHERE id = ?",
            (datetime.now().isoformat(), task_id)
        )
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected > 0

# Made with Bob
