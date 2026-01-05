import streamlit as st
import json
from datetime import datetime
from pathlib import Path

# Configuration

DATA_FILE = Path("tasks_data.json")

# Initialize session state

if 'tasks' not in st.session_state:
st.session_state.tasks = {
'urgent_important': [],
'not_urgent_important': [],
'urgent_not_important': [],
'not_urgent_not_important': []
}
st.session_state.completed_tasks = []

# Load tasks from file

def load_tasks():
if DATA_FILE.exists():
try:
with open(DATA_FILE, 'r') as f:
data = json.load(f)
st.session_state.tasks = data.get('tasks', st.session_state.tasks)
st.session_state.completed_tasks = data.get('completed_tasks', [])
except Exception as e:
st.error(f"Error loading tasks: {e}")

# Save tasks to file

def save_tasks():
try:
data = {
'tasks': st.session_state.tasks,
'completed_tasks': st.session_state.completed_tasks
}
with open(DATA_FILE, 'w') as f:
json.dump(data, f, indent=2)
except Exception as e:
st.error(f"Error saving tasks: {e}")

# Add task

def add_task(category, task_text):
if task_text.strip():
task = {
'text': task_text,
'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
'id': datetime.now().timestamp()
}
st.session_state.tasks[category].append(task)
save_tasks()

# Complete task

def complete_task(category, task_id):
tasks = st.session_state.tasks[category]
task = next((t for t in tasks if t['id'] == task_id), None)
if task:
task['completed'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
task['category'] = category
st.session_state.completed_tasks.append(task)
st.session_state.tasks[category] = [t for t in tasks if t['id'] != task_id]
save_tasks()

# Delete task

def delete_task(category, task_id):
st.session_state.tasks[category] = [
t for t in st.session_state.tasks[category] if t['id'] != task_id
]
save_tasks()

# Load tasks on startup

load_tasks()

# App layout

st.title("Eisenhower Matrix Task Manager")
st.markdown("*Organize tasks by urgency and importance*")

# Create two columns for the matrix

col1, col2 = st.columns(2)

# Quadrant 1: Urgent & Important

with col1:
st.markdown("### 🔴 DO FIRST")
st.caption("Urgent & Important")

```
new_task = st.text_input("Add task:", key="urgent_important_input")
if st.button("Add", key="urgent_important_add"):
    add_task('urgent_important', new_task)
    st.rerun()

tasks = st.session_state.tasks['urgent_important']
if tasks:
    for task in tasks:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"- {task['text']}")
            st.caption(f"Added: {task['created']}")
        with col_b:
            if st.button("✓", key=f"complete_urgent_important_{task['id']}"):
                complete_task('urgent_important', task['id'])
                st.rerun()
            if st.button("🗑️", key=f"delete_urgent_important_{task['id']}"):
                delete_task('urgent_important', task['id'])
                st.rerun()
else:
    st.info("No tasks yet")
```

# Quadrant 2: Not Urgent & Important

with col2:
st.markdown("### 🟡 SCHEDULE")
st.caption("Not Urgent & Important")

```
new_task = st.text_input("Add task:", key="not_urgent_important_input")
if st.button("Add", key="not_urgent_important_add"):
    add_task('not_urgent_important', new_task)
    st.rerun()

tasks = st.session_state.tasks['not_urgent_important']
if tasks:
    for task in tasks:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"- {task['text']}")
            st.caption(f"Added: {task['created']}")
        with col_b:
            if st.button("✓", key=f"complete_not_urgent_important_{task['id']}"):
                complete_task('not_urgent_important', task['id'])
                st.rerun()
            if st.button("🗑️", key=f"delete_not_urgent_important_{task['id']}"):
                delete_task('not_urgent_important', task['id'])
                st.rerun()
else:
    st.info("No tasks yet")
```

st.divider()

# Quadrant 3: Urgent & Not Important

col3, col4 = st.columns(2)

with col3:
st.markdown("### 🟠 DELEGATE")
st.caption("Urgent & Not Important")

```
new_task = st.text_input("Add task:", key="urgent_not_important_input")
if st.button("Add", key="urgent_not_important_add"):
    add_task('urgent_not_important', new_task)
    st.rerun()

tasks = st.session_state.tasks['urgent_not_important']
if tasks:
    for task in tasks:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"- {task['text']}")
            st.caption(f"Added: {task['created']}")
        with col_b:
            if st.button("✓", key=f"complete_urgent_not_important_{task['id']}"):
                complete_task('urgent_not_important', task['id'])
                st.rerun()
            if st.button("🗑️", key=f"delete_urgent_not_important_{task['id']}"):
                delete_task('urgent_not_important', task['id'])
                st.rerun()
else:
    st.info("No tasks yet")
```

# Quadrant 4: Not Urgent & Not Important

with col4:
st.markdown("### 🟢 ELIMINATE")
st.caption("Not Urgent & Not Important")

```
new_task = st.text_input("Add task:", key="not_urgent_not_important_input")
if st.button("Add", key="not_urgent_not_important_add"):
    add_task('not_urgent_not_important', new_task)
    st.rerun()

tasks = st.session_state.tasks['not_urgent_not_important']
if tasks:
    for task in tasks:
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.markdown(f"- {task['text']}")
            st.caption(f"Added: {task['created']}")
        with col_b:
            if st.button("✓", key=f"complete_not_urgent_not_important_{task['id']}"):
                complete_task('not_urgent_not_important', task['id'])
                st.rerun()
            if st.button("🗑️", key=f"delete_not_urgent_not_important_{task['id']}"):
                delete_task('not_urgent_not_important', task['id'])
                st.rerun()
else:
    st.info("No tasks yet")
```

# Completed tasks section

st.divider()
with st.expander(f"📋 Completed Tasks ({len(st.session_state.completed_tasks)})"):
if st.session_state.completed_tasks:
for task in reversed(st.session_state.completed_tasks[-20:]):  # Show last 20
category_labels = {
'urgent_important': '🔴 DO FIRST',
'not_urgent_important': '🟡 SCHEDULE',
'urgent_not_important': '🟠 DELEGATE',
'not_urgent_not_important': '🟢 ELIMINATE'
}
st.markdown(f"**{task['text']}** - {category_labels.get(task['category'], '')}")
st.caption(f"Completed: {task['completed']}")
else:
st.info("No completed tasks yet")
