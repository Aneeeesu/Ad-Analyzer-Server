import subprocess
import uuid
from threading import Thread
import time
import asyncio
import select
import os

from transformers import pipeline
# load pipe

def is_valid_uuid(string):
    """
    Check if a string is a valid UUID.
    Args:
        string (str): The string to check.
    Returns:
        bool: True if the string is a valid UUID, False otherwise.
    """
    try:
        # Try to create a UUID object
        uuid_obj = uuid.UUID(string)
        return True
    except ValueError:
        return False

class LogMonitor:
    def __init__(self,process_name, tag,targetDevice):
        """
        Initialize the LogMonitor.

        Args:
            tag (str): The tag or keyword to filter logs.
            on_match_callback (function): The function to call when a matching log is found.
            targetDevice (str): The target device to monitor. If None, it will monitor all devices.
        Exceptions:
            Exception: If the process is not found or if the device id is invalid is invalid.
        """

        self.deviceSelector = f"-s {targetDevice} "

        process = subprocess.Popen(
            f"adb {self.deviceSelector} shell ps -A | grep {process_name}",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            text=True
        )
        stdout, stderr = process.communicate()
        print("Raw output:", repr(stdout))
        print("STDERR:", stderr)


        string = [value for value in stdout.split() if value]
        print(string)
        try:
            pid = [value for value in stdout.split() if value][1]
        except IndexError:
            raise Exception("ADB process for given device not found. Check if accessibility service is running.")

        self.tag = tag
        self.running = False
        self.pid = pid
        self.match_futures = {}
        self.loop = asyncio.get_event_loop()
        self.proc = None

    def add_match_future(self, id):
        """Add a future to be set when a matching log is found."""
        self.match_futures[id] = asyncio.Future()
        return self.match_futures[id]

    def start(self):
        """Start monitoring logs."""
        self.running = True
        self.thread = Thread(target=self._monitor_logs)
        self.thread.start()

    def stop(self):
        """Stop monitoring logs.
            This might fail sometimes, even if there was kill requested.
        """
        self.running = False
        # Wait for the thread to finish
        # and kill the adb process
        if self.proc:
            self.proc.send_signal(9)
        if self.thread.is_alive():
            self.thread.join()
        

    def _monitor_logs(self):
        """Internal method to monitor ADB logs."""
        try:
            # Start adb logcat with filter for the tag
            with subprocess.Popen(
                f"adb {self.deviceSelector} logcat --pid {str(self.pid)} -s {self.tag}:D",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                shell=True,
                text=True
            ) as logcat_proc:
                # Continuously read logcat output
                self.proc = logcat_proc
                while self.running:
                    if logcat_proc.poll() is not None:
                        print("ADB logcat process terminated.")
                        break

                    try:
                        
                        # Use select to wait for output
                        rline,_ ,_= select.select([logcat_proc.stdout],[],[],1)
                        # Check if there is data to read
                        if rline:
                            while True:
                                # Read a line from the logcat output
                                line = logcat_proc.stdout.readline()
                                if not line:  # If no more lines are available, break out
                                    break
                                print(f"Matching log: {line.strip()}")

                                # Check if the line contains the tag
                                tokens = line.split()
                                if(len(tokens) <= 6):
                                    continue
                                print(f"Matched ID: {tokens[6]}")
                                if tokens and is_valid_uuid(tokens[6]):
                                    id = uuid.UUID(tokens[6])
                                    if id in self.match_futures:
                                        future = self.match_futures[id]
                                        # Set the future result with the log line
                                        asyncio.run_coroutine_threadsafe(self._set_future_result(future, line), self.loop)
                        else:
                            time.sleep(0.1)  # Wait for new logs

                    except Exception as e:
                        print(f"Error processing log line: {e}")
                logcat_proc.kill()
        except Exception as e:
            print(f"Error in log monitoring: {e}")

    async def _set_future_result(self, future, line):
        """Helper function to safely set future result inside the main event loop."""
        if not future.done():
            future.set_result(line)






def execute(command, arguments, std_output_redirect=None):
    """
    Execute a command in a subprocess and handle output redirection.
    Args:
        command (str): The command to execute.
        arguments (str): The arguments for the command.
        std_output_redirect (str, optional): If provided, the output will be redirected to this file.
    """
    try:
        # Set up the command
        full_command = f"{command} {arguments}"
        # Execute the process
        process = subprocess.Popen(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        # Wait for the process to complete and get the output
        stdout, stderr = process.communicate()

        # Handle redirection
        if std_output_redirect:
            with open(std_output_redirect, "wb") as file:
                file.write(stdout)
        else:
            # Print the output
            print("Output:", stdout.decode("utf-8"))

        # Print errors, if any
        if stderr:
            print("Error:", stderr.decode("utf-8"))

    except Exception as e:
        print(f"An error occurred: {e}")


async def broadcastAdb(command,broadcastArgs,logMonitor : LogMonitor):
    """
    Broadcast a command to the device using ADB.
    Args:
        command (str): The command to broadcast.
        broadcastArgs (str): The arguments for the command.
        logMonitor (LogMonitor): The LogMonitor instance to use.
    """
    # Generate a unique ID for the broadcast
    guid = uuid.uuid4()
    # Add a future to wait for the log message
    future = logMonitor.add_match_future(guid)
    # Create awaitable future
    future = asyncio.ensure_future(future)
    # Execute the ADB command
    execute("adb", f"{logMonitor.deviceSelector} shell am broadcast -a com.tenshite.inputmacros.{command} {broadcastArgs} --es id {guid}")
    # Print to the console
    print(f"Broadcasted com.tenshite.inputmacros.{command} {broadcastArgs} --es id {guid}")
    # Wait for the future to be set
    await future
    # Return the result from the future
    return future.result()

def takeScreenshot(deviceName:str,filename:str):
    """
    Take a screenshot of the device screen using ADB.
    Args:
        deviceName (str): The name of the device to take a screenshot of.
        filename (str): The name of the file to save the screenshot as.
    """
    if deviceName == "":
        raise Exception("Device name is empty")  

    # Generate the ADB command to take a screenshot
    args = ["adb", "-s", deviceName, "exec-out", "screencap", "-p"]
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for the process to complete and get the output
    stdout, stderr = process.communicate()
    # Check if there were any errors
    if(not os.path.exists(f"./.cache{deviceName}")):
        os.makedirs(f"./.cache{deviceName}")

    # Write the binary output (screenshot data) to the file
    with open(f"./.cache{deviceName}/{filename}.png", 'wb') as f:
        f.write(stdout)
    # Print the output to the console
    print(f"Screenshot saved to ./.cache{deviceName}/{filename}.png")