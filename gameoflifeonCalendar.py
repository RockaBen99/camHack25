
import pickle, os, datetime, math
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time

SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'
TOKEN_PICKLE = 'token.pickle'
CALENDAR_SUMMARY = 'Life'   # name for your dedicated calendar

# Config: 7 columns (days), 7 rows (hours)
COLUMNS = 7
ROWS = 7
BASE_HOUR = 9              # earliest hour shown (9:00)
SLOT_MINUTES = 60          # event duration
WEEK_START = 0             # 0 = Monday (ISO weekday-1)

def auth():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as f: creds = pickle.load(f)
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE, 'wb') as f: pickle.dump(creds, f)
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_or_create_calendar(service):
    # find by summary or create new
    cal_list = service.calendarList().list().execute()
    for c in cal_list.get('items', []):
        if c.get('summary') == CALENDAR_SUMMARY:
            return c['id']
    new_cal = {
        'summary': CALENDAR_SUMMARY,
        'timeZone': 'Europe/London'
    }
    created = service.calendars().insert(body=new_cal).execute()
    return created['id']

def week_interval_for(base_date):
    # return monday start and sunday end for the week containing base_date
    # base_date: datetime.date
    iso = base_date.isoweekday()  # 1..7
    monday = base_date - datetime.timedelta(days=(iso-1))
    start_dt = datetime.datetime.combine(monday, datetime.time(hour=0, minute=0, tzinfo=datetime.timezone.utc))
    end_dt = start_dt + datetime.timedelta(days=7)
    return start_dt.isoformat(), end_dt.isoformat()

def fetch_events(service, cal_id, start_iso, end_iso):
    events = []
    page_token = None
    while True:
        resp = service.events().list(calendarId=cal_id, timeMin=start_iso, timeMax=end_iso,
                                     singleEvents=True, orderBy='startTime', pageToken=page_token).execute()
        events += resp.get('items', [])
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return events

def parse_grid_from_events(events, base_monday_date):
    grid = [[False]*COLUMNS for _ in range(ROWS)]
    for e in events:
        # We use event.start.dateTime mapped to cell; event title should contain "Life" but not required
        st = e.get('start', {}).get('dateTime')
        if not st:
            continue
        dt = datetime.datetime.fromisoformat(st.replace('Z', '+00:00')).astimezone(datetime.timezone(datetime.timedelta(hours=0)))
        # compute column (day offset) and row (hour offset)
        day_offset = (dt.date() - base_monday_date).days
        hour_offset = dt.hour - BASE_HOUR
        if 0 <= day_offset < COLUMNS and 0 <= hour_offset < ROWS:
            grid[hour_offset][day_offset] = True
    return grid

def next_generation(grid):
    R, C = len(grid), len(grid[0])
    new = [[False]*C for _ in range(R)]
    for r in range(R):
        for c in range(C):
            alive = grid[r][c]
            neighbors = 0
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==0 and dc==0: continue
                    rr, cc = r+dr, c+dc
                    if 0 <= rr < R and 0 <= cc < C and grid[rr][cc]:
                        neighbors += 1
            if alive and neighbors in (2, 3):
                new[r][c] = True
            elif alive and (neighbors < 2 or neighbors > 3):
                new[r][c] = False
            elif (not alive) and neighbors == 3:
                new[r][c] = True
    return new

def clear_life_events(service, cal_id, start_iso, end_iso):
    events = fetch_events(service, cal_id, start_iso, end_iso)
    for e in events:
        # optionally filter by summary prefix if you share the calendar
        if e.get('summary','').startswith('Life:'):
            try:
                service.events().delete(calendarId=cal_id, eventId=e['id']).execute()
            except Exception as exc:
                print('Delete failed', exc)

def create_events_from_grid(service, cal_id, base_monday_date, grid):
    for r in range(ROWS):
        for c in range(COLUMNS):
            if not grid[r][c]:
                continue
            start_date = base_monday_date + datetime.timedelta(days=c)
            start_dt = datetime.datetime.combine(start_date, datetime.time(hour=BASE_HOUR + r, minute=0))
            end_dt = start_dt + datetime.timedelta(minutes=SLOT_MINUTES)
            # Use timezone Europe/London
            tz = 'Europe/London'
            event = {
                'summary': f'Life: {r},{c}',
                'start': {'dateTime': start_dt.isoformat(), 'timeZone': tz},
                'end': {'dateTime': end_dt.isoformat(), 'timeZone': tz},
            }
            service.events().insert(calendarId=cal_id, body=event).execute()

def run_once(base_date=None):
    service = auth()
    cal_id = get_or_create_calendar(service)
    if base_date is None: base_date = datetime.date.today()
    # Get monday for the week we will use as columns
    while True:
        time.sleep(15)
        iso = base_date.isoweekday()
        monday = base_date - datetime.timedelta(days=(iso-1))
        start_iso, end_iso = week_interval_for(base_date)
        events = fetch_events(service, cal_id, start_iso, end_iso)
        grid = parse_grid_from_events(events, monday)
        print('Current grid:')
        for row in grid: print(''.join(['#' if x else '.' for x in row]))
        new_grid = next_generation(grid)
        clear_life_events(service, cal_id, start_iso, end_iso)
        create_events_from_grid(service, cal_id, monday, new_grid)
        print('Next grid written.')

if __name__ == '__main__':
        run_once()