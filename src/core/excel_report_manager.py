"""
Excel Report Manager - Single source of truth for Excel exports

Generates three sheets from JSON session data:
  - Sessions
  - Auswertung (daily evaluation with start/end, work/break totals)
  - Projekt_Analyse (monthly project/task aggregation)

Replaces legacy Excel manager variants.
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict
import os
from core.json_database import JsonDatabase, TimeSession


class ExcelReportManager:
    """Comprehensive Excel export manager"""

    def __init__(self, excel_file: str = "working_hours.xlsx"):
        self.excel_file = excel_file
        print(f"📊 ExcelReportManager initialized with: {excel_file}")

    def _file_writeable(self) -> bool:
        try:
            if not os.path.exists(self.excel_file):
                return True
            with open(self.excel_file, 'a'):
                pass
            return True
        except Exception:
            return False

    def export_all(self, json_db: JsonDatabase) -> bool:
        try:
            if not self._file_writeable():
                print("❌ Excel file locked")
                return False

            print(f"📝 Exporting {len(json_db.sessions)} sessions → {self.excel_file}")

            sessions_df = self._sessions_sheet(json_db.sessions)
            evaluation_df = self._evaluation_sheet(json_db.sessions, json_db)  # Pass json_db for work_hours
            project_df = self._project_analysis(json_db.sessions)

            with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                sessions_df.to_excel(writer, sheet_name='Sessions', index=False)
                evaluation_df.to_excel(writer, sheet_name='Auswertung', index=False)
                project_df.to_excel(writer, sheet_name='Projekt_Analyse', index=False)
                for name in ['Sessions', 'Auswertung', 'Projekt_Analyse']:
                    self._auto_fit(writer, name)

            print(f"✅ Excel export done: {len(sessions_df)} sessions | {len(evaluation_df)} days | {len(project_df)} project rows")
            return True
        except Exception as e:
            print(f"❌ Export error: {e}")
            return False

    # --- Sheet builders -------------------------------------------------
    def _sessions_sheet(self, sessions: List[TimeSession]):
        daily = self._daily_totals(sessions)
        rows = []
        for s in sessions:
            if not s.end_time:
                continue
            day_key = s.start_time.strftime('%d.%m.%Y')
            info = daily.get(day_key, {})
            first = info.get('first_id') == s.id
            dur_h = (s.end_time - s.start_time).total_seconds() / 3600
            rows.append({
                'Datum': day_key,
                'Session_Start': s.start_time.strftime('%H:%M:%S'),
                'Session_Ende': s.end_time.strftime('%H:%M:%S'),
                'Session_Dauer (h)': round(dur_h, 2),
                'Projekt': s.project,
                'Task': s.task or '',
                'Notiz': s.note or '',
                'Session_Type': s.session_type,
                'Tag_Arbeitszeit (h)': round(info.get('work', 0), 2) if first else '',
                'Tag_Pausenzeit (h)': round(info.get('break', 0), 2) if first else '',
                'Tag_Gesamtzeit (h)': round(info.get('total', 0), 2) if first else ''
            })
        import pandas as pd
        return pd.DataFrame(rows)

    def _evaluation_sheet(self, sessions: List[TimeSession], json_db: JsonDatabase):
        """Create daily evaluation with correct work_hours from config"""
        by_date = defaultdict(list)
        for s in sessions:
            if s.end_time:
                by_date[s.start_time.strftime('%d.%m.%Y')].append(s)
        
        rows = []
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for date_str in sorted(by_date.keys()):
            day_sessions = by_date[date_str]
            work = [x for x in day_sessions if x.session_type != 'break' and x.project != 'BREAK']
            brks = [x for x in day_sessions if x.session_type == 'break' or x.project == 'BREAK']
            work_h = sum((x.end_time - x.start_time).total_seconds() for x in work) / 3600
            break_h = sum((x.end_time - x.start_time).total_seconds() for x in brks) / 3600
            all_sorted = sorted(day_sessions, key=lambda x: x.start_time)
            start = all_sorted[0].start_time.strftime('%H:%M:%S')
            end = all_sorted[-1].end_time.strftime('%H:%M:%S')
            date_obj = datetime.strptime(date_str, '%d.%m.%Y').date()
            
            # GET CORRECT TARGET FROM CONFIG - NOT HARDCODED 8.0!
            weekday_name = weekdays[date_obj.weekday()]
            work_hours_config = json_db.config_data.get('work_hours', {})
            target = work_hours_config.get(weekday_name, 8.0)  # Use config or fallback to 8.0
            
            diff = work_h - target
            if work_h == 0:
                status = '⭕ No work'
            elif work_h >= target:
                status = '✅ Target reached'
            else:
                status = '❌ Below target'
            rows.append({
                'Datum': date_str,
                'Weekday': date_obj.strftime('%A'),
                'Tag_Startzeit': start,
                'Tag_Endzeit': end,
                'Arbeitszeit (h)': round(work_h, 2),
                'Pausenzeit (h)': round(break_h, 2),
                'Gesamtzeit (h)': round(work_h + break_h, 2),
                'Sollzeit (h)': target,  # Now uses correct config value
                'Differenz (h)': round(diff, 2),
                'Status': status
            })
        import pandas as pd
        return pd.DataFrame(rows)

    def _project_analysis(self, sessions: List[TimeSession]):
        agg = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {'time': 0, 'count': 0})))
        for s in sessions:
            if not s.end_time or s.session_type == 'break' or s.project == 'BREAK':
                continue
            month = s.start_time.strftime('%Y-%m')
            proj = s.project or 'General'
            task = s.task or 'No Task'
            dur_h = (s.end_time - s.start_time).total_seconds() / 3600
            agg[month][proj][task]['time'] += dur_h
            agg[month][proj][task]['count'] += 1
        rows = []
        for month in sorted(agg.keys()):
            for proj in sorted(agg[month].keys()):
                for task in sorted(agg[month][proj].keys()):
                    info = agg[month][proj][task]
                    rows.append({
                        'Monat': month,
                        'Projekt': proj,
                        'Task': task,
                        'Arbeitszeit (h)': round(info['time'], 2),
                        'Anzahl_Sessions': info['count']
                    })
        import pandas as pd
        df = pd.DataFrame(rows)
        if not df.empty:
            df = df.sort_values(['Monat', 'Arbeitszeit (h)'], ascending=[True, False])
        return df

    def _daily_totals(self, sessions: List[TimeSession]):
        daily = defaultdict(lambda: {'work': 0, 'break': 0, 'total': 0, 'first_id': None})
        bucket = defaultdict(list)
        for s in sessions:
            if s.end_time:
                key = s.start_time.strftime('%d.%m.%Y')
                bucket[key].append(s)
        for date_str, sess in bucket.items():
            sess.sort(key=lambda x: x.start_time)
            daily[date_str]['first_id'] = sess[0].id
            for s in sess:
                dur_h = (s.end_time - s.start_time).total_seconds() / 3600
                if s.session_type == 'break' or s.project == 'BREAK':
                    daily[date_str]['break'] += dur_h
                else:
                    daily[date_str]['work'] += dur_h
            daily[date_str]['total'] = daily[date_str]['work'] + daily[date_str]['break']
        return daily

    def _auto_fit(self, writer, sheet_name: str):
        try:
            ws = writer.sheets[sheet_name]
            for col in ws.columns:
                max_len = 0
                col_cells = [c for c in col]
                for c in col_cells:
                    try:
                        max_len = max(max_len, len(str(c.value)))
                    except Exception:
                        pass
                width = min((max_len + 2) * 1.2, 50)
                ws.column_dimensions[col_cells[0].column_letter].width = width
        except Exception as e:
            print(f"Column adjust failed: {e}")