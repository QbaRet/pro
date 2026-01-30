# Dokumentacja projektu: Football Match Center
## System Obsługi Rozgrywek Piłkarskich (CLI)

**Autor:** [Twoje Imię i Nazwisko]  
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

**Football Match Center** to aplikacja konsolowa służąca do gromadzenia, przetwarzania i analizy wyników rozgrywek piłkarskich. System oparty jest na relacyjnej bazie danych i umożliwia zarządzanie pełnym cyklem życia danych meczowych – od planowania, przez wprowadzanie wyników, aż po generowanie tabel ligowych.

### 1.1 Główne cele systemu

1.  **Archiwizacja danych** – trwałe przechowywanie historii meczów, drużyn i zawodników z podziałem na sezony.
2.  **Analiza rozgrywek** – automatyczne generowanie tabeli ligowej (punkty, bilans bramek) na podstawie surowych wyników meczów.
3.  **Zarządzanie strukturą ligi** – pełna obsługa CRUD (tworzenie, edycja, usuwanie) dla drużyn, piłkarzy i meczów.
4.  **Audytowalność** – automatyczne logowanie zmian wyników meczów (zabezpieczenie przed manipulacją).

---

## 2. Charakterystyka użytkowników

System przewiduje **dwa typy użytkowników** o zróżnicowanych uprawnieniach:

### 2.1 Administrator (`role = 'admin'`)

**Charakterystyka:**
* Osoba zarządzająca systemem (np. pracownik związku piłki nożnej).
* Posiada pełny dostęp do modyfikacji danych (zapis/odczyt/usuwanie).
* Odpowiada za spójność i poprawność danych w bazie.

**Uprawnienia:**
* Dodawanie nowych drużyn i piłkarzy.
* Wprowadzanie i edycja wyników meczów (wraz ze strzelcami).
* Usuwanie błędnych rekordów (mecze, zawodnicy).

### 2.2 Użytkownik / Kibic (`role = 'user'`)

**Charakterystyka:**
* Osoba zainteresowana wynikami.
* Posiada dostęp w trybie odczytu (SELECT).
* Może samodzielnie założyć konto w systemie.

**Uprawnienia:**
* Przeglądanie listy meczów w wybranym sezonie.
* Wyświetlanie tabeli ligowej.
* Wyszukiwanie meczów konkretnej drużyny.
* Podgląd szczegółów meczu (kto strzelił bramkę).

---

## 3. Wymagania funkcjonalne

System realizuje operacje CRUD oraz zaawansowane filtrowanie danych.

### 3.1 Funkcjonalności Administratora

| ID | Funkcja | Opis | Typ operacji |
|----|---------|------|--------------|
| A1 | **Dodawanie drużyny** | Rejestracja nowego klubu (nazwa, miasto, stadion). | CREATE |
| A2 | **Dodawanie piłkarza** | Przypisanie nowego zawodnika do istniejącej drużyny. | CREATE |
| A3 | **Edycja wyniku** | Wprowadzenie wyniku meczu i listy strzelców (Transakcja). | UPDATE |
| A4 | **Usuwanie meczu** | Usunięcie meczu wraz z powiązanymi zdarzeniami (kaskadowo). | DELETE |
| A5 | **Usuwanie piłkarza** | Usunięcie zawodnika z bazy. | DELETE |

### 3.2 Funkcjonalności Użytkownika

| ID | Funkcja | Opis | Typ operacji |
|----|---------|------|--------------|
| K1 | **Rejestracja** | Utworzenie konta z walidacją loginu i hasła. | CREATE |
| K2 | **Logowanie** | Autoryzacja dostępu przy użyciu hasha SHA-256. | READ |
| K3 | **Tabela ligowa** | Wyświetlenie rankingu drużyn (sortowanie po pkt i bramkach). | READ (Logic) |
| K4 | **Szczegóły meczu** | Wyświetlenie listy strzelców dla danego spotkania. | READ |
| K5 | **Wyszukiwarka** | Znajdowanie meczów po nazwie drużyny (LIKE). | READ |

---

## 4. Schemat bazy danych

Projekt bazy danych obejmuje **7 tabel** powiązanych relacjami.

### Diagram ERD (uproszczony)

```mermaid
erDiagram
    users {
        int id PK
        string username
        string password_hash
        string role
    }
    seasons {
        int id PK
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