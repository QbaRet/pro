import sqlite3
import hashlib
DB_NAME = 'football.db'
def get_db_connection():
    return sqlite3.connect(DB_NAME)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
def verify_password(stored_hash, password):
    return stored_hash == hash_password(password)
def login(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, role, password_hash FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row and verify_password(row[2], password):
        return (row[0], row[1])
    return None
def register_user(username, password, role='user'):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        pwd_hash = hash_password(password)
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",(username, pwd_hash, role))
        conn.commit()
        return True, "Zarejestrowano pomyślnie!"
    except sqlite3.IntegrityError:
        return False, "Błąd: Taki użytkownik już istnieje."
    except Exception as e:
        return False, f"Błąd bazy danych: {e}"
    finally:
        conn.close()
def get_match_details(match_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT t1.name, t2.name, m.home_score, m.away_score, m.match_date
                 FROM matches m
                 JOIN teams t1 ON m.home_team_id = t1.id
                 JOIN teams t2 ON m.away_team_id = t2.id
                 WHERE m.id = ?''', (match_id,))
    match_info = c.fetchone()
    
    if not match_info:
        conn.close()
        return None
    c.execute('''SELECT p.last_name, me.minute, t.name, me.event_type
                 FROM match_events me
                 JOIN players p ON me.player_id = p.id
                 JOIN teams t ON p.team_id = t.id
                 WHERE me.match_id = ?
                 ORDER BY me.minute ASC''', (match_id,))
    events = c.fetchall()
    conn.close()
    
    return {'info': match_info, 'events': events}
def search_matches_by_team(team_name):
    conn = get_db_connection()
    c = conn.cursor()
    search_term = f"%{team_name}%"
    c.execute('''SELECT m.id, t1.name, t2.name, m.home_score, m.away_score, m.match_date
                 FROM matches m
                 JOIN teams t1 ON m.home_team_id = t1.id
                 JOIN teams t2 ON m.away_team_id = t2.id
                 WHERE t1.name LIKE ? OR t2.name LIKE ?
                 ORDER BY m.match_date DESC
                 LIMIT 20''', (search_term, search_term))
    results = c.fetchall()
    conn.close()
    return results
def get_matches_by_season(season_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT m.id, t1.name AS home_team, t2.name AS away_team, m.round, m.match_date, m.home_score, m.away_score
                 FROM matches m
                 JOIN teams t1 ON m.home_team_id = t1.id
                 JOIN teams t2 ON m.away_team_id = t2.id
                 WHERE m.season_id = ?''', (season_id,))
    matches = c.fetchall()
    conn.close()
    return matches
def get_season_standings(season_id):
    matches = get_matches_by_season(season_id)
    # Słownik: { 'Real Madryt': {'m': 0, 'w': 0, 'd': 0, 'l': 0, 'pts': 0, 'gz': 0, 'gs': 0} }
    table = {}
    
    def init_team(name):
        if name not in table:
            table[name] = {'m': 0, 'w': 0, 'd': 0, 'l': 0, 'pts': 0, 'gz': 0, 'gs': 0}

    for m in matches:
        h_team, a_team = m[1], m[2]
        h_score, a_score = m[5], m[6]
        if h_score is None: continue
        
        init_team(h_team)
        init_team(a_team)

        table[h_team]['m'] += 1
        table[a_team]['m'] += 1
        table[h_team]['gz'] += h_score
        table[h_team]['gs'] += a_score
        table[a_team]['gz'] += a_score
        table[a_team]['gs'] += h_score
        if h_score > a_score: 
            table[h_team]['pts'] += 3
            table[h_team]['w'] += 1
            table[a_team]['l'] += 1
        elif a_score > h_score: 
            table[a_team]['pts'] += 3
            table[a_team]['w'] += 1
            table[h_team]['l'] += 1
        else: 
            table[h_team]['pts'] += 1
            table[a_team]['pts'] += 1
            table[h_team]['d'] += 1
            table[a_team]['d'] += 1

    sorted_table = sorted(table.items(), key=lambda x: (x[1]['pts'], x[1]['gz']-x[1]['gs']), reverse=True)
    return sorted_table
def get_team_players(team_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT first_name, last_name, position
                 FROM players
                 WHERE team_id = ?''', (team_id,))
    players = c.fetchall()
    conn.close()
    return players
def get_match_events(match_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT p.first_name, p.last_name, me.event_type, me.minute
                 FROM match_events me
                 JOIN players p ON me.player_id = p.id
                 WHERE me.match_id = ?''', (match_id,))
    events = c.fetchall()
    conn.close()
    return events
def log_score_change(match_id, old_score, new_score):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO audit_logs (match_id, old_score, new_score)
                 VALUES (?, ?, ?)''', (match_id, old_score, new_score))
    conn.commit()
    conn.close()
def add_match_results(match_id, h_score, a_score, scorers_list):
    conn = get_db_connection()
    try:
        c= conn.cursor()
        c.execute('''UPDATE matches
                     SET home_score = ?, away_score = ?
                     WHERE id = ?''', (h_score, a_score, match_id))
        for player_id, minute in scorers_list:
            c.execute('''INSERT INTO match_events (match_id, player_id, event_type, minute)
                         VALUES (?, ?, 'goal', ?)''', (match_id, player_id, minute))
        conn.commit()
        print("Wynik i strzelcy dodani pomyslnie")
    except Exception as e:
        conn.rollback()
        print("Blad podczas dodawania wyniku i strzelcow:", e)
    finally:
        conn.close()
def add_team(name, city, stadium):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO teams (name, city, stadium) VALUES (?, ?, ?)", (name, city, stadium))
        conn.commit()
        return True, f"Dodano drużynę: {name}"
    except Exception as e:
        return False, f"Błąd: {e}"
    finally:
        conn.close()

def add_player(team_id, first_name, last_name, position):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("INSERT INTO players (team_id, first_name, last_name, position) VALUES (?, ?, ?, ?)", 
                  (team_id, first_name, last_name, position))
        conn.commit()
        return True, f"Dodano piłkarza: {last_name}"
    except Exception as e:
        return False, f"Błąd: {e}"
    finally:
        conn.close()

def delete_match(match_id):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("DELETE FROM match_events WHERE match_id = ?", (match_id,))
        c.execute("DELETE FROM matches WHERE id = ?", (match_id,))
        
        if c.rowcount > 0:
            conn.commit()
            return True, "Mecz został usunięty."
        else:
            return False, "Nie znaleziono meczu o takim ID."
    except Exception as e:
        conn.rollback()
        return False, f"Błąd usuwania: {e}"
    finally:
        conn.close()

def delete_player(player_id):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("DELETE FROM players WHERE id = ?", (player_id,))
        if c.rowcount > 0:
            conn.commit()
            return True, "Zawodnik usunięty."
        else:
            return False, "Nie znaleziono zawodnika."
    except Exception as e:
        return False, f"Błąd (może zawodnik ma przypisane gole?): {e}"
    finally:
        conn.close()