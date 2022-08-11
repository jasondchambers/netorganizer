import requests
import json
from ports import SecureNetworkAnalyticsSessionPort
try:
    requests.packages.urllib3.disable_warnings()
except:
    pass

class SecureNetworkAnalyticsSessionAdapter(SecureNetworkAnalyticsSessionPort):
    """Secure Network Analytics Session."""

    XSRF_HEADER_NAME = 'X-XSRF-TOKEN'

    def __init__(self) -> None:
        self.__host = None
        self.__api_session = None
        self.__tenant_id = None

    # overriding abstract method
    def login(self,host: str, user: str, password: str) -> None:
        #TODO - protect against successive logins without logging out
        self.__host = host
        self.__authenticate(user,password)
        self.__tenant_id = self.__query_tenant_id() 

    # overriding abstract method
    def logout(self) -> None:
        """Logout of Secure Network Analytics."""
        # pylint: disable=unused-variable
        if not self.__tenant_id: return
        uri = 'https://' + self.__host + '/token'
        response = self.__api_session.delete(uri, timeout=30, verify=False)
        self.__api_session.headers.update({SecureNetworkAnalyticsSessionAdapter.XSRF_HEADER_NAME: None})
        self.__host = None
        self.__api_session = None
        self.__tenant_id = None

    # overriding abstract method
    def get_host(self) -> str:
        return self.__host

    # overriding abstract method
    def get_tenant_id(self) -> str:
        return self.__tenant_id

    # overriding abstract method
    def get_api_session(self) -> requests.Session:
        return self.__api_session

    def __authenticate(self, user: str, password: str) -> None:
        """Authenticate with Secure Network Analytics."""
        self.__api_session = requests.Session()
        uri = "https://" + self.__host + "/token/v2/authenticate"
        login_request_data = {
            "username": user,
            "password": password
        }
        try:
            response = self.__api_session.request("POST", uri, verify=False, data=login_request_data, timeout=3)
            if response.status_code == 200:
                # Set XSRF token for future requests
                for cookie in response.cookies:
                    if cookie.name == 'XSRF-TOKEN':
                        self.__api_session.headers.update({SecureNetworkAnalyticsSessionAdapter.XSRF_HEADER_NAME: cookie.value})
                        break
            else:
                raise SecureNetworkAnalyticsSessionPort.FailedToLogin()
        except requests.exceptions.ConnectionError as e:
            raise SecureNetworkAnalyticsSessionPort.FailedToLogin() from e

    def __query_tenant_id(self) -> str:
        """Discover the tenant id."""
        url = 'https://' + self.__host + '/sw-reporting/v1/tenants/'
        response = self.__api_session.request("GET", url, verify=False)
        if response.status_code == 200:
            tenant_list = json.loads(response.content)["data"]
            return tenant_list[0]["id"]