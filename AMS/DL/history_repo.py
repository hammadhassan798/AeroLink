import json
from config import get_db
from datetime import datetime

UNDO_STACK = []
REDO_STACK = []

def load_stacks_from_db():
    global UNDO_STACK, REDO_STACK
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""SELECT * FROM action_history WHERE is_reversible = TRUE ORDER BY action_id ASC""")
    rows = cursor.fetchall()
    conn.close()
    UNDO_STACK.clear()
    REDO_STACK.clear()
    for row in rows:
        old_data = json.loads(row['old_value']) if row['old_value'] else None
        new_data = json.loads(row['new_value']) if row['new_value'] else None

        action = {
            'action_id': row['action_id'],
            'action_type': row['action_type'],
            'affected_table': row['affected_table'],
            'affected_id': row['affected_id'],
            'old_value': old_data,
            'new_value': new_data
        }
        UNDO_STACK.append(action)
    print(f"Loaded {len(UNDO_STACK)} actions into UNDO_STACK")

def record_action(action_type, affected_table, affected_id, old_data, new_data):
    global UNDO_STACK, REDO_STACK
    conn = get_db()
    cursor = conn.cursor()
    old_value_str = json.dumps(old_data, default=str) if old_data else None
    new_value_str = json.dumps(new_data, default=str) if new_data else None
    cursor.execute("""INSERT INTO action_history (action_type, affected_table, affected_id, old_value, new_value, is_reversible, action_time
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (
        action_type,
        affected_table,
        affected_id,
        old_value_str,
        new_value_str,
        True,
        datetime.now()
    ))
    action_id = cursor.lastrowid
    conn.commit()
    conn.close()
    UNDO_STACK.append({
        'action_id': action_id,
        'action_type': action_type,
        'affected_table': affected_table,
        'affected_id': affected_id,
        'old_value': old_data,
        'new_value': new_data,
    })
    REDO_STACK.clear()