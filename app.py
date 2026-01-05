import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configuration
DATA_FILE = "tasks_data.json"

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = {
        "urgent_important": [],
        "not_urgent_important": [],
        "urgent_not_important": [],
        "not_urgent_not_important": []
    }
    st.session_state.completed_tasks = []

# Load tasks from file
def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                st.session_state.tasks = data.get("tasks", st.session_state.tasks)
                st.session_state.completed_tasks = data.get("completed_tasks", [])
        except Exception as e:
            st.error(f"Error loading tasks: {e}")

# Save tasks to file
def save_tasks():
    try:
        data = {
            "tasks": st.session_state.tasks,
            "completed_tasks": st.session_state.completed_tasks
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving tasks: {e}")

# Add task
def add_task(category, task_text):
    if task_text.strip():
        task = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "text": task_text.strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.tasks[category].append(task)
        save_tasks()
        return True
    return False

# Complete task
def complete_task(category, task_id):
    task_list = st.session_state.tasks[category]
    task_to_complete = None
    
    for i, task in enumerate(task_list):
        if task["id"] == task_id:
            task_to_complete = task_list.pop(i)
            break
    
    if task_to_complete:
        task_to_complete["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        task_to_complete["category"] = category
        st.session_state.completed_tasks.append(task_to_complete)
        save_tasks()

# Delete task
def delete_task(category, task_id):
    task_list = st.session_state.tasks[category]
    st.session_state.tasks[category] = [t for t in task_list if t["id"] != task_id]
    save_tasks()

# Delete completed task
def delete_completed_task(task_id):
    st.session_state.completed_tasks = [t for t in st.session_state.completed_tasks if t["id"] != task_id]
    save_tasks()

# Load tasks on startup
load_tasks()

# Page configuration
st.set_page_config(
    page_title="Eisenhower Matrix Task Manager",
    page_icon="📋",
    layout="wide"
)

# Title
st.title("📋 Eisenhower Matrix Task Manager")
st.markdown("---")


# Create tabs
tab1, tab2 = st.tabs(["📋 Active Tasks", "✅ Completed Tasks"])

# Tab 1: Active Tasks (Eisenhower Matrix)
with tab1:
    # Category definitions
    categories = {
        "urgent_important": {
            "title": "🔥 Urgent & Important",
            "description": "Do First - Critical tasks that require immediate attention",
            "color": "#ff4b4b"
        },
        "not_urgent_important": {
            "title": "📅 Not Urgent & Important",
            "description": "Schedule - Important tasks for long-term success",
            "color": "#4b7bff"
        },
        "urgent_not_important": {
            "title": "⚡ Urgent & Not Important",
            "description": "Delegate - Tasks that are urgent but not critical",
            "color": "#ffa500"
        },
        "not_urgent_not_important": {
            "title": "🗑️ Not Urgent & Not Important",
            "description": "Eliminate - Tasks with minimal value",
            "color": "#808080"
        }
    }

    # Create two rows of two columns
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)

    columns = [row1_col1, row1_col2, row2_col1, row2_col2]
    category_keys = list(categories.keys())

    # Render each quadrant
    for idx, (category_key, category_info) in enumerate(categories.items()):
        with columns[idx]:
            st.markdown(f"### {category_info['title']}")
            st.markdown(f"*{category_info['description']}*")
            
            # Add new task
            with st.form(key=f"form_{category_key}"):
                new_task = st.text_input(
                    "Add new task",
                    key=f"input_{category_key}",
                    label_visibility="collapsed",
                    placeholder="Enter task description..."
                )
                submit = st.form_submit_button("➕ Add Task", use_container_width=True)
                
                if submit:
                    if add_task(category_key, new_task):
                        st.success("Task added!")
                        st.rerun()
                    else:
                        st.warning("Please enter a task description")
            
            st.markdown("---")
            
            # Display tasks
            tasks = st.session_state.tasks[category_key]
            
            if not tasks:
                st.info("No tasks in this category")
            else:
                for task in tasks:
                    col_text, col_complete, col_delete = st.columns([6, 1, 1])
                    
                    with col_text:
                        st.markdown(f"**{task['text']}**")
                        st.caption(f"Created: {task['created_at']}")
                    
                    with col_complete:
                        if st.button("✓", key=f"complete_{task['id']}", help="Complete task"):
                            complete_task(category_key, task["id"])
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️", key=f"delete_{task['id']}", help="Delete task"):
                            delete_task(category_key, task["id"])
                            st.rerun()
                    
                    st.markdown("---")
    
    st.markdown("---")
    st.markdown("*Tasks are automatically saved and persist between sessions*")

# Tab 2: Completed Tasks
with tab2:
    st.header("✅ Completed Tasks")
    
    if st.session_state.completed_tasks:
        # Summary statistics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Completed Tasks", len(st.session_state.completed_tasks))
        with col2:
            if st.button("🗑️ Clear All Completed Tasks", use_container_width=True):
                st.session_state.completed_tasks = []
                save_tasks()
                st.rerun()
        
        st.markdown("---")
        
        # Create dataframe for completed tasks
        completed_data = []
        category_labels = {
            "urgent_important": "Urgent & Important",
            "not_urgent_important": "Not Urgent & Important",
            "urgent_not_important": "Urgent & Not Important",
            "not_urgent_not_important": "Not Urgent & Not Important"
        }
        
        for task in st.session_state.completed_tasks:
            completed_data.append({
                "Task": task["text"],
                "Category": category_labels.get(task["category"], task["category"]),
                "Created": task["created_at"],
                "Completed": task["completed_at"],
                "ID": task["id"]
            })
        
        df = pd.DataFrame(completed_data)
        
        # Display the dataframe
        st.dataframe(
            df[["Task", "Category", "Created", "Completed"]],
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # Option to delete individual completed tasks
        st.subheader("Manage Completed Tasks")
        
        for idx, task in enumerate(reversed(st.session_state.completed_tasks)):
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"**{task['text']}** - {category_labels.get(task['category'], task['category'])}")
                st.caption(f"Completed: {task['completed_at']}")
            with col2:
                if st.button("🗑️", key=f"delete_completed_{task['id']}", help="Delete this completed task"):
                    delete_completed_task(task["id"])
                    st.rerun()
            
            if idx < len(st.session_state.completed_tasks) - 1:
                st.markdown("---")
    else:
        st.info("No completed tasks yet. Complete tasks from the Active Tasks tab to see them here.")