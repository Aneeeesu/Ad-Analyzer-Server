import subprocess
import uuid
from threading import Thread
import time
import asyncio

from transformers import pipeline
# load pipe

def is_valid_uuid(string):
    try:
        # Try to create a UUID object
        uuid_obj = uuid.UUID(string)
        return True
    except ValueError:
        return False

class LogMonitor:
    def __init__(self,process_name, tag, on_match_callback):
        """
        Initialize the LogMonitor.

        Args:
            tag (str): The tag or keyword to filter logs.
            on_match_callback (function): The function to call when a matching log is found.
        """

        process = subprocess.Popen(
            f"adb shell \"ps -A | grep {process_name}\"",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        stdout, stderr = process.communicate()
        string = [value for value in stdout.decode("utf-8").split(" ") if value]
        pid = [value for value in stdout.decode("utf-8").split(" ") if value][1]

        self.tag = tag
        self.on_match_callback = on_match_callback
        self.running = False
        self.pid = pid
        self.match_futures = {}
        self.loop = asyncio.get_event_loop()

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
        """Stop monitoring logs."""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def _monitor_logs(self):
        """Internal method to monitor ADB logs."""
        try:
            # Start adb logcat with filter for the tag
            with subprocess.Popen(
                ["adb", "logcat", "--pid", str(self.pid),"-s", f"{self.tag}:D"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                text=True
            ) as logcat_proc:
                # Continuously read logcat output
                while self.running:
                    if logcat_proc.poll() is not None:
                        print("ADB logcat process terminated.")
                        break

                    try:
                        line = logcat_proc.stdout.readline()
                        if line:
                            print(f"Matching log: {line.strip()}")
                            self.on_match_callback(line.strip())

                            tokens = line.split()
                            if(len(tokens) <= 6):
                                continue
                            print(f"Matched ID: {tokens[6]}")
                            if tokens and is_valid_uuid(tokens[6]):
                                id = uuid.UUID(tokens[6])
                                if id in self.match_futures:
                                    future = self.match_futures[id]
                                    # Use an async wrapper function
                                    asyncio.run_coroutine_threadsafe(self._set_future_result(future, line), self.loop)
                        else:
                            time.sleep(0.1)  # Wait for new logs
                    except Exception as e:
                        print(f"Error processing log line: {e}")
        except Exception as e:
            print(f"Error in log monitoring: {e}")

    async def _set_future_result(self, future, line):
        """Helper function to safely set future result inside the main event loop."""
        if not future.done():
            future.set_result(line)






def execute(command, arguments, std_output_redirect=None):
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
    guid = uuid.uuid4()
    future = logMonitor.add_match_future(guid)
    future = asyncio.ensure_future(future)
    execute("adb", f"shell am broadcast -a com.tenshite.inputmacros.{command} {broadcastArgs} --es id {guid}")
    print(f"Broadcasted com.tenshite.inputmacros.{command} {broadcastArgs} --es id {guid}")
    await future
    return future.result()

def takeScreenshot(filename:str):
    execute("adb", "exec-out screencap -p", f"./cache/{filename}.png")