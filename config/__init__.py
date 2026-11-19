# config package

# На shared-хостинге (Hostland) компилируемый mysqlclient обычно собрать
# нельзя, поэтому в качестве драйвера MySQL используется чистый PyMySQL.
# Локально (PostgreSQL) PyMySQL может отсутствовать — тогда просто пропускаем.
try:  # pragma: no cover
    import pymysql

    pymysql.install_as_MySQLdb()
except ImportError:  # pragma: no cover
    pass