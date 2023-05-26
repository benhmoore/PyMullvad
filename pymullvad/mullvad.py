"""Contains the Mullvad class, which is a Python interface for the Mullvad CLI tool."""

import time
import subprocess


class Mullvad:
    """Python interface for Mullvad CLI tool."""

    @staticmethod
    def get_account_number():
        """Get Mullvad account number."""

        try:
            output = subprocess.check_output(
                ["mullvad", "account", "get"],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError as e:
            print("Mullvad VPN CLI tool not available.")
            return False

        result = output.strip()
        result = result.split("\n")[0]
        return int(result.split(":")[1].strip())

    @staticmethod
    def run_command(command: str) -> tuple[str, str]:
        """
        Helper method to run a command in the shell and return the output.

        Args:
            command (str): The command to run.

        Returns:
            Tuple[str, str]: The stdout and stderr from the command.
        """
        process = subprocess.run(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return process.stdout.decode("utf-8"), process.stderr.decode("utf-8")

    @staticmethod
    def login(account_number: int) -> tuple[str, str]:
        """Logs in to Mullvad account.

        Args:
            account_number (int): The account number.

        Returns:
            tuple[str, str]: The stdout and stderr from the command.
        """
        return Mullvad.run_command(f"mullvad account login {account_number}")

    @staticmethod
    def list_devices() -> list[str]:
        """Lists all available devices.

        Returns:
            list[str]: List of devices
        """

        device_list = Mullvad.run_command("mullvad account list-devices")[0].split(
            "\n"
        )[1::]
        device_list = [device.strip() for device in device_list if device.strip()]

        return device_list

    @staticmethod
    def list_relays() -> str:
        """Lists all available relays.

        Returns:
            str: List of relays
        """

        return Mullvad.run_command("mullvad relay list")[0].strip()

    @staticmethod
    def set_relay_location(
        country: str = "us", city: str = None, server: str = None
    ) -> tuple[str, str]:
        """Sets the relay location.

        Args:
            country (str, optional): The country code. Defaults to "us".
            city (_type_, optional): The city code. Defaults to None.
            server (_type_, optional): The server name. Defaults to None.

        Returns:
            tuple[str, str]: The stdout and stderr from the command.
        """
        if server:
            return Mullvad.run_command(
                f"mullvad relay set location {country} {city} {server}"
            )
        elif city:
            return Mullvad.run_command(f"mullvad relay set location {country} {city}")
        else:
            return Mullvad.run_command(f"mullvad relay set location {country}")

    @staticmethod
    def set_relay_hostname(hostname) -> tuple[str, str]:
        """Sets the relay hostname.

        Args:
            hostname (str): The hostname.

        Returns:
            tuple[str, str]: The stdout and stderr from the command.
        """
        return Mullvad.run_command(f"mullvad relay set hostname {hostname}")

    @staticmethod
    def connect(country: str = "us", city: str = None, server: str = None) -> bool:
        """Connects to an arbitrary location.
        If already connected, disconnects and reconnects to a new location.

        Waits up to 10 seconds for connection to be established.

        Args:
            country (str, optional): Country code. Defaults to "us".
            city (str, optional): City name. Defaults to None.
            server (str, optional): Server name. Defaults to None.

        Returns:
            bool: True if connected, False otherwise.
        """

        # Disconnect if already connected
        if "Connected" in Mullvad.get_status():
            Mullvad.disconnect()

        # Connect to new location
        Mullvad.set_relay_location(country, city, server)
        Mullvad.run_command("mullvad connect")

        # Wait for connection to be established
        wait_iter = 0
        while "Connected" not in Mullvad.get_status():
            time.sleep(0.5)

            if wait_iter > 20:
                return False
            wait_iter += 1

        return True

    @staticmethod
    def disconnect() -> tuple[str, str]:
        """Disconnects from Mullvad VPN.

        Returns:
            tuple[str, str]: The stdout and stderr from the command.
        """
        return Mullvad.run_command("mullvad disconnect")

    @staticmethod
    def update_relay() -> tuple[str, str]:
        """Updates the relay list.

        Returns:
            tuple[str, str]: The stdout and stderr from the command.
        """
        return Mullvad.run_command("mullvad relay update")

    @staticmethod
    def get_status(verbose=False) -> str:
        """Gets the status of the VPN connection.

        Args:
            verbose (bool, optional): Whether to return verbose output. Defaults to False.

        Returns:
            str: The status of the VPN connection.
        """
        if verbose:
            return Mullvad.run_command("mullvad status -v")[0].strip()
        else:
            return Mullvad.run_command("mullvad status")[0].strip()
