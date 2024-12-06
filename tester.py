import subprocess
import os
import uuid
from threading import Thread
import time
import asyncio
import select

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
                            
                            if tokens and is_valid_uuid(tokens[6]):
                                id = uuid.UUID(tokens[6])
                                if id in self.match_futures:
                                    self.match_futures[id].set_result(line)
                        else:
                            time.sleep(0.1)  # Wait for new logs
                    except Exception as e:
                        print(f"Error processing log line: {e}")


        except Exception as e:
            print(f"Error in log monitoring: {e}")



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

async def broadcastAdb(command,broadcastArgs,logMonitor):
    guid = uuid.uuid4()
    future = logMonitor.add_match_future(guid)
    execute("adb", f"shell am broadcast -a com.tenshite.inputmacros.{command} {broadcastArgs} --es id {guid}")
    await future
    return future.result()

def open_dm(username):
    execute(
    "adb",
    f"shell am broadcast -a com.tenshite.inputmacros.TikTok.OpenDMs --es username '{username}'"
)


def goToHome():
    execute("adb", "shell am broadcast -a com.tenshite.inputmacros.TikTok.NavigateToHome")
def goToMessages():
    execute("adb", "shell am broadcast -a com.tenshite.inputmacros.TikTok.NavigateToMessages")
def goToProfile():
    execute("adb", "shell am broadcast -a com.tenshite.inputmacros.TikTok.NavigateToProfile")
def takeScreenshot():
    execute("adb", "exec-out screencap -p", "screen.png")



async def main():
    monitor = LogMonitor("com.tenshite.inputmacros","AppControllerEvent", lambda x: print(x))
    monitor.start()
    await broadcastAdb("TikTok.OpenDMs","--es username aneeeesu",monitor)
    await broadcastAdb("TikTok.SendDM","--es message NAAAAH",monitor)
    await broadcastAdb("TikTok.NavigateToHome","",monitor)
    monitor.stop()

if __name__ == "__main__":
   asyncio.run(main())
