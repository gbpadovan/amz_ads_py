"""Database operations for Amazon Advertising reports."""
import os
import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, List, Any
from contextlib import contextmanager
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ReportDatabase:
    """Manages report metadata and links in a SQLite database.
    
    Handles concurrent access for async operations and stores Amazon Advertising
    API report data according to the v3 API specification.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database connection.
        
        Args:
            db_path: Optional path to the database file. If None, creates 'reports.db'
                    in the current working directory.
        """
        if db_path is None:
            db_path = os.path.join(os.getcwd(), 'reports.db')
        self.db_path = db_path
        self._init_db()
        # Thread pool for async database operations
        self._executor = ThreadPoolExecutor(max_workers=10)
        # Lock for thread-safe database operations
        self._lock = asyncio.Lock()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections with proper locking."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable row factory for dict-like access
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Initialize the database schema according to Amazon Advertising API v3."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create reports table with fields matching Amazon's API response
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    -- Report identification
                    report_id TEXT PRIMARY KEY,
                    name TEXT,
                    
                    -- Report dates
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP,
                    start_date DATE,
                    end_date DATE,
                    
                    -- Report configuration (stored as JSON)
                    configuration TEXT,  -- Complete report configuration including:
                                       -- adProduct, columns, format, reportTypeId, groupBy, timeUnit
                    
                    -- Report status
                    status TEXT,     -- PENDING, IN_PROGRESS, COMPLETED, FAILED
                    
                    -- Download information
                    url TEXT,            -- Download URL when available
                    file_size_bytes INTEGER,
                    location TEXT,       -- Local file path after download
                    
                    -- Error tracking
                    error_message TEXT,
                    retry_count INTEGER DEFAULT 0,
                    
                    -- API specific fields
                    api_request_id TEXT,    -- From X-Amz-RequestId header
                    api_timestamp TEXT,     -- From x-amz-date header
                    api_status_code INTEGER -- HTTP status code
                )
            ''')
            
            # Create an index on status for quick retrieval of pending reports
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_reports_status 
                ON reports(status)
            ''')
            
            # Create a table for report processing history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS report_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_id TEXT,
                    timestamp TIMESTAMP,
                    status TEXT,
                    details TEXT,
                    FOREIGN KEY(report_id) REFERENCES reports(report_id)
                )
            ''')
            
            conn.commit()

    async def add_report(self, report_data: Dict[str, Any]) -> None:
        """Add a new report entry to the database asynchronously.
        
        Args:
            report_data: Dictionary containing report information from Amazon API
        """
        async with self._lock:
            def db_operation():
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Convert configuration to JSON string if it's a dict
                    if 'configuration' in report_data and isinstance(report_data['configuration'], dict):
                        report_data['configuration'] = json.dumps(report_data['configuration'])
                    
                    # Prepare the insert statement dynamically based on available fields
                    fields = []
                    values = []
                    placeholders = []
                    
                    # Map Amazon API response fields to database fields
                    field_mapping = {
                        'reportId': 'report_id',
                        'name': 'name',
                        'createdAt': 'created_at',
                        'updatedAt': 'updated_at',
                        'startDate': 'start_date',
                        'endDate': 'end_date',
                        'configuration': 'configuration',
                        'status': 'status'
                    }
                    
                    # Process fields using the mapping
                    for api_field, db_field in field_mapping.items():
                        if api_field in report_data:
                            fields.append(db_field)
                            values.append(report_data[api_field])
                            placeholders.append('?')
                    
                    # Add any additional fields that might be present
                    for key, value in report_data.items():
                        db_field = key.lower()
                        if db_field not in fields and db_field in [col[1] for col in cursor.execute("PRAGMA table_info(reports)").fetchall()]:
                            fields.append(db_field)
                            values.append(value)
                            placeholders.append('?')
                    
                    query = f'''
                        INSERT OR REPLACE INTO reports 
                        ({', '.join(fields)}) 
                        VALUES ({', '.join(placeholders)})
                    '''
                    
                    cursor.execute(query, values)
                    
                    # Add entry to history
                    cursor.execute('''
                        INSERT INTO report_history 
                        (report_id, timestamp, status, details) 
                        VALUES (?, ?, ?, ?)
                    ''', (
                        report_data.get('reportId') or report_data.get('report_id'),
                        datetime.utcnow().isoformat(),
                        report_data.get('status', 'CREATED'),
                        'Report entry created'
                    ))
                    
                    conn.commit()
            
            await asyncio.get_event_loop().run_in_executor(self._executor, db_operation)

    async def update_report_status(
        self,
        report_id: str,
        status: str,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> None:
        """Update report status and related information asynchronously.
        
        Args:
            report_id: The ID of the report to update
            status: Current status from Amazon API
            response_data: Complete response data from Amazon API
            error_message: Optional error message if status is 'FAILED'
        """
        async with self._lock:
            def db_operation():
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    update_fields = ['status = ?', 'updated_at = ?']
                    params = [status, datetime.utcnow().isoformat()]
                    
                    if response_data:
                        # Map Amazon API response fields to database fields
                        field_mapping = {
                            'reportId': 'report_id',
                            'name': 'name',
                            'createdAt': 'created_at',
                            'updatedAt': 'updated_at',
                            'startDate': 'start_date',
                            'endDate': 'end_date',
                            'configuration': 'configuration',
                            'status': 'status'
                        }
                        
                        for api_field, db_field in field_mapping.items():
                            if api_field in response_data:
                                value = response_data[api_field]
                                if isinstance(value, (dict, list)):
                                    value = json.dumps(value)
                                update_fields.append(f'{db_field} = ?')
                                params.append(value)
                    
                    if error_message:
                        update_fields.append('error_message = ?')
                        params.append(error_message)
                    
                    params.append(report_id)
                    
                    query = f'''
                        UPDATE reports 
                        SET {', '.join(update_fields)}
                        WHERE report_id = ?
                    '''
                    cursor.execute(query, params)
                    
                    # Add entry to history
                    cursor.execute('''
                        INSERT INTO report_history 
                        (report_id, timestamp, status, details) 
                        VALUES (?, ?, ?, ?)
                    ''', (
                        report_id,
                        datetime.utcnow().isoformat(),
                        status,
                        error_message or f'Status updated to {status}'
                    ))
                    
                    conn.commit()
            
            await asyncio.get_event_loop().run_in_executor(self._executor, db_operation)

    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a report by its ID asynchronously."""
        async with self._lock:
            def db_operation():
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT * FROM reports WHERE report_id = ?', (report_id,))
                    row = cursor.fetchone()
                    
                    if row:
                        result = dict(row)
                        # Parse JSON fields
                        if result.get('configuration'):
                            try:
                                result['configuration'] = json.loads(result['configuration'])
                            except json.JSONDecodeError:
                                pass
                        return result
                    return None
            
            return await asyncio.get_event_loop().run_in_executor(self._executor, db_operation)

    async def get_pending_reports(self) -> List[Dict[str, Any]]:
        """Retrieve all pending reports asynchronously."""
        async with self._lock:
            def db_operation():
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT * FROM reports 
                        WHERE status = 'PENDING'
                    ''')
                    return [dict(row) for row in cursor.fetchall()]
            
            return await asyncio.get_event_loop().run_in_executor(self._executor, db_operation)

    async def cleanup_expired_reports(self, days_to_keep: int = 30) -> int:
        """Remove old report entries but keep their history.
        
        Args:
            days_to_keep: Number of days to keep report data
            
        Returns:
            Number of cleaned up reports
        """
        async with self._lock:
            def db_operation():
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cutoff_date = (
                        datetime.utcnow()
                        .replace(hour=0, minute=0, second=0, microsecond=0)
                        .timestamp() - (days_to_keep * 86400)
                    )
                    
                    # Add final history entry for reports being cleaned up
                    cursor.execute('''
                        INSERT INTO report_history 
                        (report_id, timestamp, status, details)
                        SELECT 
                            report_id,
                            datetime('now'),
                            'CLEANED_UP',
                            'Report removed during cleanup'
                        FROM reports
                        WHERE strftime('%s', created_at) < ?
                    ''', (cutoff_date,))
                    
                    # Delete old reports
                    cursor.execute('''
                        DELETE FROM reports 
                        WHERE strftime('%s', created_at) < ?
                    ''', (cutoff_date,))
                    
                    deleted_count = cursor.rowcount
                    conn.commit()
                    return deleted_count
            
            return await asyncio.get_event_loop().run_in_executor(self._executor, db_operation)

    async def get_report_history(self, report_id: str) -> List[Dict[str, Any]]:
        """Get the complete history of a report's status changes."""
        async with self._lock:
            def db_operation():
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT * FROM report_history 
                        WHERE report_id = ? 
                        ORDER BY timestamp
                    ''', (report_id,))
                    return [dict(row) for row in cursor.fetchall()]
            
            return await asyncio.get_event_loop().run_in_executor(self._executor, db_operation)
