import peewee

db = peewee.SqliteDatabase('SaT.db')

"""classe base para modelo da tabela de Alertas
"""
class Model(peewee.Model):
    class Meta:
        database = db

class AlertModel(Model):
    host = peewee.CharField()
    timestamp_alert = peewee.CharField()
    to_ip = peewee.CharField()
    from_ip = peewee.CharField()
    protocol = peewee.CharField()
    msg = peewee.CharField()
    sid = peewee.CharField()
    rev = peewee.CharField()
    priority = peewee.IntegerField()
    classification = peewee.CharField()
    alert_priority = peewee.IntegerField()
    text_alert = peewee.CharField(unique=True)

    @staticmethod
    def add(attrs: dict)-> bool:
        try:
            if AlertModel.create( **attrs ):
                return True
        except peewee.IntegrityError:
            return False

if __name__ == '__main__':
    try: AlertModel.create_table()
    except Exception as e: print(' [err] %s' % e)

    attrs = {
        'host': '127.0.0.1',
        'timestamp_alert': '04/20-18:24:37.484048',
        'to_ip': '255.255.255.255:67',
        'from_ip': '0.0.0.0:68',
        'protocol': 'UDP',
        'msg': 'BAD-TRAFFIC same SRC/DST',
        'sid': '527',
        'rev': '1',
        'priority': 0,
        'classification': '7',
        'alert_priority': 3,
        'text_alert': '05/28/2020-10:59:21.409681  [**] [1:2221010:1] SURICATA HTTP unable to match response to request [**] [Classification: Generic Protocol Command Decode] [Priority: 3] {TCP} 172.16.41.32:19999 -> 45.234.102.102:50336'
    }

    if AlertModel.add(attrs): print(' - insert [OK]')
    alerts = AlertModel.select()
    for alert in alerts: print(alert.text_alert)
