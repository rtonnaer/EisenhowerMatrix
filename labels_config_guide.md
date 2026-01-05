# Labels Configuration Guide

The Eisenhower Matrix Task Manager uses a `labels_config.json` file to define available labels and their colors.

## Configuration File Structure

```json
{
  "default_labels": [
    {
      "name": "work",
      "color": "#3b82f6"
    },
    {
      "name": "personal",
      "color": "#8b5cf6"
    }
  ],
  "auto_generate_colors": true
}
```

## Configuration Options

### `default_labels` (Array)
Defines the predefined labels that appear in the label selector.

Each label object contains:
- **`name`** (string): The label name (lowercase recommended)
- **`color`** (string): Hex color code (e.g., "#3b82f6")

### `auto_generate_colors` (Boolean)
- **`true`**: Automatically generates colors for custom labels created by users
- **`false`**: Custom labels will use a default gray color (#808080)

## Default Labels Included

| Label | Color | Hex Code |
|-------|-------|----------|
| work | Blue | #3b82f6 |
| personal | Purple | #8b5cf6 |
| urgent | Red | #ef4444 |
| health | Green | #10b981 |
| finance | Orange | #f59e0b |
| family | Pink | #ec4899 |
| learning | Cyan | #06b6d4 |
| hobby | Purple | #a855f7 |
| errands | Lime | #84cc16 |
| meetings | Indigo | #6366f1 |

## Customizing Labels

### Adding New Default Labels

1. Edit `labels_config.json`
2. Add a new object to the `default_labels` array:

```json
{
  "name": "project-alpha",
  "color": "#ff6b6b"
}
```

### Changing Label Colors

Simply update the `color` value for any label:

```json
{
  "name": "work",
  "color": "#1e40af"
}
```

### Removing Default Labels

Delete the label object from the `default_labels` array.

**Note**: This won't affect existing tasks that already have the label assigned.

## Color Guidelines

### Recommended Color Formats
- Use 6-digit hex codes: `#rrggbb`
- Include the `#` symbol
- Use web-safe colors for best compatibility

### Good Color Choices
- High contrast with white text
- Distinct from other labels
- Meaningful associations (e.g., red for urgent, green for health)

### Example Color Palettes

**Professional**:
```json
"work": "#1e3a8a",
"meetings": "#6366f1",
"deadline": "#dc2626"
```

**Personal**:
```json
"family": "#ec4899",
"hobby": "#a855f7",
"social": "#06b6d4"
```

**Project-based**:
```json
"project-a": "#ef4444",
"project-b": "#3b82f6",
"project-c": "#10b981"
```

## Advanced Configuration

### Disabling Auto-Generated Colors

If you want strict control over label colors:

```json
{
  "default_labels": [...],
  "auto_generate_colors": false
}
```

With this setting, any custom label created by users will appear gray unless you add it to the config file.

### Using the Same Color for Multiple Labels

You can assign the same color to multiple labels:

```json
{
  "name": "urgent",
  "color": "#ef4444"
},
{
  "name": "critical",
  "color": "#ef4444"
}
```

## Deployment Notes

### For Posit Connect
- Place `labels_config.json` in the same directory as `eisenhower_matrix_app.py`
- The file will be read on application startup
- Changes to the config require restarting the app

### File Priority
1. Config file defines default labels and colors
2. User-created labels are saved in `tasks_data.json`
3. Colors for user-created labels are auto-generated (if enabled) or use fallback

### Troubleshooting

**Labels not appearing?**
- Check that `labels_config.json` is in the same directory as the app
- Verify JSON syntax is valid (use a JSON validator)
- Check file permissions

**Colors not showing correctly?**
- Ensure hex codes include the `#` symbol
- Use 6-digit format (not 3-digit shorthand)
- Verify the color value is a string

**Custom labels not colorful?**
- Check that `auto_generate_colors` is set to `true`
- Verify the app has write permissions to save `tasks_data.json`

## Example Configuration Files

### Minimal Setup
```json
{
  "default_labels": [
    {"name": "work", "color": "#3b82f6"},
    {"name": "personal", "color": "#8b5cf6"}
  ],
  "auto_generate_colors": true
}
```

### Comprehensive Setup
```json
{
  "default_labels": [
    {"name": "work", "color": "#3b82f6"},
    {"name": "personal", "color": "#8b5cf6"},
    {"name": "urgent", "color": "#ef4444"},
    {"name": "health", "color": "#10b981"},
    {"name": "finance", "color": "#f59e0b"},
    {"name": "family", "color": "#ec4899"},
    {"name": "learning", "color": "#06b6d4"},
    {"name": "hobby", "color": "#a855f7"},
    {"name": "errands", "color": "#84cc16"},
    {"name": "meetings", "color": "#6366f1"},
    {"name": "deadline", "color": "#dc2626"},
    {"name": "planning", "color": "#14b8a6"},
    {"name": "review", "color": "#f97316"}
  ],
  "auto_generate_colors": true
}
```

### Project-Specific
```json
{
  "default_labels": [
    {"name": "frontend", "color": "#3b82f6"},
    {"name": "backend", "color": "#10b981"},
    {"name": "database", "color": "#f59e0b"},
    {"name": "testing", "color": "#8b5cf6"},
    {"name": "documentation", "color": "#06b6d4"},
    {"name": "bug", "color": "#ef4444"},
    {"name": "feature", "color": "#84cc16"},
    {"name": "refactor", "color": "#6366f1"}
  ],
  "auto_generate_colors": true
}
```