# -*- coding: utf-8 -*-


import MySQLdb as mdb
import sys


def get_connection(database=''):
    try:
        con = mdb.connect(
            "localhost",
            "root",
            "",
            database
        )
    except mdb.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    return con


def get_cursor(database=''):
    con = get_connection(database)
    return con.cursor()


def create_database():
    print "create database crawl"
    cursor = get_cursor()
    query = """
        CREATE DATABASE IF NOT EXISTS crawl CHARACTER SET utf8 COLLATE utf8_general_ci;
    """

    cursor.execute(query)


def create_table():
    print "create table quoka"
    cursor = get_cursor("crawl")
    query = """
    CREATE TABLE IF NOT EXISTS quoka (
        id INT AUTO_INCREMENT NOT NULL,
        Boersen_ID INT DEFAULT 21,
        OBID INT,
        erzeugt_am DATE,
        Anbieter_ID VARCHAR(80),
        Anbieter_ObjektID VARCHAR(100) DEFAULT NULL,
        Immobilientyp VARCHAR(100),
        Immobilientyp_detail VARCHAR(200) DEFAULT NULL,
        Vermarktungstyp VARCHAR(50) DEFAULT 'kaufen',
        Land VARCHAR(30) DEFAULT 'Deutschland',
        Bundesland VARCHAR(50) DEFAULT NULL,
        Bezirk VARCHAR(150) DEFAULT NULL,
        Stadt VARCHAR(150),
        PLZ VARCHAR(10),
        Strasse VARCHAR(100) DEFAULT NULL,
        Hausnummer VARCHAR(40) DEFAULT NULL,
        Überschrift VARCHAR(500),
        Beschreibung VARCHAR(15000),
        Kaufpreis INT,
        Kaltmiete INT DEFAULT NULL,
        Warmmiete INT DEFAULT NULL,
        Nebenkosten INT DEFAULT NULL,
        Zimmeranzahl INT DEFAULT NULL,
        Wohnflaeche INT DEFAULT NULL,
        Monat INT,
        url VARCHAR(1000),
        Telefon VARCHAR(1000),
        Erstellungsdatum DATE,
        Gewerblich INT,
        PRIMARY KEY (id)
    );
    """

    cursor.execute(query)


def create_table_stats():
    print "create table stats"
    cursor = get_cursor("crawl")
    query = """
    CREATE TABLE IF NOT EXISTS stats (
        id INT AUTO_INCREMENT NOT NULL,
        commercial INT,
        city_category VARCHAR(120),
        PRIMARY KEY (id)
    );
    """

    cursor.execute(query)


def drop_database():
    print "drop database crawl"
    cursor = get_cursor()
    query = """
    DROP DATABASE crawl
    """

    cursor.execute(query)


def prepare_database():
    drop_database()
    create_database()
    create_table()
    create_table_stats()


if __name__ == "__main__":
    create_database()
    create_table()
    create_table_stats()
