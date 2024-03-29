import re
import json
from deepdiff import DeepDiff
from devicetable import DeviceTable
from ports import SecureNetworkAnalyticsHostGroupManagementPort, SecureNetworkAnalyticsSessionPort


class SecureNetworkAnalyticsHostGroupManagementAdapter(SecureNetworkAnalyticsHostGroupManagementPort):

    def __init__(self, config: dict, sna_session_port: SecureNetworkAnalyticsSessionPort):
        self.__sna_session_port = sna_session_port
        self.host = config['sna.manager.host']
        self.username = config['sna.manager.username']
        self.password = config['sna.manager.password'] 

    # overriding abstract method
    def update_host_groups(self,device_table: DeviceTable) -> None: #TODO
        hostgroups = self.__build_hostgroups(device_table.df)
        self.__sna_session_port.login(
                self.host,
                self.username,
                self.password)
        sna_hostgroup_manager = SnaHostGroupManager(self.__sna_session_port)
        sna_hostgroup_manager.push_changes(hostgroups)
        self.__sna_session_port.logout()

    def __build_hostgroups(self, df):
        """From the specified DataFrame, build a dictionary of hostgroups.
        Returns something similar to the following:
        hostgroups = {
            'Lights': ['192.168.128.10', '192.168.128.191', '192.168.128.192'],
            'Eero':   ['192.168.128.11'],
            'Ring': ['192.168.128.15', '192.168.128.16', '192.168.128.17'],
            'Laptops': ['192.168.128.190']
        }
        """
        # pylint: disable=invalid-name
        hostgroups = {}
        groups = self.__get_groups(df)
        for group_name in groups :
            hostgroups[group_name] = self.__get_device_ips_in_group(df,group_name)
        return hostgroups

    def __get_groups(self, df) -> list :
        """Produce a list of all unique groups in the device table."""
        # pylint: disable=invalid-name
        return df.group.unique().tolist()

    def __get_device_ips_in_group(self, df, group_name) -> list:
        """Produce a list of all device IPs in specified group."""
        # pylint: disable=unused-variable
        # pylint: disable=invalid-name
        list_of_ips = []
        for index, row in df.query(f'group == "{group_name}"').iterrows():
            list_of_ips.append(row["ip"])
        return list_of_ips

