
# Football Match Center

**Kompleksowy system do zarządzania rozgrywkami piłkarskimi**

**Autor:** Jakub Retmańczyk  
**Wersja:** 1.0 (2026)  
**Technologie:** Python 3.7+, SQLite 3.0+

---

## Spis treści

1. [Architektura i filozofia projektu](#architektura-i-filozofia-projektu)
2. [Przykładowe użycie CLI](#przykladowe-uzycie-cli)
3. [Rozbudowane scenariusze użytkownika](#rozbudowane-scenariusze-uzytkownika)
4. [Schemat bazy danych](#schemat-bazy-danych)
5. [Opis tabel](#opis-tabel)
6. [Relacje między tabelami](#relacje-miedzy-tabelami)
7. [Normalizacja bazy danych](#normalizacja-bazy-danych)
8. [Prawa dostępu](#prawa-dostepu)
9. [Trigger SQL](#trigger-sql)
10. [Transakcje i spójność](#transakcje-i-spojnosc)
11. [Bezpieczeństwo](#bezpieczenstwo)
12. [Możliwości rozbudowy i integracji](#mozliwosci-rozbudowy-i-integracji)
13. [Instrukcja uruchomienia](#instrukcja-uruchomienia)


---


## Architektura i filozofia projektu

Projekt jest prosty i nieskomplikowany. Każda funkcja CLI jest osobnym, czytelnym modułem. Dane przechowywane są w relacyjnej bazie SQLite, co zapewnia łatwość przenoszenia i brak wymagań serwerowych. System jest odporny na typowe błędy użytkownika (np. podwójne wpisy, nieprawidłowe dane) dzięki walidacji i transakcjom.

Główne założenia:
- Minimalizm interfejsu (CLI, bez zbędnych pytań)
- Bezpieczeństwo danych (hashowanie haseł, transakcje, audyt zmian)
- Możliwość łatwej rozbudowy (np. eksport do CSV, REST API, integracja z frontendem)


---


## Przykładowe użycie CLI

Poniżej kilka typowych interakcji z programem:

**Rejestracja nowego użytkownika:**
```
> python main.py
1. Rejestracja nowego konta
Podaj login: janek
Podaj hasło: haslo
Powtórz hasło: haslo
Zarejestrowano pomyślnie!
```

**Logowanie i przeglądanie meczów:**
```
> python main.py
1. Logowanie
Login: admin
Hasło: haslo
Zalogowano jako ADMIN
3. Przeglądaj mecze (wg sezonu)
Podaj ID sezonu: 9
Lista meczów:
2024-09-01 | Real Madryt 2:1 FC Barcelona
...
```

**Dodawanie wyniku i strzelców (admin):**
```
6. Panel ADMIN
1. Edytuj wynik meczu
Podaj ID meczu: 15
Gole gospodarzy: 3
Gole gości: 2
Dodać strzelca? (t/n): t
ID piłkarza: 7
Minuta: 12
...
```

**Wyszukiwanie meczów po drużynie:**
```
5. Szukaj drużyny
Wpisz nazwę: Bayern
Znalezione mecze:
2024-10-10 | Bayern 1:0 Juventus
...
```

---

---

## 3. Wymagania funkcjonalne

System realizuje operacje CRUD oraz zaawansowane filtrowanie i analizę danych.

### 3.1 Wymagania dla Administratora

| ID | Wymaganie |
|----|-----------|
| A1 | Dodawanie nowych drużyn z informacją o stadionie |
| A2 | Dodawanie piłkarzy do istniejących drużyn |
| A3 | Edycja wyników meczów i dodawanie strzelców |
| A4 | Usuwanie meczów wraz z powiązanymi zdarzeniami |
| A5 | Usuwanie piłkarzy z bazy danych |
| A6 | Dostęp do panelu administracyjnego |
| A7 | Przeglądanie wszystkich danych bez ograniczeń |

### 3.2 Wymagania dla Użytkownika/Kibica

| ID | Wymaganie |
|----|-----------|
| K1 | Samodzielna rejestracja konta |
| K2 | Logowanie do systemu z weryfikacją hasła |
| K3 | Przeglądanie listy meczów w wybranym sezonie |
| K4 | Wyświetlanie tabeli ligowej z automatycznym rankingiem |
| K5 | Wyszukiwanie meczów konkretnej drużyny |
| K6 | Przeglądanie szczegółów meczu (strzelcy, minuty bramek) |
| K7 | Przeglądanie listy zawodników drużyn |

### 3.3 Wymagania niefunkcjonalne

| ID | Wymaganie | Opis |
|----|-----------|------|
| N1 | Bezpieczeństwo haseł | Hashowanie SHA-256 |
| N2 | Ochrona przed SQL Injection | Parametryzowane zapytania SQLite |
| N3 | Transakcyjność | Atomowe operacje przy dodawaniu wyników |
| N4 | Audytowalność | Trigger logujący zmiany wyników |
| N5 | Kontrola dostępu | Dwupoziomowy system uprawnień (admin/user) |

---

## 4. Schemat bazy danych

### Diagram ERD

```
┌─────────────────┐
│     users       │ (użytkownicy)
│─────────────────│
│ id (PK)         │
│ username        │ UNIQUE
│ password_hash   │
│ role            │ CHECK('admin'/'user')
└────────┬────────┘
         │ 1:N
         ▼
┌─────────────────────────┐
│      seasons            │ (sezony)
│─────────────────────────│
│ id (PK)                 │
│ name                    │ (np. "2024/2025")
│ start_date              │
│ end_date                │
└────────┬────────────────┘
         │ 1:N
         ▼
┌──────────────────────────────┐     ┌──────────────────┐
│        matches               │────▶│      teams       │
│──────────────────────────────│     │──────────────────│
│ id (PK)                      │     │ id (PK)          │
│ season_id (FK)               │     │ name             │
│ home_team_id (FK)            │     │ city             │
│ away_team_id (FK)            │     │ stadium          │
│ round                        │     └────────┬─────────┘
│ match_date                   │            │ 1:N
│ home_score                   │            ▼
│ away_score                   │     ┌──────────────────┐
└────────┬──────────────────────┘     │     players      │
         │ 1:N                        │──────────────────│
         ▼                            │ id (PK)          │
┌─────────────────┐                   │ team_id (FK)     │
│  match_events   │                   │ first_name       │
│─────────────────│                   │ last_name        │
│ id (PK)         │                   │ position         │
│ match_id (FK)   │                   └──────────────────┘
│ player_id (FK)  │
│ event_type      │ ('goal', 'card')
│ minute          │
└─────────────────┘

┌──────────────────────────────┐
│     audit_logs               │ (tabela dla triggera)
│──────────────────────────────│
│ id (PK)                      │
│ match_id (FK)                │
│ old_score                    │ (np. "0:0")
│ new_score                    │ (np. "1:0")
│ change_date                  │ TIMESTAMP
└──────────────────────────────┘

```

---

## 5. Opis tabel i kluczy

Baza danych zawiera **7 tabel** w strukturze relacyjnej.

### 5.1 users (Użytkownicy)
| Kolumna | Typ | Opis |
|---------|-----|------|
| id | INTEGER (PK) | Klucz główny |
| username | TEXT UNIQUE | Login użytkownika |
| password_hash | TEXT | Hasło zahashowane SHA-256 |
| role | TEXT CHECK | Rola: 'admin' lub 'user' |

**Klucze:**
- **Klucz główny:** `id`
- **Klucz unikalny:** `username`
- **Ograniczenie:** `role IN ('admin', 'user')`

### 5.2 seasons (Sezony)
| Kolumna | Typ | Opis |
|---------|-----|------|
| id | INTEGER (PK) | Klucz główny |
| name | TEXT | Nazwa sezonu (np. "2024/2025") |
| start_date | TEXT | Data rozpoczęcia |
| end_date | TEXT | Data zakończenia |

**Klucze:**
- **Klucz główny:** `id`
- **Klucze obce:** brak

**Dane testowe:** 9 sezonów od 2016/17 do 2024/25

### 5.3 teams (Drużyny)
| Kolumna | Typ | Opis |
|---------|-----|------|
| id | INTEGER (PK) | Klucz główny |
| name | TEXT | Nazwa drużyny |
| city | TEXT | Miasto siedziby |
| stadium | TEXT | Nazwa stadionu |

**Klucze:**
- **Klucz główny:** `id`
- **Klucze obce:** brak

**Dane testowe:** 12 drużyn europejskich (Real Madryt, Barcelona, Bayern, etc.)

### 5.4 players (Piłkarze)
| Kolumna | Typ | Opis |
|---------|-----|------|
| id | INTEGER (PK) | Klucz główny |
| team_id | INTEGER (FK) | Drużyna zawodnika |
| first_name | TEXT | Imię |
| last_name | TEXT | Nazwisko |
| position | TEXT | Pozycja (Napastnik, Obrońca, Bramkarz, Pomocnik) |

**Klucze:**
- **Klucz główny:** `id`
- **Klucz obcy:** `team_id` → `teams(id)`

**Dane testowe:** ~36 piłkarzy (3 na drużynę)

### 5.5 matches (Mecze)
| Kolumna | Typ | Opis |
|---------|-----|------|
| id | INTEGER (PK) | Klucz główny |
| season_id | INTEGER (FK) | Sezon |
| home_team_id | INTEGER (FK) | Drużyna gospodarz |
| away_team_id | INTEGER (FK) | Drużyna gość |
| round | INTEGER | Numer rundy (1-30) |
| match_date | TEXT | Data meczu (YYYY-MM-DD) |
| home_score | INTEGER | Liczba bramek zespołu domowego |
| away_score | INTEGER | Liczba bramek zespołu gościa |

**Klucze:**
- **Klucz główny:** `id`
- **Klucze obce:** `season_id` → `seasons(id)`, `home_team_id` → `teams(id)`, `away_team_id` → `teams(id)`

**Statusy:** Brak pola statusu - wynik jest nullabilny (NULL = mecz zaplanowany, liczby = rozegrany)

**Dane testowe:** ~108 meczów (12 na sezon, 9 sezonów)

### 5.6 match_events (Zdarzenia meczowe)
| Kolumna | Typ | Opis |
|---------|-----|------|
| id | INTEGER (PK) | Klucz główny |
| match_id | INTEGER (FK) | Mecz |
| player_id | INTEGER (FK) | Zawodnik |
| event_type | TEXT | Typ zdarzenia ('goal', 'card') |
| minute | INTEGER | Minuta zdarzenia |

**Klucze:**
- **Klucz główny:** `id`
- **Klucze obce:** `match_id` → `matches(id)`, `player_id` → `players(id)`

**Uwaga:** Brak ograniczenia UNIQUE - jeden zawodnik może strzelić kilka bramek w jednym meczu

### 5.7 audit_logs (Logi zmian wyników)
| Kolumna | Typ | Opis |
|---------|-----|------|
| id | INTEGER (PK) | Klucz główny |
| match_id | INTEGER (FK) | Mecz |
| old_score | TEXT | Poprzedni wynik (np. "0:0") |
| new_score | TEXT | Nowy wynik (np. "1:0") |
| change_date | TIMESTAMP | Data i godzina zmiany |

**Klucze:**
- **Klucz główny:** `id`
- **Klucze obce:** `match_id` → `matches(id)`

**Uwaga:** Tabela zarządzana przez trigger SQL (zapisywane automatycznie)

---

## 6. Relacje między tabelami

### 6.1 Relacje jeden-do-wielu (1:N):

1. **seasons → matches**
   - Jeden sezon zawiera wiele meczów
   - Każdy mecz należy do dokładnie jednego sezonu

2. **teams → players**
   - Jedna drużyna ma wielu piłkarzy
   - Każdy piłkarz należy do dokładnie jednej drużyny

3. **teams → matches** (dwustronna)
   - Drużyna domowa: jeden do wielu meczów (w roli gospodyni)
   - Drużyna gość: jeden do wielu meczów (w roli gościa)

4. **matches → match_events**
   - Jeden mecz zawiera wiele zdarzeń (bramek, kartek)
   - Każde zdarzenie dotyczy dokładnie jednego meczu

5. **players → match_events**
   - Jeden piłkarz uczestniczy w wielu zdarzeniach
   - Każde zdarzenie dotyczy dokładnie jednego piłkarza

6. **matches → audit_logs**
   - Jeden mecz może mieć wiele wpisów w dzienniku zmian
   - Każdy wpis dotyczy dokładnie jednego meczu

---

## 7. Normalizacja bazy danych

### 7.1 Pokazanie normalizacji

Baza danych jest w **trzeciej postaci normalnej (3NF)**.

#### Pierwsza postać normalna (1NF) ✓
- Wszystkie kolumny przechowują wartości atomowe, bez możliwości dalszego podziału- Brak powtarzających się grup atrybutów
- Nie występują powtarzające się zestawy danych w obrębie jednej tabeli
- Każda tabela posiada jednoznacznie określony klucz główny

#### Druga postać normalna (2NF) ✓
- Spełnione są wymagania pierwszej postaci normalnej
- Każdy atrybut niebędący kluczem jest w pełni zależny od całego klucza głównego
- W tabelach z kluczem prostym warunek ten jest spełniony automatycznie
#### Trzecia postać normalna (3NF) ✓
- Spełnione są założenia drugiej postaci normalne
- Nie występują zależności przechodnie pomiędzy atrybutami niekluczowymi
- Przykładowo w tabeli match_events pola event_type oraz minute zależą bezpośrednio od identyfikatora rekordu, a nie od innych kolumn

### 7.2 Redundancja danych

Wszystkie dane przechowywane są w jednym miejscu, więc w aplikacji ** nie ma celowej redundancji danych **.

| Dane | Lokalizacja | Uzasadnienie |
|------|-------------|--------------|
| Wynik meczu | `matches` | Przechowywany w jednym miejscu |
| Strzelcy bramek | `match_events` | Oddzielna tabela dla zdarzeń |
| Info o drużynie | `teams` | Nie duplikuje się w innych tabelach |
| Info o zawodniku | `players` | Powiązanie przez FK do drużyny |
| Historia zmian | `audit_logs` | Automatycznie tworzone przez trigger |

---

## 8. Prawa dostępu

W systemie możliwe są dwa poziomy dostępu do aplikacji:

### 8.1 Tabela uprawnień

| Komponent | Administrator | Użytkownik |
|-----------|----------------|-----------|
| `users` | Create (rejestracja innych), Read | Read (własne dane) |
| `seasons` | Read | Read |
| `teams` | CRUD | Read |
| `players` | CRUD | Read |
| `matches` | CRUD | Read |
| `match_events` | CRUD | Read |
| `audit_logs` | Read | Brak dostępu |
| Panel administracyjny | ✓ Pełny dostęp | ✗ Brak dostępu |

### 8.2 Administrator (`role = 'admin'`)

| Uprawnienie | Dostęp |
|-------------|--------|
| Panel administracyjny | ✓ |
| Dodawanie drużyn | ✓ |
| Dodawanie piłkarzy | ✓ |
| Edycja wyników meczów | ✓ |
| Dodawanie strzelców | ✓ |
| Usuwanie meczów | ✓ |
| Usuwanie piłkarzy | ✓ |
| Przeglądanie logów audytu | ✓ |
| Rejestracja innych użytkowników | ✓ |

### 8.3 Użytkownik / Kibic (`role = 'user'`)

| Uprawnienie | Dostęp |
|-------------|--------|
| Panel administracyjny | ✗ |
| Przeglądanie meczów | ✓ |
| Przeglądanie tabeli ligowej | ✓ |
| Wyszukiwanie drużyn | ✓ |
| Podgląd strzelców | ✓ |
| Przeglądanie zawodników | ✓ |
| Modyfikacja danych | ✗ |
| Przeglądanie logów audytu | ✗ |

### 8.4 Kontrola dostępu w aplikacji

Kontrola dostępu w aplikacji:
```python
def login(username, password):
    """Logowanie z walidacją hasha hasła"""
    c.execute('SELECT id, role, password_hash FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    if row and verify_password(row[2], password):
        return (row[0], row[1])  # Zwraca (user_id, role)
    return None

# W panelu admina
if current_user and current_user[1] == 'admin':
    # Wyświetl opcje administracyjne
```

---

## 9. Trigger 

### 9.1 Cel triggera

Każda aktualizacja wyniku meczu uruchamia trigger SQL, który zapisuje poprzedni i nowy rezultat w tabeli audit_logs. Rozwiązanie to zapewnia możliwość odtworzenia historii zmian i stanowi zabezpieczenie przed manipulacją danymi

### 9.2 Implementacja triggera

```sql
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
```

### 9.3 Przykład działania

**Scenariusz:** Administratorem zmienia wynik meczu

```sql
-- Przed zmianą
SELECT * FROM matches WHERE id = 1;
-- Wynik: home_score = NULL, away_score = NULL

-- Zmiana wyniku
UPDATE matches SET home_score = 2, away_score = 1 WHERE id = 1;

-- Trigger automatycznie doda wpis:
SELECT * FROM audit_logs WHERE match_id = 1;
+---------+----------+----------+-------------------------------+
| id | match_id | old_score | new_score | change_date |
+----+----------+-----------+-----------+-------------------------------+
| 1  | 1        | NULL:NULL | 2:1       | 2026-01-30 10:30:45.123456  |
+----+----------+-----------+-----------+-------------------------------+

-- Druga zmiana
UPDATE matches SET home_score = 2, away_score = 2 WHERE id = 1;

-- Nowy wpis w logu
SELECT * FROM audit_logs WHERE match_id = 1 ORDER BY change_date;
+---------+----------+----------+-------------------------------+
| id | match_id | old_score | new_score | change_date |
+----+----------+-----------+-----------+-------------------------------+
| 1  | 1        | NULL:NULL | 2:1       | 2026-01-30 10:30:45.123456  |
| 2  | 1        | 2:1       | 2:2       | 2026-01-30 10:31:12.654321  |
+----+----------+-----------+-----------+-------------------------------+
```

---

## 10. Transakcje

### 10.1 Opis problemu

Wprowadzanie rezultatu meczu do bazy danych jest operacją złożoną, która wymaga jednoczesnej modyfikacji kilku obszarów systemu. Aby zapewnić standard integralności danych, proces ten realizowany jest jako operacja atomowa.
1. Zaaktualizowanie wyniku w tabeli `matches`
2. Dodanie wpisów dla każdego strzelcy w tabeli `match_events`
3. Zautomatyzowanie logowania w `audit_logs` (trigger)

### 10.2 Implementacja transakcji

```python
def add_match_results(match_id, h_score, a_score, scorers_list):
    """
    Dodaje wynik meczu i strzelców w jednej transakcji.
    Jeśli któraś operacja się nie powiedzie, wszystkie zmiany są wycofywane.
    """
    conn = get_db_connection()
    try:
        c = conn.cursor()
        # Operacja 1: Aktualizacja wyniku
        c.execute('''UPDATE matches
                     SET home_score = ?, away_score = ?
                     WHERE id = ?''', (h_score, a_score, match_id))
        
        # Operacja 2: Dodanie strzelców
        for player_id, minute in scorers_list:
            c.execute('''INSERT INTO match_events 
                         (match_id, player_id, event_type, minute)
                         VALUES (?, ?, 'goal', ?)''', 
                      (match_id, player_id, minute))
        
        # Commit - wszystkie operacje się powiodły
        conn.commit()
        print("Wynik i strzelcy dodani pomyślnie")
        
    except Exception as e:
        # Rollback - coś poszło nie tak, wycofujemy zmiany
        conn.rollback()
        print("Błąd podczas dodawania wyniku i strzelców:", e)
        
    finally:
        conn.close()
```

### 10.3 Mechanizm działania

1. **`try` blok** - wszystkie operacje SQL są wykonywane
2. **`conn.commit()`** - zatwierdza transakcję (wszystkie zmiany są zapisywane do bazy)
3. **`except` blok** - w przypadku błędu:
   - Trigger SQL NIE jest uruchamiany (bo zmiana nie doszła do skutku)
   - `conn.rollback()` cofa wszystkie zmiany do ostatniego commit
4. **`finally` blok** - zamyka połączenie w każdym przypadku

### 10.4 ACID w praktyce

- **Atomicity** ✓ - Albo wszystkie operacje, albo żadna
- **Consistency** ✓ - Baza pozostaje w spójnym stanie
- **Isolation** ✓ - SQLite używa poziomego zamknięcia (locking)
- **Durability** ✓ - Po commit, dane są trwale zapisane

---

## 11. Ochrona

### 11.1 Hashowanie haseł

System używa **SHA-256** do zabezpieczenia haseł:

```python
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_hash, password):
    return stored_hash == hash_password(password)
```

**Przepływ:**
1. Użytkownik wpisuje hasło w plaintext
2. Hasło jest haszowane (algorytm SHA-256)
3. Hash jest porównywany z hashem zapisanym w bazie
4. W bazie nie jest przechowywane plaintext hasła

**Domyślne hasła:**
- Admin: `adminpass` → hash: `8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918`
- User: `user123` → hash: `0d9b5d7c2c5f3c3d8e9c8b8f8c8c8b8c...`

### 11.2 Ochrona przed SQL Injection

System używa **parametryzowanych zapytań** (prepared statements):

```python
# BEZPIECZNE 
c.execute('SELECT id, role FROM users WHERE username = ?', (username,))

# NIEBEZPIECZNE 
c.execute(f"SELECT id, role FROM users WHERE username = '{username}'")
```

Dlaczego parametryzowane zapytania są bezpieczne?
- Parametry (`?`) są zawsze traktowane jako dane, nigdy jako kod SQL
- Nawet jeśli username = `' OR '1'='1`, zostanie potraktowany jako string, nie jako warunek SQL

### 11.3 Kontrola dostępu

Dwa poziomy uprawnień zaimplementowane w aplikacji:

```python
# Sprawdzenie roli użytkownika
if current_user and current_user[1] == 'admin':
    # Pokaż panel administratora
    admin_panel()
else:
    # Pokaż tylko opcje dla użytkownika zwykłego
    show_user_menu()
```

## 12. Instrukcja uruchomienia

### 12.1 Wymagania systemowe

- **Python:** 3.7+
- **System:** Windows, Linux, macOS
- **Biblioteki:** hashlib (standard library), sqlite3 (standard library)

### 12.2 Instalacja krok po kroku

```bash
# 1. Pobranie/rozpakowanie projektu
cd /sciezka/do/projekt_bazy

# 2. Inicjalizacja bazy danych
python setup_db.py

# 3. Uruchomienie aplikacji
python main.py
```

### 12.3 Struktura projektu

```
projekt_bazy/
├── main.py              # Aplikacja główna (CLI)
├── database.py          # Funkcje bazy danych
├── setup_db.py          # Inicjalizacja i dane testowe
├── football.db          # Baza danych SQLite (tworzona automatycznie)
└── README.md            # Ta dokumentacja
```

### 12.4 Pierwsze uruchomienie

```bash
# Skrypt setup_db.py:
# 1. Tworzy tabele
# 2. Tworzy triggery
# 3. Wstawia domyślne konta (admin/kibic)
# 4. Generuje 12 drużyn
# 5. Generuje ~36 piłkarzy (po 3 na drużynę)
# 6. Generuje ~108 meczów (12 na sezon, 9 sezonów)
# 7. Generuje losowe wyniki i bramkarzy

python setup_db.py
# Sukces! Baza danych została utworzona.
# Wygenerowano 108 meczów w 9 sezonach.
# Dodano 12 drużyn i 36 piłkarzy.
```

### 12.5 Dostęp do aplikacji

**Menu główne:**
```
============================================================
               FOOTBALL MATCH CENTER
============================================================
1. Logowanie
2. Rejestracja nowego konta
3. Przeglądaj mecze (wg Sezonu)
4. Tabela Ligowa
5. Szukaj drużyny
0. Wyjście
```

**Konta testowe:**

| Login | Hasło | Rola |
|-------|-------|------|
| admin | adminpass | Administrator |
| kibic | user123 | Użytkownik |

### 12.6 Dostępne funkcjonalności

**Dla wszystkich:**
- Logowanie / Rejestracja
- Przeglądanie meczów
- Tabela ligowa
- Wyszukiwanie drużyn

**Dla administratora (po zalogowaniu z `role=admin`):**
```
1. Edytuj wynik meczu (Update)
2. Dodaj nową drużynę (Create)
3. Dodaj nowego piłkarza (Create)
4. Usuń mecz (Delete)
5. Usuń piłkarza (Delete)
```

## Możliwości rozbudowy i integracji

- Eksport danych do CSV/Excel
- Integracja z aplikacją webową (np. Flask, Django REST)
- Automatyczne pobieranie składów i wyników z API sportowych
- Wersja mobilna (np. Kivy, React Native)
- Rozszerzenie o statystyki zaawansowane (asysty, kartki, minuty na boisku)
- System powiadomień e-mail/SMS o nowych wynikach

---
