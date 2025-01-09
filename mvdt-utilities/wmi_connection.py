from logging import Logger
from typing import List, Optional, Tuple

import win32com.client
import win32security
import time

class WMIConnection:
    """
    A wrapper class around some Win32 components that allows local connections to WMI.
    The wrapper still provides the speed and performance improvements as the wmi library while allowing
    local logons.

    This is better than the wmi library since it only allows username/password connections remotely.
    `with WMIConnection(self.account, self.logger) as c:`
        `c.query("Select * from Win32_ComputerSystem")`
    """

    def __init__(
        self, account: Tuple[str, str], logger: Logger, namespace: str = "root\\cimv2"
    ):
        self._domain, self._username = str(account[0]).split("\\")
        self._password = str(account[1])
        self._namespace = namespace
        self._conn: any = None

        self.logger = logger

    def __enter__(self):
        """
        The function thats implicitly called when used in a 'with' statement.
        """
        token = win32security.LogonUser(
            self._username,
            self._domain,
            self._password,
            win32security.LOGON32_LOGON_INTERACTIVE,
            win32security.LOGON32_PROVIDER_DEFAULT,
        )
        win32security.ImpersonateLoggedOnUser(token)
        try:
            c = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            self._conn = c.ConnectServer(".", self._namespace)
        except Exception as e:
            self.logger.error(f"Error dispatching SWbemLocator: {e}")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        win32security.RevertToSelf()
        self._conn = None

    def query(self, query: str) -> Optional[win32com.client.CDispatch]:
        try:
            if self._conn is not None:
                start = time.perf_counter()
                result = self._conn.ExecQuery(query)
                # Looks strange from the outside but its required to correctly catch most errors.

                # The COM object returned from ExecQuery still references other COM objects internally. 
                # When its possible that the resulting COM object is a collection of other COM objects, 
                # it calls back out to the WMI provider using __next__ Python function.
                
                # The child COM objects aren't actually resolved until they're queried - meaning the 
                # query can error but its not known until the COM object is iterated on or indexed.
                # Trying to access the length results in all the child COM objects being traversed
                # which will throw and subsequently handle any errors.
                _ = len(result)
                end = time.perf_counter()
                self.logger.debug(f"Executed query '{query}' in {end - start}s")
                return result
        except Exception as e:
            self.logger.error(f"Error executing query '{query}': {e}")
        return None
    
    def query_or_empty_list(self, query: str) -> win32com.client.CDispatch | List[object]:
        return self.query(query) or []

    def is_demo_mode(self) -> bool:
        return self._domain == "dynatrace" and self._username == "demo" and self._password == "demo"

    def to_underlying(self) -> any:
        return self._conn