class SnaHostGroupManager:
    """Facade for the Secure Network Analytics Host Group REST API."""

    INSIDE_HOSTS = 'Inside Hosts'
    NET_ORGANIZER_GROUPS = 'Net Organizer Groups'

    def __init__(self, sna_session_port: SecureNetworkAnalyticsSessionPort) -> None:
        self.sna_session_port = sna_session_port
        self.hostgroups_to_create_set = set()
        self.hostgroups_to_update_set = set()
        self.hostgroups_to_delete_set = set()

    def push_changes(self, hostgroups_changes):
        """Push changes to Secure Network Analytics.
        Newly discovered hostgroups are created.
        Existing hostgroups that have changed are updated.
        Hostgroups that are no longer needed are deleted.
        """
        current_hostgroups = self.query_current_hostgroups()
        self.analyze_changes(current_hostgroups, hostgroups_changes)
        self.create_hostgroups(self.hostgroups_to_create_set,hostgroups_changes)
        self.update_hostgroups(self.hostgroups_to_update_set,hostgroups_changes)
        self.delete_hostgroups(self.hostgroups_to_delete_set)

    def query_current_hostgroups(self) -> dict:
        """Query the current hostgroups that exist in Secure Network Analytics."""
        current_hostgroups = {}
        inside_hosts_id = self.find_hostgroup_id(SnaHostGroupManager.INSIDE_HOSTS)
        net_organizer_groups_id = self.find_hostgroup_id(SnaHostGroupManager.NET_ORGANIZER_GROUPS)
        if net_organizer_groups_id:
            url = f'https://{self.sna_session_port.get_host()}/smc-configuration/rest/v1/tenants/{self.sna_session_port.get_tenant_id()}/tags/tree'
            response = self.sna_session_port.get_api_session().request("GET", url, verify=False)
            if response.status_code == 200:
                hostgroup_tree = json.loads(response.content)["data"]
                inside_host_children = SnaHostGroupManager.get_group_children(hostgroup_tree[0]['root'],inside_hosts_id)
                net_org_hostgroup_children = SnaHostGroupManager.get_group_children(inside_host_children,net_organizer_groups_id)
                hostgroup_map = SnaHostGroupManager.build_hostgroup_name_to_id_map(net_org_hostgroup_children)
                for name,hostgroup_id in hostgroup_map.items():
                    current_hostgroups[name] = self.get_list_of_ips_for_hostgroup(hostgroup_id)
        return current_hostgroups

    def analyze_changes(self, old, new): # Tested
        """Analyze the changes between what currently exists and the new modifications."""
        diff = DeepDiff(old, new)
        self.hostgroups_to_create_set = SnaHostGroupManager.get_hostgroups_to_create(diff)
        self.hostgroups_to_update_set = SnaHostGroupManager.get_hostgroups_to_update(diff)
        self.hostgroups_to_delete_set = SnaHostGroupManager.get_hostgroups_to_delete(diff)

    @staticmethod # Tested
    def get_hostgroups_to_create(diff) -> set:
        """Determine the hostgroups that need to be created."""
        create_set = set()
        if diff:
            if 'dictionary_item_added' in diff:
                added_list = diff['dictionary_item_added']
                for added in added_list:
                    added = re.search(r"'(.*?)'", added, re.DOTALL).group()
                    added = added.strip("'")
                    create_set.add(added)
        return create_set

    def create_hostgroups(self, hostgroups_to_create_set, hostgroups_changes): #Tested
        """Create the hostgroups."""
        net_organizer_hostgroup_id = self.ensure_net_organizer_groups_exists()
        if not hostgroups_to_create_set:
            print('No new host groups to add')
        for hostgroup_name in hostgroups_to_create_set:
            list_of_ips = hostgroups_changes[hostgroup_name]
            print(f'Adding {hostgroup_name} {list_of_ips}')
            self.create_hostgroup(hostgroup_name, list_of_ips, net_organizer_hostgroup_id)

    def create_hostgroup(self, name, list_of_ips_in_group, parent_id): # Tested
        """Create a single hostgroup."""
        request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        request_data = [{
            'parentDisplay': {
                'name': SnaHostGroupManager.NET_ORGANIZER_GROUPS,
                'path': [SnaHostGroupManager.INSIDE_HOSTS]
            },
            'display': {
                'path': [SnaHostGroupManager.INSIDE_HOSTS, SnaHostGroupManager.NET_ORGANIZER_GROUPS]},
                'parentId': parent_id,
                'location': 'INSIDE',
                'hostBaselines': True,
                'suppressExcludedServices': True,
                'inverseSuppression': False,
                'hostTrap': False,
                'name': name,
                'ranges': list_of_ips_in_group}]
        url = f'https://{self.sna_session_port.get_host()}/smc-configuration/rest/v1/tenants/{self.sna_session_port.get_tenant_id()}/tags'
        response = self.sna_session_port.get_api_session().request("POST", url, verify=False, data=json.dumps(request_data), headers=request_headers)
        if response.status_code != 200:
            raise SecureNetworkAnalyticsHostGroupManagementPort.FailedToCreateHostGroup()

    @staticmethod # Tested
    def get_hostgroups_to_update(diff) -> set:
        """Determine the hostgroups that have changed and need to be updated."""
        # pylint: disable=invalid-name
        # pylint: disable=unused-variable
        update_set = set()
        if diff:
            if 'iterable_item_added' in diff:
                added_list = diff['iterable_item_added']
                for k,v in added_list.items():
                    hostgroup = re.search(r"'(.*?)'", k, re.DOTALL).group()
                    hostgroup = hostgroup.strip("'")
                    update_set.add(hostgroup)
            if 'iterable_item_removed' in diff:
                removed_list = diff['iterable_item_removed']
                for k,v in removed_list.items():
                    hostgroup = re.search(r"'(.*?)'", k, re.DOTALL).group()
                    hostgroup = hostgroup.strip("'")
                    update_set.add(hostgroup)
            if 'values_changed' in diff:
                for k in diff['values_changed'].keys():
                    hostgroup = re.search(r"'(.*?)'", k, re.DOTALL).group()
                    hostgroup = hostgroup.strip("'")
                    update_set.add(hostgroup)
        return update_set

    def update_hostgroups(self, hostgroups_to_update_set, hostgroups_changes):
        """Update the hostgroups that have changed."""
        if not hostgroups_to_update_set:
            print('No host groups to update')
        for hostgroup_name in hostgroups_to_update_set:
            id_to_update = self.find_hostgroup_id(hostgroup_name)
            print(f'Updating {hostgroup_name} {id_to_update}')
            self.update_hostgroup(id_to_update,hostgroups_changes[hostgroup_name])

    def update_hostgroup(self, id_to_update, new_ranges):
        """Update a single hostgroup."""
        url = f'https://{self.sna_session_port.get_host()}/smc-configuration/rest/v1/tenants/{self.sna_session_port.get_tenant_id()}/tags/{id_to_update}'
        response = self.sna_session_port.get_api_session().request("GET", url, verify=False)
        if response.status_code == 200:
            hostgroup_details = json.loads(response.content)["data"]
            hostgroup_details['ranges'] = new_ranges
            request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
            request_data = hostgroup_details
            response = self.sna_session_port.get_api_session().request("PUT", url, verify=True, data=json.dumps(request_data), headers=request_headers)
            if response.status_code != 200:
                raise SecureNetworkAnalyticsHostGroupManagementPort.FailedToUpdateHostGroup()

    @staticmethod # Tested
    def get_hostgroups_to_delete(diff) -> set:
        """Determine the hostgroups that are no longer needed and need to be deleted."""
        delete_set = set()
        if diff:
            if 'dictionary_item_removed' in diff:
                removed_list = diff['dictionary_item_removed']
                for removed in removed_list:
                    removed = re.search(r"'(.*?)'", removed, re.DOTALL).group()
                    removed = removed.strip("'")
                    delete_set.add(removed)
        return delete_set

    def delete_hostgroups(self, hostgroups_to_delete_set): #Tested
        """Delete the hostgroups that are no longer needed."""
        if not hostgroups_to_delete_set:
            print('No host groups to delete')
        for hostgroup_name in hostgroups_to_delete_set:
            id_to_delete = self.find_hostgroup_id(hostgroup_name)
            print(f'Deleting {hostgroup_name} {id_to_delete}')
            self.delete_hostgroup(id_to_delete)

    def delete_hostgroup(self, hostgroup_id): # Tested
        """Delete a single hostgroup."""
        if hostgroup_id:
            url = f'https://{self.sna_session_port.get_host()}/smc-configuration/rest/v1/tenants/{self.sna_session_port.get_tenant_id()}/tags/{hostgroup_id}'
            response = self.sna_session_port.get_api_session().request("DELETE", url, verify=False)
            if response.status_code != 200:
                raise SecureNetworkAnalyticsHostGroupManagementPort.FailedToDeleteHostGroup()

    @staticmethod # Tested
    def get_group_children(root, hostgroup_id):
        """Get the children of a group."""
        group = list(filter(lambda hostgroup: hostgroup['id'] == hostgroup_id, root))[0]
        return group['children']

    @staticmethod # Tested
    def build_hostgroup_name_to_id_map(hostgroups) -> dict:
        """Build a map from hostgroup_name -> id."""
        hostgroup_name_to_id_map = {}
        for hostgroup in hostgroups:
            name = hostgroup['name']
            hostgroup_id = hostgroup['id']
            hostgroup_name_to_id_map[name] = hostgroup_id
        return hostgroup_name_to_id_map

    def get_list_of_ips_for_hostgroup(self, hostgroup_id):
        """Return the current list of IPs for a hostgroup in Secure Network Analytics."""
        url = f'https://{self.sna_session_port.get_host()}/smc-configuration/rest/v1/tenants/{self.sna_session_port.get_tenant_id()}/tags/{hostgroup_id}'
        response = self.sna_session_port.get_api_session().request("GET", url, verify=False)
        if response.status_code == 200:
            hostgroup_details = json.loads(response.content)["data"]
            return hostgroup_details['ranges']
        return []

    def ensure_net_organizer_groups_exists(self): # Tested
        """Ensure the root group 'Net Organizer Groups' exists."""
        net_organizer_hostgroup_id = self.find_hostgroup_id(SnaHostGroupManager.NET_ORGANIZER_GROUPS)
        if not net_organizer_hostgroup_id:
            print(f'Did not find {SnaHostGroupManager.NET_ORGANIZER_GROUPS} - creating it')
            net_organizer_hostgroup_id = self.create_net_organizer_groups_group()
        else:
            print(f'{SnaHostGroupManager.NET_ORGANIZER_GROUPS} already exists')
        return net_organizer_hostgroup_id

    @staticmethod
    def find_hostgroup_id_in_tags_data(tags, hostgroup_name):
        """Find the ID for a hostgroup by it's name in tags."""
        found_id = ''
        for tag in tags:
            if tag['name'] == hostgroup_name:
                found_id = tag['id']
                break
        return found_id

    def find_hostgroup_id(self, hostgroup_name): # Tested
        """Find the hostgroup ID from Secure Network Analytics given the name."""
        url = f'https://{self.sna_session_port.get_host()}/smc-configuration/rest/v1/tenants/{self.sna_session_port.get_tenant_id()}/tags'
        response = self.sna_session_port.get_api_session().request("GET", url, verify=False)
        found_id = ''
        if response.status_code == 200:
            tags = json.loads(response.content)["data"]
            found_id = SnaHostGroupManager.find_hostgroup_id_in_tags_data(tags, hostgroup_name)
        return found_id

    def create_net_organizer_groups_group(self): # Tested
        """Create the root group 'Net Organizer Groups' under 'Inside Hosts'."""
        inside_hosts_id = self.find_hostgroup_id(SnaHostGroupManager.INSIDE_HOSTS)
        request_headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        request_data = [{
            'parentDisplay': {
                'name': SnaHostGroupManager.INSIDE_HOSTS,
                'path': []
            },
            'display': {
                'path': [SnaHostGroupManager.INSIDE_HOSTS]
            },
            'parentId': inside_hosts_id,
            'location': 'INSIDE',
            'hostBaselines': True,
            'suppressExcludedServices': True,
            'inverseSuppression': False,
            'hostTrap': False,
            'name': SnaHostGroupManager.NET_ORGANIZER_GROUPS}]
        url = f'https://{self.sna_session_port.get_host()}/smc-configuration/rest/v1/tenants/{self.sna_session_port.get_tenant_id()}/tags'
        response = self.sna_session_port.get_api_session().request("POST", url, verify=False, data=json.dumps(request_data), headers=request_headers)
        if response.status_code == 200:
            return json.loads(response.content)['data'][0]['id']
        raise SecureNetworkAnalyticsHostGroupManagementPort.FailedToCreateHostGroup()