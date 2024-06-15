import pytest
import sqlite3
import database

def test_utworz_tabele():
    database.utworz_tabele()
    conn = sqlite3.connect('dane_pomiarowe.db')
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='czujniki'")
    assert c.fetchone() is not None
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='dane'")
    assert c.fetchone() is not None
    conn.close()

def test_zapisz_czujnik():
    database.utworz_tabele()
    database.zapisz_czujnik(1, 'PM10')
    conn = sqlite3.connect('dane_pomiarowe.db')
    c = conn.cursor()
    c.execute("SELECT * FROM czujniki WHERE id_czujnika = 1")
    assert c.fetchone() == (1, 'PM10')
    conn.close()

def test_zapisz_dane():
    database.utworz_tabele()
    database.zapisz_czujnik(1, 'PM10')
    database.zapisz_dane((1, '2022-01-01 00:00:00', 50.0))
    conn = sqlite3.connect('dane_pomiarowe.db')
    c = conn.cursor()
    c.execute("SELECT * FROM dane WHERE id_czujnika = 1")
    assert c.fetchone() == (1, '2022-01-01 00:00:00', 50.0)
    conn.close()
