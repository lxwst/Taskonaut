# 🕐 Time Tracker

A modern desktop overlay for time tracking with Excel integration and project management.

## 📋 Features

- **🎯 Desktop Overlay** - Always visible time display without intrusive windows
- **📊 Excel Integration** - Automatic saving to Excel files (.xlsx)
- **📁 Project Management** - Multiple projects with session tracking
- **⏱️ Session Management** - Start/Stop/Pause with notes per session
- **🎨 Customizable Design** - Transparency, size, font configurable
- **💾 Secure Data Storage** - Protection against data loss from multiple clicks
- **⚡ Easy Operation** - Direct clicks + right-click context menu
- **🔄 Smart Project Switching** - Recent combinations menu with auto-split sessions
- **⏰ Auto-Split Sessions** - Automatically creates separate sessions when switching projects after 5+ minutes

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python Package Manager)

### Setup
```bash
git clone https://github.com/[username]/time-tracker.git
cd time-tracker
pip install -r requirements.txt
```

### Start
```bash
python src/main.py
```

## 🎮 Usage

### Overlay Controls
- **📁 Click Project Name** → Project selection menu
- **🕐 Click Work Time** → Start/resume day
- **☕ Click Break Time** → Stop/pause session
- **⏹️ Click Status** → Edit note or start new task
- **Right Click Project Area** → Quick switch menu with recent project-task combinations

### Right-Click Quick Switch Menu
The right-click menu now shows your **recent project-task combinations** for faster switching:
- **Recent Combinations** → Shows last 10 used project-task pairs (e.g., " Daily Work")
- **Current Selection** → Marked with ✓ and disabled
- **Smart Auto-Split** → Automatically creates separate sessions when switching after 5+ minutes
- **Edit Options** → Access to project editor and session manager

### Auto-Split Sessions Feature
When switching projects via right-click:
- **If current session < 5 minutes** → Just updates project/task (no split)
- **If current session ≥ 5 minutes** → Automatically:
  1. Stops and saves current session
  2. Creates new session with selected project/task
  3. Starts the new session immediately

**Configure threshold**: Edit `"auto_split_minutes": 5` in `config.json`

### Context Menu
- 📊 Open Excel
- ⚙️ Overlay Settings
- 💾 Save Data to Excel
- 📁 Switch Project
- ⏸️ Stop Session / 💾 End Day & Save
- ❌ Exit Application

### Project Switching During Active Session
If you want to switch projects during an active session:
1. **Right-click project area** → Select from recent combinations (recommended)
2. **Left-click project name** → Full project editor dialog
3. Auto-split handles session management automatically
4. No manual session stopping needed

### Break Time vs Break Sessions
**Important**: The application handles breaks in two different ways:

**Automatic Break Time Calculation:**
- When you stop work → Break timer starts automatically
- When you resume work → Break time is calculated and added to daily totals
- This break time appears in the "Daily_Break_Time" column in Excel
- **No separate break session records are created**

**Manual Break Sessions (Optional):**
- Open Session Editor (right-click → Open Excel)
- Click "☕ Add Break" to manually log specific breaks
- These appear as separate rows with project = "BREAK"
- Useful for logging lunch breaks, meetings, etc.

**Summary:** Break time is automatically calculated, but break session records are only created when manually added through the Session Editor.

## 📊 Excel Output

### Sessions Sheet
| Date | Start | End | Duration | Project | Note | Daily_Work_Time | Daily_Break_Time | Daily_Total_Time |
|------|-------|-----|----------|---------|------|-----------------|------------------|------------------|
| 2025-08-27 | 09:00:00 | 10:30:00 | 1.50 | Project A | Meeting | 1.50 | 0.25 | 1.75 |

### Evaluation Sheet
| Date | Weekday | Work_Time | Break_Time | Total_Time | Target_Work_Time | Difference | Status |
|------|---------|-----------|------------|------------|------------------|------------|--------|
| 2025-08-27 | Tuesday | 7.50 | 0.50 | 8.00 | 8.00 | 0.00 | ✅ Target reached |

