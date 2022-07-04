class MerakiFixedIpReservationsLoader:

    def __init__(self,meraki_dashboard,network_id,vlan_id) -> None:
        self.dashboard = meraki_dashboard
        self.network_id = network_id
        self.vlan_id = vlan_id

    def load(self) :
        vlan = self.dashboard.appliance.getNetworkApplianceVlan(self.network_id, str(self.vlan_id))
        existing_reservations = vlan['fixedIpAssignments']
        return existing_reservations