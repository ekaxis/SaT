
# classe comum entre versão agente e servidor, ambos devem permanecer
# iguais, na mesma versão para o funcionamento correto da ferramenta
import re

pattern_alert = r'([0-9:./-]+)\s+.*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})\s+->\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d{1,5})'
pattern_data_alert = r'\d{2,3}\/\d{1,2}-\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}'
pattern_ids = r'\[\d{1,5}:\d{1,15}:\d{1,5}\]'
pattern_replace_ids = r'\[\d{1,5}:\d{1,15}:\d{1,5}\]'

"""retorna dicionário com atribustos
Returns:
    [dict] -- [dicionário com atributos]
"""
def to_dict(d: dict, f: list)-> dict:
    for x in f:
        k, v = x.split(':')
        d[k.lower()] = v.strip().lower()

"""classe para mapear alerta do NIDS (suricata or snort)
"""
class Alert:
    
    def __init__(self, host: str, data: str, msg: str, rev: str, sid: str, priority: int, protocol: str,
            from_ip: str, to_ip: str, attrs: dict, classification: str, alert_priority: int, text_alert: str):
        self.host = host
        self.text_alert = text_alert
        self.alert_priority = alert_priority
        self.classification = classification
        self.to_ip = to_ip
        self.from_ip = from_ip
        self.protocol = protocol
        self.priority = priority
        self.msg = msg
        self.sid = sid
        self.rev = rev
        self.timestamp_alert = data
        self.attrs = attrs

    def __str__(self):
        return '%s' % self.text_alert

    """mensagem que será enviado pelo bot do Telegram
    Returns:
        [dict] -- [string formatada que será enviado pelo bot do telegram]
    """
    def telegram_alert(self, ip: str, num=1) -> str:
        return '❗️[%s] [%s] [%s] [%s] [%s] from [%s]' % \
               (ip, self.timestamp_alert, self.priority, num, self.msg, self.from_ip.split(':')[0])

    """cria objeto Alert mapeado do log do SNORT
    Returns:
        [Alert] -- [objeto Alert mapeado]
    """
    @staticmethod
    def create_alert(ip: str, text: str):
        raw_data_alert, raw_ids_msg, raw_details_ips = text.split('[**]')
        data_alert = raw_data_alert.strip()
        ids = re.search(pattern_ids, raw_ids_msg).group()
        rev, sid, priority = re.sub(r'[\[|\]]', '', ids).split(':')
        msg = re.sub(pattern_replace_ids, '', raw_ids_msg)
        protocol = re.sub(r'[{|\}]', '', re.search(r'{[\w|-]+\}', raw_details_ips).group())
        raw_details, raw_ips = re.split(r'{[\w|-]+\}', raw_details_ips)
        details = re.findall(r'\[(.*?)\]', raw_details)
        attrs = {}
        to_dict(attrs, details)
        raw_ips = re.sub(r'[\\n|\s]', '', raw_ips)
        from_ip_port, _, to_ip_port = re.split(r'[->|<>]', raw_ips)
        classification = ''
        priority_alert = 0
        if 'classification' in attrs:
            classification = attrs['classification']
        if 'priority' in attrs:
            priority_alert = attrs['priority']
        text = text.replace('\n', '').lower()[:253]
        alert = Alert(
            host=ip,
            data=data_alert,
            msg=msg.strip().lower(),
            rev=rev,
            sid=sid,
            priority=priority,
            protocol=protocol.lower(),
            from_ip=from_ip_port,
            to_ip=to_ip_port,
            attrs=attrs,
            classification=classification,
            alert_priority=priority_alert,
            text_alert=text)
        return alert

    """retorna o objeto Alert como um dicionário
    Returns:
        [dict] -- [Alert serializado]
    """
    def alert(self) -> dict:
        return {
            'host': self.host,
            'timestamp_alert': self.timestamp_alert,
            'to_ip': self.to_ip,
            'from_ip': self.from_ip,
            'protocol': self.protocol,
            'msg': self.msg,
            'sid': self.sid,
            'rev': self.rev,
            'priority': self.priority,
            'classification': self.priority,
            'alert_priority': self.alert_priority,
            'text_alert': self.text_alert
        }

if __name__ == '__main__':
    alert_msg = '06/01/2020-13:20:57.116054  [**] [1:2200074:2] SURICATA TCPv4 invalid checksum [**] [Classification: Generic Protocol Command Decode] [Priority: 3] {TCP} 222.186.190.14:39850 -> 172.16.41.32:22'
    alert = Alert.create_alert('127.0.0.1', alert_msg)
    from pprint import pprint
    pprint(alert.alert())
