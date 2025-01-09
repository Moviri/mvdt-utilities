import logging
import subprocess
import time
from subprocess import PIPE, CompletedProcess
from typing import IO, Dict, List, Optional, Tuple

from .windows_runas import RunasPopen, run_as

EXIT_SUCCESS = 0


class PowershellException(Exception):
    def __init__(self, stderr):
        self.message = stderr
        super().__init__(stderr)


class PowershellHelper:
    # Account is ("Domain\Username", "Password")
    def __init__(
        self,
        account: Tuple[str, str] | None = None,
        logger: logging.Logger | None = None,
    ):
        self._account = account
        self.logger = logger or logging.getLogger(__name__)

    def run_script_pid(self, script_path: str, arguments: Optional[List[str]]) -> Tuple[str, int]:
        username = self._account[0]
        domain = "."

        if "\\" in username:
            domain, username = username.split("\\")

        command = ["powershell.exe", "-File", script_path]
        if arguments:
            for argument in arguments:
                command.append(argument)

        result = run_as(command, username, self._account[1], domain, stdout=PIPE, stderr=PIPE)

        if result.stderr:
            message = f"{result.stderr}"
            if not message:
                message += f"\n{result.stdout}"
            raise PowershellException(result.stderr)

        if result.wait() != EXIT_SUCCESS:
            raise PowershellException(result.stdout)

        return (result.stdout.strip(), result.pid)

    def run_script(self, script_path: str, arguments: Optional[List[str]]) -> str:
        username = self._account[0]
        domain = "."

        if "\\" in username:
            domain, username = username.split("\\")

        command = ["powershell.exe", "-File", script_path]
        if arguments:
            for argument in arguments:
                command.append(argument)

        result = run_as(command, username, self._account[1], domain, stdout=PIPE, stderr=PIPE)

        if result.stderr:
            raise PowershellException(result.stderr)

        if result.wait() != EXIT_SUCCESS:
            raise PowershellException(result.stdout)

        return result.stdout.strip()

    def run_command(self, command: str) -> List[Dict[str, str]]:
        """
        Runs a powershell command and returns the result formatted as a list of dict's.

        `command` - The powershell command to run

        Throws: A powershell exception if the result of running the command does not result in a list with one element.
        """

        if self._account:
            return self._runas_user_account_formatted(command)

        return self._runas_local_service_formatted(command)

    def run_raw_command_pid(self, command) -> int:
        """
        Runs the specified command and returns the PID of the Powershell process.
        """
        result = None
        if self._account:
            result = self._runas_user_account(command, False)
        else:
            result = self._runas_local_service(command, False)
        return result.pid

    def run_raw_command(self, command) -> Tuple[int, IO, IO]:
        result = None
        if self._account:
            result = self._runas_user_account(command)
        else:
            result = self._runas_local_service(command)

        return (result.returncode, result.stdout, result.stderr)

    def run_raw_command_with_error_checks(self, command) -> str:
        result = None
        if self._account:
            result = self._runas_user_account(command)

            self.check_for_errors(result.wait(), result.stderr, result.stdout)
            if not result.stdout:
                raise PowershellException(f"Command's stdout was empty: {command}")
            return result.stdout.strip()
        else:
            result = self._runas_local_service(command)

            self.check_for_errors(result.returncode, result.stderr, result.stdout)
            if not result.stdout:
                raise PowershellException(f"Command's stdout was empty: {command}")
            return result.stdout.decode().strip()

    def run_single_response_command(self, command: str) -> Dict[str, str]:
        """
        Runs a powershell command and assumes there is only one possible output.

        `command` - The powershell command to run

        Throws: A powershell exception if the result of running the command does not result in a list with one element.
        """

        result = []
        if self._account:
            result = self._runas_user_account_formatted(command)
        else:
            result = self._runas_local_service_formatted(command)

        length = len(result)
        if length != 1:
            raise PowershellException(
                f"Expected only one powershell response from {command} but got: {length}"
            )

        return result[0]

    def did_command_exit_successfully(self, command: str) -> bool:
        """
        Returns True when the command runs successfully
        """
        if self._account:
            return self._runas_user_account(command).wait() == EXIT_SUCCESS

        return self._runas_local_service(command).returncode == EXIT_SUCCESS

    def run_as_local_service_with_timeout(
        self, command: str, timeout: float
    ) -> CompletedProcess:
        """
        Timeout is in seconds
        """
        return subprocess.run(
            ["powershell.exe", command], stdout=PIPE, stderr=PIPE, timeout=timeout
        )

    def _runas_user_account_formatted(self, command: str) -> List[Dict[str, str]]:
        start = time.perf_counter()
        response = self._runas_user_account(command)

        self.check_for_errors(response.wait(), response.stderr, response.stdout)
        if not response.stdout:
            return [{}]
            # raise PowershellException(f"Command's stdout was empty: {command}")
        
        end = time.perf_counter()
        self.logger.debug(f"_runas_user_account took {end - start}s")

        return self._format_command_output(response.stdout.splitlines())

    def _runas_local_service_formatted(self, command: str) -> List[Dict[str, str]]:
        start = time.perf_counter()
        response = self._runas_local_service(command)

        self.check_for_errors(response.returncode, response.stderr, response.stdout)
        if not response.stdout:
            return [{}]
            # raise PowershellException(f"Command's stdout was empty: {command}")

        end = time.perf_counter()
        self.logger.debug(f"_runas_local_service took {end - start}ms")

        return self._format_command_output(response.stdout.decode().splitlines())

    def _runas_user_account(self, command: str, format_list: bool = True) -> RunasPopen:
        """
        Runs the command with the account specified in the constructor.

        `command` - The powershell command to run

        Throws: A powershell exception if the result of running the command does not result in a list with one element.
        """

        formatted_command = command
        if format_list:
            formatted_command = f"{formatted_command} | Format-List"

        username = self._account[0]
        domain = "."

        if "\\" in username:
            domain, username = username.split("\\")

        return run_as(
            ["powershell.exe", formatted_command],
            username,
            self._account[1],
            domain,
            stdout=PIPE,
            stderr=PIPE,
        )

    def _runas_local_service(self, command: str, format_list: bool = True) -> CompletedProcess:
        """
        Runs the command without an account.
        Command should not require additional permissions.

        `command` - The powershell command to run

        Throws: A powershell exception if the result of running the command does not result in a list with one element.
        """
        formatted_command = command
        if format_list:
            formatted_command = f"{formatted_command} | Format-List"

        self.logger.info(f"Running local service command: {formatted_command}")

        return subprocess.run(
            ["powershell.exe", formatted_command], stdout=PIPE, stderr=PIPE
        )

    def _format_command_output(self, lines: List[str]) -> List[Dict[str, str]]:
        """
        Ugly but ignores all newlines/strips whitespace and returns a list of dicts.
        Powershell "entities" are seperated by a newline.
        If there are more than one powershell "entities" in the response then each entity will be its own dict.
        Run with the output of `Get-WmiObject -Class Win32_PerfFormattedData_PerfOS_Processor | Select Name`
        for an example
        """
        delimeter = " : "

        result: List[Dict[str, str]] = []
        tmp: Dict[str, str] = {}
        previous_key: str | None = None
        for line in lines:
            if line and delimeter in line:
                split = line.split(delimeter)
                previous_key = split[0].strip()
                tmp[split[0].strip()] = split[1] if len(split) > 1 else ""
            elif line and tmp and previous_key:
                tmp[previous_key] = tmp[previous_key] + line.strip()
                previous_key = None
                continue
            elif tmp:
                result.append(tmp)
                tmp = {}
        return result
    
    def check_for_errors(self, returncode: int, stderr, stdout):
        if returncode != EXIT_SUCCESS:
            message = f"Exit Code: {returncode}\nstderr: '{stderr}'\nstdout: '{stdout}'"
            raise PowershellException(message)