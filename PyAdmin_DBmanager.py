#-------------------------------------------------------------------------------
# Name:        SQL_Module
# Purpose:
#
# Author:      Mattia
#
# Created:     23/02/2012
# Copyright:   (c) Mattia 2012
# Licence:
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import MySQLdb
import sqlite3
import re

# DB_Manager costants
(SQL_DDL,SQL_DML,SQL_TYPES,SQL_COLLATION) = ('sql_ddl','sql_dml','types','collation')

class DB_Manager():

    # DB_Manager functions
    def __init__(self):
        self.NC = True
        self._cursor = sqlite3.connect('._pysql').cursor()

    @staticmethod
    def fetch_list(items):
        res = []
        for item in items:
            res.append(list(item))
        return res

    # MySQL Database
    def connect(self, user, pw=None, hostname='localhost', port_number=3306):
        try:
            if pw:
                self.db = MySQLdb.Connect(user=user, passwd=pw, host=hostname, port=port_number)
            else:
                self.db = MySQLdb.Connect(user=user, host=hostname, port=port_number)
            self.host = hostname
            self.cursor = self.db.cursor()

        except MySQLdb.Error, e:
            return "Errore %d: %s" % (e.args[0], e.args[1])
        else:
            self.NC = False
            return 'OK'


    def create_db(self, db_name, collation):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            try:
                self.cursor.execute('create database {} collate {}'.format(db_name, collation))
            except MySQLdb.Error,e:
                return "Errore %d: %s" % (e.args[0], e.args[1])
            else:
                return 'OK'


    def del_db(self, db_name):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            try:
                self.cursor.execute('drop database {}'.format(db_name))
            except MySQLdb.Error,e:
                return "Errore %d: %s" % (e.args[0], e.args[1])
            else:
                return 'OK'


    def get_dbs(self):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            try:
                self.cursor.execute('show databases')
            except MySQLdb.Error,e:
                return "Errore %d: %s" % (e.args[0], e.args[1])
            else:
                dbs = []
                for db in self.cursor.fetchall():
                    if db[0]!="performance_schema" and db[0]!="mysql" and db[0]!="information_schema":
                        dbs.append(db[0])
                return dbs


    def set_db(self, dbname):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            if dbname!="performance_schema" and dbname!="mysql" and dbname!="information_schema":
                try:
                    self.cursor.execute('use ' + dbname)
                except MySQLdb.Error,e:
                    return "Errore %d: %s" % (e.args[0], e.args[1])
                else:
                    return True
            else:
                return 'Errore 1046: No database selected'


    def get_tbls(self, db=None):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            if db:
               self.set_db(db)

            try:
                self.cursor.execute('show tables')
            except MySQLdb.Error,e:
                return "Errore %d: %s" % (e.args[0], e.args[1])
            else:
                tbls = []
                for tbl in self.cursor.fetchall():
                    tbls.append(tbl[0])
                return tbls


    def get_tbl_schema(self, tbl_name, db=None):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            if db:
                self.set_db(db)

            cols = []
            query = "show columns from " + tbl_name

            try:
                self.cursor.execute(query)
            except MySQLdb.Error,e:
                return "Errore %d: %s" % (e.args[0], e.args[1])
            else:
                for col in self.cursor.fetchall():
                    cols.append(col)
                return cols


    def col_syntax(self, col):
        name = col[0]
        tipo = col[1]
        # Set NotNUll
        nn = ''
        if col[2]=='1':
            nn = 'NOT NULL'
        # Set Key Type
        kt = ''
        if col[3] == 'Primary Key':
            kt = 'PRIMARY KEY'
        elif col[3] == 'Unique':
            kt = 'UNIQUE'
        elif col[3] == 'Foreign Key':
            kt = ', FOREIGN KEY ({}) REFERENCES {}({}) on delete {} on update {}'.format(name, col[7], col[8], col[9], col[10])
        # Set Auto_Increment
        ai = ''
        if col[4] == '1':
            ai = 'AUTO_INCREMENT'
        # Set Deafult Value
        default = col[5]
        # Set Attribute
        attr = col[6]

        return '{} {} {} {} {} {} {}'.format( name, tipo, attr, nn, default, ai,
                                                kt )


    def new_tbl(self, tbl_name, cols, db=None):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            db_name = ''
            if db:
                db_name = '{}.'.format(db)

            query = 'create table {}{} ( '.format(db_name,tbl_name)
            for col in cols[:-1]:
                query += self.col_syntax(col) + ','

            query += self.col_syntax(cols[-1]) + ' );'

            try:
                self.cursor.execute(query)
            except MySQLdb.Error,e:
                return "Errore %d: %s" % (e.args[0], e.args[1])
            else:
                return 'OK'


    def del_tbl(self, tbl_name, db_name=None):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            if db_name:
                db_name = '{}.'.format(db_name)

            try:
                self.cursor.execute('drop table {}{}'.format(db_name, tbl_name))
            except MySQLdb.Error,e:
                return "Errore %d: %s" % (e.args[0], e.args[1])
            else:
                return 'OK'


    def insert(self, tbl_name, columns, values, db_name=None):
        if self.NC:
            return "Errore PySQL: Not Connected"

        db = ''
        if db_name:
            db = '{}.'.format(db_name)

        col = val = ''
        lst = zip(columns, values)
        for c, v in lst[:-1]:
            if c != '' and v != '':
                col += '{},'.format(c)
                val += "'{}',".format(v)
        col += '{}'.format(columns[-1])
        val += "'{}'".format(values[-1])

        query = 'INSERT INTO {}{}({}) VALUE ({})'.format(db, tbl_name, col, val)

        try:
            self.cursor.execute(query)
        except MySQLdb.Error,e:
            self.rollback()
            return "Errore %d: %s" % (e.args[0], e.args[1])
        else:
            self.commit()
            return 'OK'


    def update(self, tbl_name, columns, old_values, new_values, db_name=None):
        if self.NC:
            return "Errore PySQL: Not Connected"

        db = ''
        if db_name:
            db = '{}.'.format(db_name)

        n_val = o_val = ''
        t = zip(columns, old_values, new_values)
        for c, o, n in t[:-1]:
            if c != '' and o != '' and n != '':
                n_val += "{} = '{}', ".format(c, n)
                o_val += "{} = '{}' AND ".format(c, o)
        n_val += "{} = '{}'".format(columns[-1], new_values[-1])
        o_val += "{} = '{}'".format(columns[-1], old_values[-1])

        query = 'UPDATE {}{} SET {} WHERE {}'.format(db, tbl_name, n_val, o_val)

        try:
            self.cursor.execute(query)
        except MySQLdb.Error,e:
            self.rollback()
            return "Errore %d: %s" % (e.args[0], e.args[1])
        else:
            self.commit()
            return 'OK'


    def delete(self, tbl_name, columns, values, db_name=None):
        if self.NC:
            return "Errore PySQL: Not Connected"

        db = ''
        if db_name:
            db = '{}.'.format(db_name)

        cond = ''
        t = zip(columns, values)
        for c, v in t[:-1]:
            cond += "{} = '{}' AND ".format(c, v)
        cond += "{} = '{}'".format(columns[-1], values[-1])

        query = 'DELETE FROM {}{} WHERE {}'.format(db, tbl_name, cond)

        try:
            self.cursor.execute(query)
        except MySQLdb.Error,e:
            self.rollback()
            return "Errore %d: %s" % (e.args[0], e.args[1])
        else:
            self.commit()
            return 'OK'


    def query(self, tbl_name, columns='*', where=None, limit=None, db=None):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            if db:
                self.set_db(db)

            if where:
                wh = 'where {}'.format(where)
            else:
                wh = ''

            if limit:
                lm = 'limit {}'.format(limit)
            else:
                lm = ''

            cmd = 'select {} from {} {} {}'.format(columns, tbl_name, wh, lm)

            try:
                self.cursor.execute(cmd)
            except MySQLdb.Error,e:
                return "Errore %d: %s" % (e.args[0], e.args[1])
            else:
                return self.fetch_list(self.cursor.fetchall())


    def count(self, tbl_name, db_name=None):
        if self.NC:
            return "Errore PySQL: Not Connected"

        if db_name:
            self.set_db(db_name)

        try:
            self.cursor.execute('SELECT COUNT(*) FROM {}'.format(tbl_name))
        except MySQLdb.Error,e:
            return "Errore %d: %s" % (e.args[0], e.args[1])
        else:
            return self.cursor.fetchall()[0][0]


    def execute(self,SQL_code):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            cmd_list = re.split(';',SQL_code)
            results = []

            for cmd in cmd_list:
                if cmd != '':
                    try:
                        self.cursor.execute(cmd)
                    except MySQLdb.Error,e:
                        return "Errore %d: %s" % (e.args[0], e.args[1])
                    else:
                        l = self.fetch_list(self.cursor.fetchall())
                        if l:
                            results.append(l)
            return results


    def permissions(self, perm_list, db_name, tbl_name, user, pw, boolean=False):
        if self.NC:
            return "Errore PySQL: Not Connected"

        t = 'REVOKE'
        t2 = 'FROM'
        if boolean:
            t = 'GRANT'
            t2 = 'TO'

        p = ''
        for i in perm_list[:-1]:
            p += i + ','
        p += perm_list[-1]


        if not pw:
            return "Errore 1048: Column 'password' cannot be null"

        w = "IDENTIFIED BY '{}'".format(pw)

        query_str = "{} {} ON {}.{} {} '{}'@'{}'".format(t, p, db_name, tbl_name,
                                                         t2, user, self.host)

        try:
            self.cursor.execute("CREATE USER '{}'@'{}' {}".format(user, self.host, w))
        except MySQLdb.Error,e:
            if e.args[0] != 1396:
                return "Errore %d: %s" % (e.args[0], e.args[1])

        try:
            self.cursor.execute(query_str)
        except MySQLdb.Error,e:
            return "Errore %d: %s" % (e.args[0], e.args[1])
        else:
            return 'OK'


    def commit(self):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            self.db.commit()


    def rollback(self):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            try:
                self.db.rollback()
            except NotSupportedError:
                return False
            else:
                return True

    def close(self):
        if self.NC:
            return "Errore PySQL: Not Connected"
        else:
            try:
                self.db.close()
                self.NC = True
            except NotSupportedError:
                return 'Errore MySQL: Closing Not Supported'
            else:
                return 'Ok'


    # SQLite Database
    def get_infos(self, type):
        self._cursor.execute('select name from ' + type)
        cmds = []
        for cmd in self._cursor.fetchall():
            cmds.append(cmd[0])
        return cmds


    def get_cmd_syntax(self, type, cmd):
        self._cursor.execute('select syntax from ' + type + ' where name=?', (cmd,))
        return self._cursor.fetchone()[0]


def main():
    test = DB_Manager()

    print test.connect('root','ciao93')
    print test.get_dbs()

##    print test.set_db('group')
    print test.get_tbls('information_schema')
    print test.get_tbls('world')
##
##    test.execute('use world')
##
##    print test.get_infos(SQL_DDL)
##    print
##
##    print test.get_cmd_syntax(SQL_DML,'DELETE')
##
##    results = test.execute('show tables; use sakila; show tables;')
##    for result in results:
##        print result
##
##    print
##    print test.get_infos(SQL_TYPES)
##
##
##    print len(test.get_infos(SQL_COLLATION))

##    print test.get_tbl_schema('prova','biblioteca')
##
    test.set_db('groupon')

##    print test.query('city','id',limit='0, 3')
##    print test.query('city','id',limit='3, 3')
##
##    print test.count('country')

    print test.insert('new_table', ['idnew_table'],['37'])

    print test.update('new_table', ['idnew_table'], ['37'], ['28'])

    print test.delete('new_table', ['idnew_table'], ['45'])


if __name__ == '__main__':
    main()