## ⚙️ Configuration

Configuration is automatically saved to `config.json`:

```json
{
  "overlay_settings": {
    "position": {"x": 100, "y": 100},
    "transparency": 0.9,
    "font_size": 10,
    "always_on_top": true
  },
  "work_settings": {
    "target_hours": 8.0,
    "auto_pause_after_minutes": 60
  },
  "projects_data": {
    "active_project": "General",
    "active_task": "Daily Work",
    "projects": {
      "General": ["Daily Work"],
      "Project A": ["Development", "Testing"],
      "Project B": ["Planning", "Meeting"]
    },
    "recent_combinations": [
      "Project A - Development",
      "General - Daily Work",
      "Project B - Meeting"
    ]
  },
  "excel_file": "working_hours.xlsx",
  "auto_split_minutes": 5
}
```

### Key Configuration Options

- **`auto_split_minutes`** - Threshold for automatic session splitting (default: 5 minutes)
- **`projects_data.recent_combinations`** - List of recent project-task pairs shown in right-click menu
- **`overlay_settings.transparency`** - Overlay transparency (0.1 = very transparent, 1.0 = opaque)
- **`work_settings.target_hours`** - Daily work hour target for progress calculation
```

## 🏗️ Architecture

```
src/
├── main.py                      # Application entry point
├── core/                        # Core logic (JSON + Export)
│   ├── json_database.py         # JSON-based primary datastore with projects_data
│   ├── excel_report_manager.py  # Single Excel export (Sessions / Auswertung / Projekt_Analyse)
│   └── config_manager.py        # Configuration management
├── gui/                         # User interface
│   ├── beautiful_clean_overlay.py # Active overlay with smart right-click menu
│   └── session_editor.py        # Session management & editing
├── utils/
│   ├── time_utils.py            # Time helpers & formatting
│   └── translations.py          # (Optional) i18n helpers
└── config.json                  # Unified configuration (projects + settings)
```

### 🆕 New Features Architecture
- **Unified Configuration**: Projects, tasks, and settings in single `config.json`
- **Smart Project Switching**: Recent combinations stored and displayed in right-click menu
- **Auto-Split Logic**: Intelligent session management based on configurable time threshold
- **Legacy Migration**: Automatic migration from old `projects.json` format

### 🧹 Legacy Removed
The old architecture with `excel_manager.py`, `enhanced_excel_manager.py`, multiple overlay variants, and separate evaluation services has been removed. All exports now run through `ExcelReportManager` → less code, consistent calculations, less risk for divergences.

**Recent Improvements:**
- ✅ Unified configuration in single `config.json` file
- ✅ Smart right-click menu with recent project-task combinations  
- ✅ Auto-split sessions for better time tracking accuracy
- ✅ Removed deprecated `excel_exporter.py` and `unified_excel_manager.py`
- ✅ Streamlined architecture with direct `ExcelReportManager` integration

## 🛠️ Building Executable

To create a standalone .exe file:

```bash
python build.py
```

The executable will be created in the `dist/` folder as `time-tracker.exe`.

## 📋 Requirements

- pandas>=1.5.0
- openpyxl>=3.1.0
- xlsxwriter>=3.0.0
- pyinstaller>=5.0.0 (for building executable)

## 🐛 Troubleshooting

### Common Issues

1. **"Excel file is locked"**
   - Close Excel before saving data
   - File will auto-retry saving

2. **Overlay not visible**
   - Check overlay settings in context menu
   - Reset position: Right-click → Settings

3. **Data not saving**
   - Check file permissions
   - Ensure Excel file is not open in another program

### Debug Mode
Run with debug output:
```bash
python src/main.py --debug
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section above
- Review the configuration options

---

**Made with ❤️ for efficient time tracking**
