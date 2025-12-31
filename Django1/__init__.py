import pymysql

# Esta linha é OBRIGATÓRIA para enganar a checagem do Django
pymysql.version_info = (2, 2, 7, "final", 0)

pymysql.install_as_MySQLdb()