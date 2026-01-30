import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

def create_schema():
    conn = sqlite3.connect('football.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS seasons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        start_date TEXT,
        end_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        stadium TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        position TEXT,
        FOREIGN KEY(team_id) REFERENCES teams(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        season_id INTEGER,
        home_team_id INTEGER,
        away_team_id INTEGER,
        round INTEGER,
        match_date TEXT,
        home_score INTEGER,
        away_score INTEGER,
        FOREIGN KEY(season_id) REFERENCES seasons(id),
        FOREIGN KEY(home_team_id) REFERENCES teams(id),
        FOREIGN KEY(away_team_id) REFERENCES teams(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS match_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player_id INTEGER,
        event_type TEXT,
        minute INTEGER,
        FOREIGN KEY(match_id) REFERENCES matches(id),
        FOREIGN KEY(player_id) REFERENCES players(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        old_score TEXT,
        new_score TEXT,
        change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''
    CREATE TRIGGER IF NOT EXISTS log_score_change
    AFTER UPDATE OF home_score, away_score ON matches
    BEGIN
        INSERT INTO audit_logs (match_id, old_score, new_score)
        VALUES (
            OLD.id,
            OLD.home_score || ':' || OLD.away_score,
            NEW.home_score || ':' || NEW.away_score
        );
    END;
    ''')
    print("Generowanie danych...")

    admin_pass = hashlib.sha256('adminpass'.encode()).hexdigest()
    user_pass = hashlib.sha256('user123'.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", ('admin', admin_pass, 'admin'))
        c.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", ('kibic', user_pass, 'user'))
    except sqlite3.IntegrityError:
        pass


    seasons = [
        ('2016/2017', '2016-08-01', '2017-06-03'),
        ('2017/2018', '2017-08-01', '2018-05-26'),
        ('2018/2019', '2018-08-01', '2019-06-01'),
        ('2019/2020', '2019-08-01', '2020-08-23'),
        ('2020/2021', '2020-09-12', '2021-05-29'),
        ('2021/2022', '2021-08-13', '2022-05-28'),
        ('2022/2023', '2022-08-05', '2023-06-10'),
        ('2023/2024', '2023-08-11', '2024-06-01'),
        ('2024/2025', '2024-08-16', '2025-05-31'),
    ]
    c.executemany("INSERT INTO seasons (name, start_date, end_date) VALUES (?, ?, ?)", seasons)

    teams = [
        ('Real Madryt', 'Madryt', 'Santiago Bernabéu'),
        ('FC Barcelona', 'Barcelona', 'Camp Nou'),           
        ('Bayern Monachium', 'Monachium', 'Allianz Arena'),   
        ('Borussia Dortmund', 'Dortmund', 'Signal Iduna Park'),
        ('Manchester City', 'Manchester', 'Etihad Stadium'),  
        ('Liverpool FC', 'Liverpool', 'Anfield'),             
        ('Arsenal FC', 'Londyn', 'Emirates Stadium'),         
        ('Chelsea FC', 'Londyn', 'Stamford Bridge'),          
        ('Paris Saint-Germain', 'Paryż', 'Parc des Princes'), 
        ('Juventus FC', 'Turyn', 'Allianz Stadium'),          
        ('AC Milan', 'Mediolan', 'San Siro'),                 
        ('Inter Mediolan', 'Mediolan', 'San Siro')           
    ]
    c.executemany("INSERT INTO teams (name, city, stadium) VALUES (?, ?, ?)", teams)

    players_raw = {
        1: [('Cristiano', 'Ronaldo', 'Napastnik'), ('Karim', 'Benzema', 'Napastnik'), ('Luka', 'Modrić', 'Pomocnik')],
        2: [('Lionel', 'Messi', 'Napastnik'), ('Luis', 'Suárez', 'Napastnik'), ('Neymar', 'Junior', 'Napastnik')],
        3: [('Robert', 'Lewandowski', 'Napastnik'), ('Thomas', 'Müller', 'Pomocnik'), ('Manuel', 'Neuer', 'Bramkarz')],
        4: [('Marco', 'Reus', 'Pomocnik'), ('Erling', 'Haaland', 'Napastnik'), ('Mats', 'Hummels', 'Obrońca')],
        5: [('Kevin', 'De Bruyne', 'Pomocnik'), ('Sergio', 'Agüero', 'Napastnik'), ('Phil', 'Foden', 'Pomocnik')],
        6: [('Mohamed', 'Salah', 'Napastnik'), ('Virgil', 'van Dijk', 'Obrońca'), ('Sadio', 'Mané', 'Napastnik')],
        7: [('Bukayo', 'Saka', 'Pomocnik'), ('Martin', 'Ødegaard', 'Pomocnik'), ('Thierry', 'Henry', 'Legenda')],
        8: [('Eden', 'Hazard', 'Pomocnik'), ('Didier', 'Drogba', 'Napastnik'), ('Cole', 'Palmer', 'Pomocnik')],
        9: [('Kylian', 'Mbappé', 'Napastnik'), ('Zlatan', 'Ibrahimović', 'Napastnik'), ('Angel', 'Di Maria', 'Pomocnik')],
        10: [('Alessandro', 'Del Piero', 'Napastnik'), ('Paulo', 'Dybala', 'Napastnik'), ('Giorgio', 'Chiellini', 'Obrońca')],
        11: [('Zlatan', 'Ibrahimović', 'Napastnik'), ('Rafael', 'Leão', 'Napastnik'), ('Paolo', 'Maldini', 'Legenda')],
        12: [('Lautaro', 'Martínez', 'Napastnik'), ('Romelu', 'Lukaku', 'Napastnik'), ('Javier', 'Zanetti', 'Legenda')]
    }

    players_list = []
    for t_id, p_list in players_raw.items():
        for p in p_list:
            players_list.append((t_id, p[0], p[1], p[2]))
    
    c.executemany("INSERT INTO players (team_id, first_name, last_name, position) VALUES (?, ?, ?, ?)", players_list)
    match_id_counter = 1
    for season_idx, season in enumerate(seasons, start=1):
        s_start = datetime.strptime(season[1], "%Y-%m-%d")
        s_end = datetime.strptime(season[2], "%Y-%m-%d")
        days_range = (s_end - s_start).days

        used_pairs = set()
        for _ in range(12):

            home_id = random.randint(1, 12)
            away_id = random.randint(1, 12)
            while home_id == away_id or (home_id, away_id) in used_pairs:
                home_id = random.randint(1, 12)
                away_id = random.randint(1, 12)
            used_pairs.add((home_id, away_id))

            random_days = random.randint(0, days_range)
            m_date = (s_start + timedelta(days=random_days)).strftime("%Y-%m-%d")

            h_score = random.randint(0, 5)
            a_score = random.randint(0, 4)

            c.execute('''INSERT INTO matches (season_id, home_team_id, away_team_id, round, match_date, home_score, away_score) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                         (season_idx, home_id, away_id, random.randint(1, 30), m_date, h_score, a_score))
            home_players = [p[0] for p in players_raw[home_id]] 

            c.execute("SELECT id FROM players WHERE team_id = ?", (home_id,))
            hp_ids = [row[0] for row in c.fetchall()]
            
            c.execute("SELECT id FROM players WHERE team_id = ?", (away_id,))
            ap_ids = [row[0] for row in c.fetchall()]
            
            for _ in range(h_score):
                if hp_ids:
                    scorer = random.choice(hp_ids)
                    minute = random.randint(1, 90)
                    c.execute("INSERT INTO match_events (match_id, player_id, event_type, minute) VALUES (?, ?, 'goal', ?)",
                              (match_id_counter, scorer, minute))
            
            for _ in range(a_score):
                if ap_ids:
                    scorer = random.choice(ap_ids)
                    minute = random.randint(1, 90)
                    c.execute("INSERT INTO match_events (match_id, player_id, event_type, minute) VALUES (?, ?, 'goal', ?)",
                              (match_id_counter, scorer, minute))

            match_id_counter += 1

    conn.commit()
    conn.close()
    print(f"Sukces! Baza danych została utworzona.")
    print(f"Wygenerowano {match_id_counter-1} meczów w 9 sezonach.")
    print(f"Dodano 12 drużyn i {len(players_list)} piłkarzy.")

if __name__ == '__main__':
    create_schema()