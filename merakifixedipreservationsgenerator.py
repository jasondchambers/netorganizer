
class MerakiFixedIpReservationsGenerator() : 
        def generate(self,device_table) -> dict:
                dict = {}
                df = device_table.df
                macs = df.mac.unique().tolist()
                for mac in macs :
                        device_df = df.query('mac == @mac')
                        if device_df.shape[0] == 1:
                                ip = device_df.iloc[0]['ip']
                                name = device_df.iloc[0]['name']
                                dict[mac] = { 
                                        'ip': ip, 
                                        'name': name}
                return dict



#Generate a dict of this format - follow same pattern as registereddevicesgenerator.py
#    dict = { 
        #'aba': {'ip': '192.168.128.191', 'name': 'Work Laptop'}, 
        #'abb': {'ip': '192.168.128.202', 'name': 'HS105'}, 
        #'bba': {'ip': '192.168.128.191', 'name': 'Echo 1'}, 
        #'bbb': {'ip': '192.168.128.204', 'name': 'Echo 2'}}