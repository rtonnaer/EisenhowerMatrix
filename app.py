import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
from pathlib import Path

# Configuration
DATA_FILE = "tasks_data.json"
LABELS_CONFIG_FILE = "labels_config.json"

# Load labels configuration
def load_labels_config():
    if os.path.exists(LABELS_CONFIG_FILE):
        try:
            with open(LABELS_CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading labels config: {e}")
            return None
    return None

# Initialize labels from config
def initialize_labels():
    config = load_labels_config()
    if config and "default_labels" in config:
        labels = [label["name"] for label in config["default_labels"]]
        label_colors = {label["name"]: label["color"] for label in config["default_labels"]}
        return labels, label_colors, config.get("auto_generate_colors", True)
    # Fallback to default if config doesn't exist
    default_labels = ["work", "personal", "urgent", "health", "finance"]
    default_colors = {
        "work": "#3b82f6",
        "personal": "#8b5cf6",
        "urgent": "#ef4444",
        "health": "#10b981",
        "finance": "#f59e0b"
    }
    return default_labels, default_colors, True

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = {
        "urgent_important": [],
        "not_urgent_important": [],
        "urgent_not_important": [],
        "not_urgent_not_important": []
    }
    st.session_state.completed_tasks = []

if "editing_task" not in st.session_state:
    st.session_state.editing_task = None

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "available_labels" not in st.session_state:
    default_labels, label_colors_map, auto_gen = initialize_labels()
    st.session_state.available_labels = default_labels
    st.session_state.label_colors = label_colors_map
    st.session_state.auto_generate_colors = auto_gen

if "active_filters" not in st.session_state:
    st.session_state.active_filters = {
        "urgent_important": set(),
        "not_urgent_important": set(),
        "urgent_not_important": set(),
        "not_urgent_not_important": set()
    }

# Load tasks from file
def load_tasks():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                st.session_state.tasks = data.get("tasks", st.session_state.tasks)
                st.session_state.completed_tasks = data.get("completed_tasks", [])
                
                # Load label colors if they exist, otherwise keep config defaults
                if "label_colors" in data:
                    # Merge saved colors with config colors (config takes precedence for defaults)
                    saved_colors = data.get("label_colors", {})
                    st.session_state.label_colors.update(saved_colors)
        except Exception as e:
            st.error(f"Error loading tasks: {e}")

# Save tasks to file
def save_tasks():
    try:
        data = {
            "tasks": st.session_state.tasks,
            "completed_tasks": st.session_state.completed_tasks,
            "label_colors": st.session_state.label_colors
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving tasks: {e}")

# Add task
def add_task(category, task_name, task_description, due_date=None, labels=None):
    if task_name.strip():
        task = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "name": task_name.strip(),
            "description": task_description.strip() if task_description else "",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "due_date": due_date.strftime("%Y-%m-%d") if due_date else None,
            "priority": len(st.session_state.tasks[category]),  # Add at end by default
            "labels": labels if labels else []
        }
        st.session_state.tasks[category].append(task)
        save_tasks()
        return True
    return False

# Edit task
def edit_task(category, task_id, new_name, new_description, new_due_date=None, new_labels=None):
    task_list = st.session_state.tasks[category]
    for task in task_list:
        if task["id"] == task_id:
            task["name"] = new_name.strip()
            task["description"] = new_description.strip() if new_description else ""
            task["due_date"] = new_due_date.strftime("%Y-%m-%d") if new_due_date else None
            task["labels"] = new_labels if new_labels else []
            save_tasks()
            return True
    return False

# Move task to different category
def move_task(from_category, to_category, task_id):
    task_list = st.session_state.tasks[from_category]
    task_to_move = None
    
    for i, task in enumerate(task_list):
        if task["id"] == task_id:
            task_to_move = task_list.pop(i)
            break
    
    if task_to_move:
        task_to_move["priority"] = len(st.session_state.tasks[to_category])
        st.session_state.tasks[to_category].append(task_to_move)
        # Reindex priorities in source category
        for idx, task in enumerate(st.session_state.tasks[from_category]):
            task["priority"] = idx
        save_tasks()
        return True
    return False

# Move task up in priority
def move_task_up(category, task_id):
    task_list = st.session_state.tasks[category]
    for i, task in enumerate(task_list):
        if task["id"] == task_id and i > 0:
            task_list[i], task_list[i-1] = task_list[i-1], task_list[i]
            # Update priorities
            for idx, t in enumerate(task_list):
                t["priority"] = idx
            save_tasks()
            return True
    return False

# Move task down in priority
def move_task_down(category, task_id):
    task_list = st.session_state.tasks[category]
    for i, task in enumerate(task_list):
        if task["id"] == task_id and i < len(task_list) - 1:
            task_list[i], task_list[i+1] = task_list[i+1], task_list[i]
            # Update priorities
            for idx, t in enumerate(task_list):
                t["priority"] = idx
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
        # Ensure backward compatibility with old 'text' field
        if "text" in task_to_complete and "name" not in task_to_complete:
            task_to_complete["name"] = task_to_complete["text"]
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

# Check if task is overdue
def is_overdue(due_date_str):
    if not due_date_str:
        return False
    from datetime import datetime as dt
    due_date = dt.strptime(due_date_str, "%Y-%m-%d")
    return due_date.date() < dt.now().date()

# Get days until due
def days_until_due(due_date_str):
    if not due_date_str:
        return None
    from datetime import datetime as dt
    due_date = dt.strptime(due_date_str, "%Y-%m-%d")
    delta = (due_date.date() - dt.now().date()).days
    return delta

# Get label color
def get_label_color(label):
    # First check if color is defined in session state (from config)
    if label in st.session_state.label_colors:
        return st.session_state.label_colors[label]
    
    # If auto-generate is enabled, create a color for new labels
    if st.session_state.auto_generate_colors:
        import hashlib
        hash_val = int(hashlib.md5(label.encode()).hexdigest()[:6], 16)
        r = (hash_val >> 16) & 255
        g = (hash_val >> 8) & 255
        b = hash_val & 255
        color = f"#{r:02x}{g:02x}{b:02x}"
        # Save it for consistency
        st.session_state.label_colors[label] = color
        return color
    
    # Fallback color if auto-generate is disabled
    return "#808080"

# Filter tasks by active labels
def filter_tasks_by_labels(tasks, active_filters):
    if not active_filters:
        return tasks
    
    filtered = []
    for task in tasks:
        task_labels = set(task.get("labels", []))
        # Show task if it has any of the active filter labels
        if task_labels.intersection(active_filters):
            filtered.append(task)
    
    return filtered

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

# Theme toggle in header
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🌓 Theme", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# Apply theme-specific styles
if st.session_state.dark_mode:
    # Dark mode colors
    bg_color = "#1e1e1e"
    text_color = "#e0e0e0"
    card_bg = "#2d2d2d"
    card_border = "#404040"
    header_text = "#ffffff"
    secondary_text = "#b0b0b0"
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    # Light mode colors
    bg_color = "#ffffff"
    text_color = "#262730"
    card_bg = "#f0f2f6"
    card_border = "#e0e0e0"
    header_text = "#262730"
    secondary_text = "#666666"

st.markdown("---")


# Create tabs
tab1, tab2, tab3 = st.tabs(["📋 Active Tasks", "✅ Completed Tasks", "📊 Statistics"])

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
            # Category header with background color
            st.markdown(
                f"""
                <div style="background-color: {category_info['color']}; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                    <h3 style="color: white; margin: 0;">{category_info['title']}</h3>
                    <p style="color: white; margin: 5px 0 0 0; font-size: 0.9em;">{category_info['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Add new task
            with st.form(key=f"form_{category_key}", clear_on_submit=True):
                new_task_name = st.text_input(
                    "Task Name",
                    key=f"input_name_{category_key}",
                    placeholder="Enter task name..."
                )
                new_task_description = st.text_area(
                    "Description (optional)",
                    key=f"input_desc_{category_key}",
                    placeholder="Enter task description...",
                    height=80
                )
                new_task_due_date = st.date_input(
                    "Due Date (optional)",
                    key=f"input_due_{category_key}",
                    value=None
                )
                new_task_labels = st.multiselect(
                    "Labels (optional)",
                    options=st.session_state.available_labels,
                    key=f"input_labels_{category_key}"
                )
                
                submit = st.form_submit_button("➕ Add Task", use_container_width=True)
                
                if submit:
                    if add_task(category_key, new_task_name, new_task_description, new_task_due_date, new_task_labels):
                        st.success("Task added!")
                        st.rerun()
                    else:
                        st.warning("Please enter a task name")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Label filter buttons
            # Get all labels used in this category
            category_labels_used = set()
            for task in st.session_state.tasks[category_key]:
                category_labels_used.update(task.get("labels", []))
            
            if category_labels_used:
                st.markdown("**Filter by labels:**")
                
                # Create filter buttons
                filter_cols = st.columns(min(len(category_labels_used) + 1, 6))
                
                # Clear filter button
                with filter_cols[0]:
                    if st.button("🔄 Clear", key=f"clear_filter_{category_key}", use_container_width=True):
                        st.session_state.active_filters[category_key] = set()
                        st.rerun()
                
                # Label filter buttons
                for idx, label in enumerate(sorted(category_labels_used)):
                    if idx + 1 < len(filter_cols):
                        with filter_cols[idx + 1]:
                            is_active = label in st.session_state.active_filters[category_key]
                            button_style = "primary" if is_active else "secondary"
                            label_color = get_label_color(label)
                            
                            if st.button(
                                f"{'✓ ' if is_active else ''}{label}",
                                key=f"filter_{category_key}_{label}",
                                use_container_width=True,
                                type=button_style
                            ):
                                if is_active:
                                    st.session_state.active_filters[category_key].discard(label)
                                else:
                                    st.session_state.active_filters[category_key].add(label)
                                st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Display tasks as custom styled list
            tasks = st.session_state.tasks[category_key]
            
            # Apply label filters
            if st.session_state.active_filters[category_key]:
                tasks = filter_tasks_by_labels(tasks, st.session_state.active_filters[category_key])
            
            # Sort tasks by priority
            tasks.sort(key=lambda x: x.get("priority", 0))
            
            if not tasks:
                st.info("No tasks in this category")
            else:
                for task_idx, task in enumerate(tasks):
                    # Handle backward compatibility with old 'text' field
                    task_name = task.get("name", task.get("text", "Untitled"))
                    task_desc = task.get("description", "")
                    task_id = task["id"]
                    task_due = task.get("due_date")
                    task_labels = task.get("labels", [])
                    
                    # Check if overdue
                    overdue = is_overdue(task_due)
                    days_left = days_until_due(task_due)
                    
                    # Determine due date display and styling
                    due_date_html = ""
                    if task_due:
                        if overdue:
                            due_date_html = f'<span style="color: #ff4b4b; font-weight: bold;">⚠️ OVERDUE: {task_due}</span>'
                        elif days_left is not None and days_left <= 3:
                            due_date_html = f'<span style="color: #ffa500; font-weight: bold;">⏰ Due: {task_due} ({days_left} days)</span>'
                        else:
                            due_date_html = f'<span style="color: {secondary_text};">📅 Due: {task_due}</span>'
                    
                    # Check if this task is being edited
                    is_editing = (st.session_state.editing_task == f"{category_key}_{task_id}")
                    
                    # Set background color for overdue tasks
                    task_bg_color = "#ffebee" if overdue and not st.session_state.dark_mode else "#3d2020" if overdue else card_bg
                    
                    if is_editing:
                        # Edit mode - show form
                        st.markdown(
                            f"""
                            <div style="background-color: #fff3cd; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {category_info['color']};">
                                <div style="font-size: 0.9em; font-weight: 600; color: #856404; margin-bottom: 8px;">
                                    ✏️ Editing Task
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                        with st.form(key=f"edit_form_{task_id}"):
                            edit_name = st.text_input("Task Name", value=task_name, key=f"edit_name_{task_id}")
                            edit_desc = st.text_area("Description", value=task_desc, key=f"edit_desc_{task_id}", height=80)
                            
                            # Parse existing due date for date input
                            from datetime import datetime as dt
                            edit_due_default = dt.strptime(task_due, "%Y-%m-%d").date() if task_due else None
                            edit_due = st.date_input("Due Date", value=edit_due_default, key=f"edit_due_{task_id}")
                            
                            edit_labels = st.multiselect(
                                "Labels",
                                options=st.session_state.available_labels,
                                default=task_labels,
                                key=f"edit_labels_{task_id}"
                            )
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Save", use_container_width=True):
                                    if edit_task(category_key, task_id, edit_name, edit_desc, edit_due, edit_labels):
                                        st.session_state.editing_task = None
                                        st.success("Task updated!")
                                        st.rerun()
                            with col2:
                                if st.form_submit_button("❌ Cancel", use_container_width=True):
                                    st.session_state.editing_task = None
                                    st.rerun()
                    else:
                        # Normal display mode
                        # Build the complete HTML with proper escaping
                        task_html = f"""
                        <div style="background-color: {task_bg_color}; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {category_info['color']};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div style="flex-grow: 1;">
                                    <div style="font-size: 1.1em; font-weight: 600; color: {text_color}; margin-bottom: 5px;">
                                        {task_name}
                                    </div>
                                    <div style="font-size: 0.85em; color: {secondary_text}; margin-bottom: 3px;">
                                        {task_desc if task_desc else '<em>No description</em>'}
                                    </div>
                                    <div style="font-size: 0.75em; color: {secondary_text};">
                                        Created: {task['created_at']}
                                    </div>
                                    <div style="font-size: 0.75em; margin-top: 3px;">
                                        {due_date_html}
                                    </div>
                        """
                        
                        # Add labels if they exist
                        if task_labels:
                            task_html += '<div style="margin-top: 5px;">'
                            for label in task_labels:
                                label_color = get_label_color(label)
                                task_html += f'<span style="background-color: {label_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7em; margin-right: 4px; display: inline-block;">{label}</span>'
                            task_html += '</div>'
                        
                        task_html += """
                                </div>
                            </div>
                        </div>
                        """
                        
                        st.markdown(task_html, unsafe_allow_html=True)
                        
                        # Priority ordering buttons
                        col_up, col_down, col_edit, col_move, col_complete, col_delete = st.columns([0.7, 0.7, 1, 1, 1, 0.8])
                        
                        with col_up:
                            if task_idx > 0:
                                if st.button("⬆️", key=f"up_{task_id}", use_container_width=True, help="Move up"):
                                    move_task_up(category_key, task_id)
                                    st.rerun()
                        
                        with col_down:
                            if task_idx < len(tasks) - 1:
                                if st.button("⬇️", key=f"down_{task_id}", use_container_width=True, help="Move down"):
                                    move_task_down(category_key, task_id)
                                    st.rerun()
                        
                        with col_edit:
                            if st.button("✏️ Edit", key=f"edit_{task_id}", use_container_width=True):
                                st.session_state.editing_task = f"{category_key}_{task_id}"
                                st.rerun()
                        
                        with col_move:
                            if st.button("↔️ Move", key=f"move_{task_id}", use_container_width=True):
                                st.session_state.editing_task = f"move_{category_key}_{task_id}"
                                st.rerun()
                        
                        with col_complete:
                            if st.button("✓ Done", key=f"complete_{task_id}", use_container_width=True):
                                complete_task(category_key, task_id)
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️", key=f"delete_{task_id}", use_container_width=True):
                                delete_task(category_key, task_id)
                                st.rerun()
                        
                        # Move dialog
                        if st.session_state.editing_task == f"move_{category_key}_{task_id}":
                            st.markdown("**Move to:**")
                            
                            move_options = {k: v["title"] for k, v in categories.items() if k != category_key}
                            
                            cols = st.columns(len(move_options))
                            for idx, (move_cat_key, move_cat_title) in enumerate(move_options.items()):
                                with cols[idx]:
                                    if st.button(move_cat_title, key=f"moveto_{move_cat_key}_{task_id}", use_container_width=True):
                                        move_task(category_key, move_cat_key, task_id)
                                        st.session_state.editing_task = None
                                        st.success(f"Moved to {move_cat_title}")
                                        st.rerun()
                            
                            if st.button("❌ Cancel Move", key=f"cancel_move_{task_id}", use_container_width=True):
                                st.session_state.editing_task = None
                                st.rerun()
                        
                        st.markdown("<br>", unsafe_allow_html=True)

    
    st.markdown("---")
    st.markdown("*Tasks are automatically saved and persist between sessions*")

# Tab 2: Completed Tasks
with tab2:
    st.header("✅ Completed Tasks")
    
    if st.session_state.completed_tasks:
        # Summary statistics and actions
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Completed Tasks", len(st.session_state.completed_tasks))
        with col2:
            # Download button
            completed_data_export = []
            category_labels = {
                "urgent_important": "Urgent & Important",
                "not_urgent_important": "Not Urgent & Important",
                "urgent_not_important": "Urgent & Not Important",
                "not_urgent_not_important": "Not Urgent & Not Important"
            }
            
            for task in st.session_state.completed_tasks:
                task_name = task.get("name", task.get("text", "Untitled"))
                task_desc = task.get("description", "")
                
                completed_data_export.append({
                    "Task Name": task_name,
                    "Description": task_desc,
                    "Category": category_labels.get(task["category"], task["category"]),
                    "Created": task["created_at"],
                    "Completed": task["completed_at"]
                })
            
            df_export = pd.DataFrame(completed_data_export)
            csv = df_export.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Tasks (CSV)",
                data=csv,
                file_name=f"completed_tasks_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col3:
            if st.button("🗑️ Clear All Completed", use_container_width=True):
                st.session_state.completed_tasks = []
                save_tasks()
                st.rerun()
        
        st.markdown("---")
        
        # Activity Timeline (GitLab-style contribution graph)
        st.subheader("📊 Activity Timeline")
        
        # Prepare data for timeline
        from collections import defaultdict
        from datetime import datetime as dt, timedelta
        
        # Count tasks completed per day
        daily_counts = defaultdict(int)
        for task in st.session_state.completed_tasks:
            completed_date = task["completed_at"].split(" ")[0]  # Get just the date part
            daily_counts[completed_date] += 1
        
        # Generate last 12 weeks of dates
        today = dt.now()
        weeks_ago = today - timedelta(days=84)  # 12 weeks
        
        # Create a list of all dates in range
        date_range = []
        current_date = weeks_ago
        while current_date <= today:
            date_range.append(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
        
        # Prepare data for heatmap
        activity_data = []
        for date_str in date_range:
            count = daily_counts.get(date_str, 0)
            date_obj = dt.strptime(date_str, "%Y-%m-%d")
            activity_data.append({
                "Date": date_str,
                "Day": date_obj.strftime("%a"),
                "Week": date_obj.strftime("%W"),
                "Count": count
            })
        
        df_activity = pd.DataFrame(activity_data)
        
        # Create pivot table for heatmap
        pivot_data = df_activity.pivot_table(
            index="Day",
            columns="Week",
            values="Count",
            fill_value=0
        )
        
        # Reorder days of week
        day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        pivot_data = pivot_data.reindex(day_order)
        
        # Create custom HTML heatmap
        max_count = df_activity["Count"].max()
        
        heatmap_html = '<div style="overflow-x: auto;"><table style="border-collapse: separate; border-spacing: 3px;">'
        heatmap_html += '<tr><td style="width: 30px;"></td>'
        
        # Add week labels (only show some)
        week_labels = pivot_data.columns.tolist()
        for i, week in enumerate(week_labels):
            if i % 2 == 0:  # Show every other week
                heatmap_html += f'<td style="text-align: center; font-size: 0.7em; color: #666;">{week}</td>'
            else:
                heatmap_html += '<td></td>'
        heatmap_html += '</tr>'
        
        # Add rows for each day
        for day in day_order:
            heatmap_html += f'<tr><td style="font-size: 0.8em; color: #666; text-align: right; padding-right: 5px;">{day}</td>'
            
            if day in pivot_data.index:
                for week in pivot_data.columns:
                    count = pivot_data.loc[day, week]
                    
                    # Determine color intensity
                    if count == 0:
                        color = "#ebedf0"
                    elif count <= max_count * 0.25:
                        color = "#9be9a8"
                    elif count <= max_count * 0.5:
                        color = "#40c463"
                    elif count <= max_count * 0.75:
                        color = "#30a14e"
                    else:
                        color = "#216e39"
                    
                    heatmap_html += f'<td style="width: 12px; height: 12px; background-color: {color}; border-radius: 2px;" title="{int(count)} tasks"></td>'
            
            heatmap_html += '</tr>'
        
        heatmap_html += '</table></div>'
        
        # Display heatmap
        st.markdown(heatmap_html, unsafe_allow_html=True)
        
        # Legend
        st.markdown(
            """
            <div style="margin-top: 10px; font-size: 0.8em; color: #666;">
                <span style="margin-right: 10px;">Less</span>
                <span style="display: inline-block; width: 12px; height: 12px; background-color: #ebedf0; border-radius: 2px; margin: 0 2px;"></span>
                <span style="display: inline-block; width: 12px; height: 12px; background-color: #9be9a8; border-radius: 2px; margin: 0 2px;"></span>
                <span style="display: inline-block; width: 12px; height: 12px; background-color: #40c463; border-radius: 2px; margin: 0 2px;"></span>
                <span style="display: inline-block; width: 12px; height: 12px; background-color: #30a14e; border-radius: 2px; margin: 0 2px;"></span>
                <span style="display: inline-block; width: 12px; height: 12px; background-color: #216e39; border-radius: 2px; margin: 0 2px;"></span>
                <span style="margin-left: 5px;">More</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        
        # Display completed tasks as styled cards
        st.subheader("All Completed Tasks")
        
        for idx, task in enumerate(reversed(st.session_state.completed_tasks)):
            task_name = task.get("name", task.get("text", "Untitled"))
            task_desc = task.get("description", "")
            task_labels = task.get("labels", [])
            category_label = category_labels.get(task["category"], task["category"])
            
            # Get category color
            category_colors = {
                "Urgent & Important": "#ff4b4b",
                "Not Urgent & Important": "#4b7bff",
                "Urgent & Not Important": "#ffa500",
                "Not Urgent & Not Important": "#808080"
            }
            category_color = category_colors.get(category_label, "#808080")
            
            # Create styled card for completed task
            task_html = f"""
            <div style="background-color: #f0f2f6; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid {category_color};">
                <div style="font-size: 1.1em; font-weight: 600; color: #262730; margin-bottom: 5px;">
                    {task_name}
                </div>
                <div style="font-size: 0.85em; color: #666; margin-bottom: 5px;">
                    {task_desc if task_desc else '<em>No description</em>'}
                </div>
                <div style="font-size: 0.75em; color: #888;">
                    <strong>Category:</strong> {category_label} | <strong>Created:</strong> {task['created_at']} | <strong>Completed:</strong> {task['completed_at']}
                </div>
            """
            
            # Add labels if they exist
            if task_labels:
                task_html += '<div style="margin-top: 5px;">'
                for label in task_labels:
                    label_color = get_label_color(label)
                    task_html += f'<span style="background-color: {label_color}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.7em; margin-right: 4px; display: inline-block;">{label}</span>'
                task_html += '</div>'
            
            task_html += """
            </div>
            """
            
            st.markdown(task_html, unsafe_allow_html=True)
            
            # Delete button
            if st.button("🗑️ Delete", key=f"delete_completed_{task['id']}", use_container_width=False):
                delete_completed_task(task["id"])
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
    else:
        st.info("No completed tasks yet. Complete tasks from the Active Tasks tab to see them here.")

# Tab 3: Statistics Dashboard
with tab3:
    st.header("📊 Statistics Dashboard")
    
    # Calculate statistics
    from datetime import datetime as dt, timedelta
    from collections import defaultdict
    
    # Count active tasks
    total_active = sum(len(tasks) for tasks in st.session_state.tasks.values())
    total_completed = len(st.session_state.completed_tasks)
    total_all_time = total_active + total_completed
    
    # Category labels
    category_labels = {
        "urgent_important": "Urgent & Important",
        "not_urgent_important": "Not Urgent & Important",
        "urgent_not_important": "Urgent & Not Important",
        "not_urgent_not_important": "Not Urgent & Not Important"
    }
    
    # Overview metrics
    st.subheader("📈 Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Tasks", total_active)
    with col2:
        st.metric("Completed Tasks", total_completed)
    with col3:
        st.metric("Total Tasks", total_all_time)
    with col4:
        completion_rate = (total_completed / total_all_time * 100) if total_all_time > 0 else 0
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    st.markdown("---")
    
    # Tasks by Category
    st.subheader("📊 Tasks by Category")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Active Tasks by Category**")
        for cat_key, cat_label in category_labels.items():
            count = len(st.session_state.tasks[cat_key])
            percentage = (count / total_active * 100) if total_active > 0 else 0
            st.markdown(f"**{cat_label}:** {count} ({percentage:.1f}%)")
    
    with col2:
        st.markdown("**Completed Tasks by Category**")
        completed_by_cat = defaultdict(int)
        for task in st.session_state.completed_tasks:
            completed_by_cat[task["category"]] += 1
        
        for cat_key, cat_label in category_labels.items():
            count = completed_by_cat[cat_key]
            percentage = (count / total_completed * 100) if total_completed > 0 else 0
            st.markdown(f"**{cat_label}:** {count} ({percentage:.1f}%)")
    
    st.markdown("---")
    
    # Due Date Statistics
    st.subheader("📅 Due Date Analysis")
    
    overdue_count = 0
    due_soon_count = 0  # Due in next 3 days
    due_later_count = 0
    no_due_date_count = 0
    
    for category_tasks in st.session_state.tasks.values():
        for task in category_tasks:
            due_date = task.get("due_date")
            if not due_date:
                no_due_date_count += 1
            elif is_overdue(due_date):
                overdue_count += 1
            else:
                days_left = days_until_due(due_date)
                if days_left is not None and days_left <= 3:
                    due_soon_count += 1
                else:
                    due_later_count += 1
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("⚠️ Overdue", overdue_count)
    with col2:
        st.metric("⏰ Due Soon (3 days)", due_soon_count)
    with col3:
        st.metric("📅 Due Later", due_later_count)
    with col4:
        st.metric("➖ No Due Date", no_due_date_count)
    
    st.markdown("---")
    
    # Time to Complete Statistics
    if st.session_state.completed_tasks:
        st.subheader("⏱️ Time to Complete")
        
        completion_times = []
        for task in st.session_state.completed_tasks:
            try:
                created = dt.strptime(task["created_at"], "%Y-%m-%d %H:%M:%S")
                completed = dt.strptime(task["completed_at"], "%Y-%m-%d %H:%M:%S")
                days_to_complete = (completed - created).days
                completion_times.append({
                    "category": task["category"],
                    "days": days_to_complete
                })
            except:
                pass
        
        if completion_times:
            # Overall average
            avg_days = sum(t["days"] for t in completion_times) / len(completion_times)
            
            # By category
            cat_times = defaultdict(list)
            for ct in completion_times:
                cat_times[ct["category"]].append(ct["days"])
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Average Days to Complete", f"{avg_days:.1f}")
            
            with col2:
                st.markdown("**By Category:**")
                for cat_key, cat_label in category_labels.items():
                    if cat_key in cat_times:
                        cat_avg = sum(cat_times[cat_key]) / len(cat_times[cat_key])
                        st.markdown(f"**{cat_label}:** {cat_avg:.1f} days")
    
    st.markdown("---")
    
    # Productivity Trends
    st.subheader("📈 Productivity Trends")
    
    if st.session_state.completed_tasks:
        # Tasks completed per week (last 12 weeks)
        weekly_counts = defaultdict(int)
        today = dt.now()
        
        for task in st.session_state.completed_tasks:
            try:
                completed_date = dt.strptime(task["completed_at"].split(" ")[0], "%Y-%m-%d")
                week_num = completed_date.strftime("%Y-W%W")
                weekly_counts[week_num] += 1
            except:
                pass
        
        # Get last 12 weeks
        weeks = []
        for i in range(11, -1, -1):
            week_date = today - timedelta(weeks=i)
            week_num = week_date.strftime("%Y-W%W")
            weeks.append({
                "Week": week_date.strftime("W%W"),
                "Count": weekly_counts.get(week_num, 0)
            })
        
        # Create simple bar chart using text
        st.markdown("**Tasks Completed per Week (Last 12 Weeks)**")
        max_count = max(w["Count"] for w in weeks) if weeks else 1
        
        for week in weeks:
            bar_length = int((week["Count"] / max_count * 30)) if max_count > 0 else 0
            bar = "█" * bar_length
            st.markdown(f"`{week['Week']}` {bar} {week['Count']}")
        
        # Best and worst weeks
        if weeks:
            best_week = max(weeks, key=lambda x: x["Count"])
            worst_week = min(weeks, key=lambda x: x["Count"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🏆 Best Week", f"{best_week['Count']} tasks")
            with col2:
                st.metric("📉 Slowest Week", f"{worst_week['Count']} tasks")
    else:
        st.info("Complete some tasks to see productivity trends!")
    
    st.markdown("---")
    
    # Task Distribution
    st.subheader("🎯 Current Task Distribution")
    
    if total_active > 0:
        st.markdown("**Distribution Across Categories:**")
        
        for cat_key, cat_label in category_labels.items():
            count = len(st.session_state.tasks[cat_key])
            percentage = (count / total_active * 100) if total_active > 0 else 0
            bar_length = int(percentage / 2)  # Scale to 50 chars max
            bar = "▓" * bar_length
            st.markdown(f"`{cat_label:30}` {bar} {count} ({percentage:.1f}%)")
        
        # Recommendations based on distribution
        st.markdown("---")
        st.subheader("💡 Recommendations")
        
        urgent_important = len(st.session_state.tasks["urgent_important"])
        not_urgent_important = len(st.session_state.tasks["not_urgent_important"])
        urgent_not_important = len(st.session_state.tasks["urgent_not_important"])
        
        if urgent_important > total_active * 0.4:
            st.warning("⚠️ You have many urgent & important tasks. Focus on completing these first!")
        
        if not_urgent_important > total_active * 0.5:
            st.info("📅 Good job planning ahead! You have many important tasks scheduled.")
        
        if urgent_not_important > total_active * 0.3:
            st.warning("↔️ Consider delegating some urgent but not important tasks.")
        
        if overdue_count > 0:
            st.error(f"🚨 You have {overdue_count} overdue task(s). Address these immediately!")
    else:
        st.info("Add some tasks to see distribution analysis!")