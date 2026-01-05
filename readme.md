# Eisenhower Matrix Task Manager

A task management application based on the Eisenhower Matrix, built with Streamlit and designed for deployment on Posit Connect.

## Features

- **Four Quadrants**: Organize tasks by urgency and importance
  - Urgent & Important (Do First)
  - Not Urgent & Important (Schedule)
  - Urgent & Not Important (Delegate)
  - Not Urgent & Not Important (Eliminate)

- **Persistent Storage**: Tasks are saved to a JSON file and persist between sessions
- **Task Management**: Add, complete, and delete tasks
- **Completion History**: View recently completed tasks in the sidebar
- **Posit Connect Compatible**: Ready for deployment on Posit Connect

## Local Development

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run eisenhower_matrix_app.py
```

3. Open your browser to `http://localhost:8501`

## Deployment on Posit Connect

### Option 1: Using rsconnect-python

1. Install rsconnect-python:
```bash
pip install rsconnect-python
```

2. Deploy to Posit Connect:
```bash
rsconnect deploy streamlit \
    --server <your-posit-connect-url> \
    --api-key <your-api-key> \
    eisenhower_matrix_app.py
```

### Option 2: Using the Posit Connect UI

1. Log in to your Posit Connect instance
2. Click "Publish" > "Upload Application"
3. Upload `eisenhower_matrix_app.py` and `requirements.txt`
4. Configure the application settings as needed
5. Click "Deploy"

## Data Storage

Tasks are stored in `tasks_data.json` in the application directory. This file contains:
- Active tasks in each quadrant
- Completed tasks history

The JSON file is automatically created and updated as you use the application.

## Usage

1. **Add Tasks**: Enter task description in the input field and click "Add Task"
2. **Complete Tasks**: Click the checkmark (✓) button to mark a task as complete
3. **Delete Tasks**: Click the trash (🗑️) button to delete a task
4. **View Completed**: Check the sidebar to see recently completed tasks
5. **Clear History**: Use the "Clear Completed Tasks" button in the sidebar to reset history

## Future Enhancements

Potential features to add:
- Export tasks to CSV/Excel
- Import tasks from files
- Task due dates and reminders
- Task notes and descriptions
- Search and filter functionality
- Task statistics and analytics
- User authentication for multi-user deployments

## File Structure

```
.
├── eisenhower_matrix_app.py   # Main application file
├── requirements.txt            # Python dependencies
├── tasks_data.json            # Task storage (auto-generated)
└── README.md                  # This file
```

## Troubleshooting

**Tasks not persisting?**
- Check that the application has write permissions to its directory
- Verify that `tasks_data.json` is being created

**Deployment issues on Posit Connect?**
- Ensure Python version compatibility (3.8+)
- Check that all dependencies are listed in requirements.txt
- Verify Posit Connect has necessary file system permissions

## License

This project is provided as-is for personal and commercial use.