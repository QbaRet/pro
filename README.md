# Dokumentacja projektu: Football Match Center
## System Obsługi Rozgrywek Piłkarskich (CLI)

**Autor:** Jakub Kubarek  
**Data:** Styczeń 2026  
**Technologia:** Python + SQLite  

---

## Spis treści

1. [Cel aplikacji](#1-cel-aplikacji)
2. [Charakterystyka użytkowników](#2-charakterystyka-użytkowników)
3. [Wymagania funkcjonalne](#3-wymagania-funkcjonalne)
4. [Schemat bazy danych](#4-schemat-bazy-danych)
5. [Opis tabel i kluczy](#5-opis-tabel-i-kluczy)
6. [Relacje między tabelami](#6-relacje-między-tabelami)
7. [Normalizacja bazy danych](#7-normalizacja-bazy-danych)
8. [Prawa dostępu](#8-prawa-dostępu)
9. [Trigger SQL](#9-trigger-sql)
10. [Transakcje](#10-transakcje)
11. [Bezpieczeństwo](#11-bezpieczeństwo)
12. [Instrukcja uruchomienia](#12-instrukcja-uruchomienia)

---

## 1. Cel aplikacji

**Football Match Center** to aplikacja konsolowa służąca do gromadzenia, przetwarzania i analizy wyników rozgrywek piłkarskich. System oparty jest na relacyjnej bazie danych SQLite i umożliwia zarządzanie pełnym cyklem życia danych meczowych – od planowania, przez wprowadzanie wyników, aż po generowanie tabel ligowych z automatyczną audytowalności zmian.

### 1.1 Główne cele systemu

1. **Archiwizacja danych** - trwałe przechowywanie historii meczów, drużyn i zawodników z podziałem na sezony (2016/2017 do 2024/2025)
2. **Analiza rozgrywek** - automatyczne generowanie tabeli ligowej (punkty, bilans bramek, wygrane/remisy/przegrane) na podstawie surowych wyników meczów
3. **Zarządzanie strukturą ligi** - pełna obsługa CRUD (tworzenie, edycja, usuwanie) dla drużyn, piłkarzy i meczów
4. **Śledzenie zdarzeń meczowych** - rejestrowanie bramek i kartek dla każdego zawodnika z określeniem minuty
5. **Audytowalność** - automatyczne logowanie zmian wyników meczów do tabeli audit_logs za pomocą triggera SQL

### 1.2 Zakres funkcjonalny

System obsługuje pełny cykl życia danych meczowych:
- Rejestracja użytkowników z przypisaną rolą (admin/user)
- Logowanie do systemu z weryfikacją hasła
- Przeglądanie meczów i drużyn z opcjonalnym filtrowaniem po sezonie
- Wyszukiwanie meczów drużyny po nazwie
- Generowanie tabel ligowych z automatycznym obliczeniem punktów i bilansu bramek
- Dodawanie wyników meczów i strzelców (tylko admin)
- Zarządzanie drużynami i piłkarzami (CRUD - tylko admin)
- Usuwanie meczów i piłkarzy (tylko admin)
- Automatyczne logowanie zmian wyników meczów (trigger SQL)

---

## 2. Charakterystyka użytkowników

System przewiduje **dwa typy użytkowników** o zróżnicowanych uprawnieniach:

### 2.1 Administrator (`role = 'admin'`)

**Charakterystyka:**
- Pracownik związku piłki nożnej lub administrator systemu
- Posiada pełny dostęp do modyfikacji danych (CRUD - zapis/odczyt/usuwanie)
- Odpowiada za spójność i poprawność danych w bazie
- Ma dostęp do panelu administratora w aplikacji konsolowej

**Typowe zadania:**
- Dodawanie i edycja wyników meczów
- Rejestrowanie strzelców i minut bramek
- Dodawanie nowych drużyn do systemu
- Dodawanie piłkarzy do drużyn
- Usuwanie meczów i piłkarzy (w przypadku błędów)
- Przeglądanie wszystkich danych bez ograniczeń
- Zarządzanie kont użytkowników i uprawnieniami

**Domyślne konto:**
- Login: `admin`
- Hasło: `adminpass`

### 2.2 Użytkownik zwykły / Kibic (`role = 'user'`)

**Charakterystyka:**
- Kibic piłki nożnej lub zainteresowana osoba
- Posiada ograniczony dostęp - tylko do odczytu danych
- Nie może modyfikować danych w bazie
- Nie ma dostępu do panelu administratora

**Typowe zadania:**
- Przeglądanie wyników meczów
- Wyszukiwanie meczów konkretnej drużyny
- Przeglądanie tabeli ligowej
- Wyświetlanie szczegółów meczów (strzelcy, minuty bramek)
- Przeglądanie listy zawodników drużyn

**Domyślne konto testowe:**
- Login: `kibic`
- Hasło: `user123`

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

### 7.1 Analiza postaci normalnych

Baza danych jest w **trzeciej postaci normalnej (3NF)**.

#### Pierwsza postać normalna (1NF) ✓
- Wszystkie atrybuty są atomowe (niepodzielne)
- Brak powtarzających się grup atrybutów
- Każda tabela ma klucz główny

#### Druga postać normalna (2NF) ✓
- Spełniona 1NF
- Wszystkie atrybuty niekluczowe zależą od całego klucza głównego
- W tabelach bez klucza złożonego warunek jest trywialnie spełniony

#### Trzecia postać normalna (3NF) ✓
- Spełniona 2NF
- Brak zależności przechodnich między atrybutami niekluczowymi
- Przykład: w `match_events` atrybuty (event_type, minute) zależą bezpośrednio od `id`, nie od innych atrybutów niekluczowych

### 7.2 Redundancja danych

Baza **nie ma celowej redundancji**. Wszystkie dane przechowywane są w jednym miejscu:

| Dane | Lokalizacja | Uzasadnienie |
|------|-------------|--------------|
| Wynik meczu | `matches` | Przechowywany w jednym miejscu |
| Strzelcy bramek | `match_events` | Oddzielna tabela dla zdarzeń |
| Info o drużynie | `teams` | Nie duplikuje się w innych tabelach |
| Info o zawodniku | `players` | Powiązanie przez FK do drużyny |
| Historia zmian | `audit_logs` | Automatycznie tworzone przez trigger |

---

## 8. Prawa dostępu

System implementuje **dwa poziomy dostępu** na poziomie aplikacji:

### 8.1 Macierz uprawnień

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

### 8.4 Implementacja kontroli dostępu

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

## 9. Trigger SQL

### 9.1 Cel triggera

Automatyczne logowanie zmian wyników meczów do tabeli `audit_logs`. Trigger jest kluczowym elementem audytu systemu, umożliwiającym śledzenie wszystkich zmian wyników oraz ochraniającym przed manipulacją danych.

### 9.2 Definicja triggera

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

### 9.3 Mechanizm działania

1. **Wyzwalacz:** Trigger uruchamia się PO zaaktualizowaniu kolumn `home_score` lub `away_score`
2. **Akcja:** Automatycznie wstawia rekord do `audit_logs` z:
   - ID meczu
   - Poprzednim wynikiem (w formacie "X:Y")
   - Nowym wynikiem (w formacie "X:Y")
   - Czasem zmiany (CURRENT_TIMESTAMP)

### 9.4 Przykład działania

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

Przy dodawaniu wyniku meczu i strzelców konieczne jest:
1. Zaaktualizowanie wyniku w tabeli `matches`
2. Dodanie wpisów dla każdego strzelcy w tabeli `match_events`
3. Zautomatyzowanie logowania w `audit_logs` (trigger)

Te operacje muszą być wykonane **atomowo** - albo wszystkie, albo żadna.

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

## 11. Bezpieczeństwo

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
4. W bazie nigdy nie jest przechowywane plaintext hasła

**Bezpieczeństwo:**
- SHA-256 jest funkcją односtronna (nie da się odtworzyć hasła z hasha)
- Każde hasło daje unikalny hash
- Nawet identyczne hasła będą miały taki sam hash (deterministycznie)

**Domyślne hasła (dla celów testowych):**
- Admin: `adminpass` → hash: `8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918`
- User: `user123` → hash: `0d9b5d7c2c5f3c3d8e9c8b8f8c8c8b8c...`

### 11.2 Ochrona przed SQL Injection

System używa **parametryzowanych zapytań** (prepared statements):

```python
# ✓ BEZPIECZNE - parametry są oddzielone od SQL
c.execute('SELECT id, role FROM users WHERE username = ?', (username,))

# ✗ NIEBEZPIECZNE - concatenacja stringów
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

### 11.4 Brak danych wrażliwych w logach

- Hasła nigdy nie są logowane
- Logi zmian (`audit_logs`) zawierają tylko wyniki meczów, nie dane użytkowników
- Zmiany są rejestrowane z timestamp dla audytu

---

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

### 12.7 Przykładowe scenariusze użycia

**Scenariusz 1: Kibic chce zobaczyć wyniki**
```
1. main_menu() → wybierz "3" (Przeglądaj mecze)
2. Podaj ID sezonu: 9 (2024/2025)
3. Wyświetlę się lista meczów z wynikami
4. (opcjonalnie) Podaj ID meczu, aby zobaczyć strzelców
```

**Scenariusz 2: Admin dodaje wynik meczu**
```
1. main_menu() → "1" (Logowanie)
2. Login: admin, Hasło: adminpass
3. main_menu() → "6" (Panel ADMIN)
4. Wybierz opcję "1" (Edytuj wynik)
5. Podaj ID meczu, wynik, dodaj strzelców
```

---

## Kontakt i wsparcie

- **Projekt:** Football Match Center
- **Autor:** Jakub Kubarek
- **Wersja:** 1.0
- **Data:** Styczeń 2026
- **Technologia:** Python 3.7+, SQLite 3.0+
        string name
        date start_date
    }
    teams {
        int id PK
        string name
        string city
    }
    players {
        int id PK
        int team_id FK
        string last_name
        string position
    }
    matches {
        int id PK
        int season_id FK
        int home_team_id FK
        int away_team_id FK
        int home_score
        int away_score
    }
    match_events {
        int id PK
        int match_id FK
        int player_id FK
        string event_type
        int minute
    }
    audit_logs {
        int id PK
        int match_id FK
        string old_score
        string new_score
    }

    teams ||--o{ players : "posiada"
    seasons ||--o{ matches : "organizuje"
    teams ||--o{ matches : "gra jako gospodarz"
    teams ||--o{ matches : "gra jako gość"
    matches ||--o{ match_events : "zawiera"
    players ||--o{ match_events : "jest autorem"
    matches ||--o{ audit_logs : "jest monitorowany"