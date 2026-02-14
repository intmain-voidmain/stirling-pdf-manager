import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import webbrowser
import time # Import time for potential delays or checks

class StirlingPDFManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Stirling PDF Docker Manager")
        self.geometry("600x450") # Slightly increased height for status indicator

        self.container_name = "stirling-pdf"
        self.create_widgets()
        self.update_status_indicator() # Initial status check
        self._periodic_status_check() # Start periodic checks

    def create_widgets(self):
        # Frame for buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.run_button = tk.Button(button_frame, text="Run Stirling PDF", command=self.run_stirling_pdf)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop Stirling PDF", command=self.stop_stirling_pdf)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        # New button to open in browser
        self.open_button = tk.Button(button_frame, text="Open in Browser", command=self.open_stirling_pdf_in_browser)
        self.open_button.pack(side=tk.LEFT, padx=5)

        # Status Indicator Frame and Canvas
        status_frame = tk.Frame(self)
        status_frame.pack(pady=5)

        tk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_canvas = tk.Canvas(status_frame, width=20, height=20, bg=self.cget('bg'), highlightthickness=0)
        self.status_canvas.pack(side=tk.LEFT, padx=5)
        self.status_circle = self.status_canvas.create_oval(5, 5, 15, 15, fill="gray", outline="gray")


        # ScrolledText for output
        self.output_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, width=70, height=15)
        self.output_text.pack(pady=10)
        self.output_text.insert(tk.END, "Welcome to Stirling PDF Docker Manager!\n")
        self.output_text.insert(tk.END, "Click 'Run Stirling PDF' to start the container.\n")
        self.output_text.insert(tk.END, "Click 'Stop Stirling PDF' to stop it.\n\n")

        # Configure tag for clickable links
        self.output_text.tag_config("link", foreground="blue", underline=1)
        self.output_text.tag_bind("link", "<Button-1>", self._open_link)
        self.output_text.tag_bind("link", "<Enter>", lambda e: self.output_text.config(cursor="hand2"))
        self.output_text.tag_bind("link", "<Leave>", lambda e: self.output_text.config(cursor="arrow"))

    def _open_link(self, event):
        index = self.output_text.index(f"@{event.x},{event.y}")
        tag_ranges = self.output_text.tag_ranges("link")
        for i in range(0, len(tag_ranges), 2):
            start = tag_ranges[i]
            end = tag_ranges[i+1]
            if self.output_text.compare(start, "<=", index) and self.output_text.compare(index, "<", end):
                link = self.output_text.get(start, end)
                webbrowser.open_new(link)
                return

    def _execute_docker_command(self, command, success_message, error_message, link_to_make_clickable=None):
        self.output_text.insert(tk.END, f"Executing: {' '.join(command)}\n")
        self.output_text.see(tk.END)
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            self.output_text.insert(tk.END, success_message + "\n")
            self.output_text.insert(tk.END, result.stdout + "\n")
            if link_to_make_clickable:
                start_index = self.output_text.search(link_to_make_clickable, tk.END+"-1c linestart", stopindex=tk.INSERT)
                if start_index:
                    end_index = f"{start_index}+{len(link_to_make_clickable)}c"
                    self.output_text.tag_add("link", start_index, end_index)
        except subprocess.CalledProcessError as e:
            self.output_text.insert(tk.END, error_message + "\n")
            self.output_text.insert(tk.END, f"Error (stderr): {e.stderr}\n")
            self.output_text.insert(tk.END, f"Error (stdout): {e.stdout}\n")
        except FileNotFoundError:
            self.output_text.insert(tk.END, "Error: Docker command not found. Is Docker installed and in your PATH?\n")
        finally:
            self.output_text.see(tk.END)
            self.update_status_indicator() # Update status after command execution

    def run_stirling_pdf(self):
        self.output_text.insert(tk.END, "Attempting to run/start Stirling PDF container...\n")
        self.output_text.see(tk.END)
        # Check if container exists first to decide between 'run' and 'start'
        check_command = ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.ID}}"]
        try:
            container_id = subprocess.run(check_command, capture_output=True, text=True, check=True).stdout.strip()
            if container_id:
                # Container exists, try to start it
                start_command = ["docker", "start", self.container_name]
                threading.Thread(target=self._execute_docker_command,
                                 args=(start_command,
                                       "Stirling PDF container started successfully (or was already running). Access at http://localhost:8080",
                                       "Failed to start existing Stirling PDF container.",
                                       "http://localhost:8080")).start()
            else:
                # Container does not exist, run a new one
                run_command = [
                    "docker", "run", "-d",
                    "--name", self.container_name,
                    "-p", "8080:8080",
                    "-v", "./stirling-data:/configs",
                    "stirlingtools/stirling-pdf:latest"
                ]
                threading.Thread(target=self._execute_docker_command,
                                 args=(run_command,
                                       "Stirling PDF container created and started successfully. Access at http://localhost:8080",
                                       "Failed to run new Stirling PDF container.",
                                       "http://localhost:8080")).start()
        except subprocess.CalledProcessError as e:
            self.output_text.insert(tk.END, "Error checking for existing container.\n")
            self.output_text.insert(tk.END, f"Error (stderr): {e.stderr}\n")
            self.output_text.insert(tk.END, f"Error (stdout): {e.stdout}\n")
        except FileNotFoundError:
            self.output_text.insert(tk.END, "Error: Docker command not found. Is Docker installed and in your PATH?\n")
        finally:
            self.output_text.see(tk.END)
            # Status update will be triggered by _execute_docker_command's finally block


    def stop_stirling_pdf(self):
        stop_command = ["docker", "stop", self.container_name]
        threading.Thread(target=self._execute_docker_command,
                         args=(stop_command,
                               "Stirling PDF container stopped successfully.",
                               "Failed to stop Stirling PDF container.")).start()

    def open_stirling_pdf_in_browser(self):
        self.output_text.insert(tk.END, "Opening Stirling PDF in browser: http://localhost:8080\n")
        webbrowser.open_new_tab("http://localhost:8080")
        self.output_text.see(tk.END)

    def check_stirling_pdf_status(self):
        try:
            # Check if container exists
            check_exists_command = ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.ID}}"]
            exists_result = subprocess.run(check_exists_command, capture_output=True, text=True, check=True)
            if not exists_result.stdout.strip():
                return None # Container does not exist

            # Check if container is running
            check_running_command = ["docker", "inspect", "--format", "{{.State.Running}}", self.container_name]
            running_result = subprocess.run(check_running_command, capture_output=True, text=True, check=True)
            if running_result.stdout.strip() == "true":
                return True # Container is running
            else:
                return False # Container exists but is not running
        except subprocess.CalledProcessError:
            return None # Docker command error, possibly container not found or other issue
        except FileNotFoundError:
            return None # Docker not installed or not in PATH

    def update_status_indicator(self):
        status = self.check_stirling_pdf_status()
        if status is True:
            color = "green"
            self.run_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.open_button.config(state=tk.NORMAL)
        elif status is False:
            color = "red"
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.open_button.config(state=tk.DISABLED)
        else: # None, meaning container not found or docker error
            color = "gray"
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.open_button.config(state=tk.DISABLED)
        self.status_canvas.itemconfig(self.status_circle, fill=color, outline=color)

    def _periodic_status_check(self):
        self.update_status_indicator()
        self.after(5000, self._periodic_status_check) # Check every 5 seconds

if __name__ == "__main__":
    app = StirlingPDFManager()
    app.mainloop()