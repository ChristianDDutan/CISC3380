import os
import shlex
import signal

class Job:
    def __init__(self, pid, command, background):
        self.pid = pid
        self.command = command
        self.background = background
        self.status = "Running"

jobs = {}  # Job directory
next_job_id = 1  # Fixed typo (removed 's')

def show_jobs():
    """Displays the currently tracked background jobs."""
    # First, quickly check if any finished while we weren't looking
    reap_children()
    
    if not jobs:
        print("No background jobs.")
        return
        
    for job_id, job in jobs.items():
        print(f"[{job_id}]  {job.status}    {job.command}")

def parse_command(line):
    """Parses input line into arguments and detects background operator (&)."""
    args = shlex.split(line)
    background = False

    if args and args[-1] == "&":
        background = True
        args.pop()

    return args, background

def reap_children():
    """Reaps zombie processes and removes them from the jobs list."""
    while True:
        try:
            # WNOHANG means don't block; check if any child exited
            pid, status = os.waitpid(-1, os.WNOHANG)

            if pid == 0:
                break

            # Find the job with this PID and remove it
            to_remove = [jid for jid, job in jobs.items() if job.pid == pid]
            for jid in to_remove:
                print(f"\n[{jid}]  Done    {jobs[jid].command}")
                del jobs[jid]

        except ChildProcessError:
            break

def run_external(args, background):
    """Forks a child process to execute external shell commands."""
    global next_job_id
    pid = os.fork()

    if pid == 0:
        # Child Process
        try:
            os.execvp(args[0], args)
        except FileNotFoundError:
            print(f"myshell: {args[0]}: command not found")
            os._exit(1)
    else:
        # Parent Process
        if background:
            # Track the background job
            job = Job(pid, " ".join(args) + " &", True)
            jobs[next_job_id] = job
            print(f"[{next_job_id}] {pid}")
            next_job_id += 1
        else:
            # Foreground job: Parent must wait for it to complete
            try:
                os.waitpid(pid, 0)
            except OSError:
                pass

def main():
    while True:
        # Automatically clean up completed background jobs before showing prompt
        reap_children()
        
        try:
            line = input("myshell> ")
        except (EOFError, KeyboardInterrupt):
            print("\nexit")
            break

        if not line.strip():
            continue

        args, background = parse_command(line)
        if not args:
            continue

        # Built-in command: exit
        if args[0] == "exit":
            break

        # Built-in command: cd
        elif args[0] == "cd":
            if len(args) < 2:
                print("myshell: cd: missing argument")
            else:
                try:
                    os.chdir(args[1])
                except FileNotFoundError:
                    print(f"myshell: cd: no such directory: {args[1]}")
            continue

        # Built-in command: jobs
        elif args[0] == "jobs":
            show_jobs()
            continue

        # Built-in command: kill
        elif args[0] == "kill":
            if len(args) < 2:
                print("myshell: kill: missing job ID")
                continue
            try:
                job_id = int(args[1])
                if job_id in jobs:
                    os.kill(jobs[job_id].pid, signal.SIGTERM)
                    print(f"Signaled job [{job_id}] to terminate.")
                else:
                    print(f"myshell: kill: [{job_id}]: no such job")
            except ValueError:
                print("myshell: kill: arguments must be process or job IDs")
            continue

        # External commands (ls, pwd, grep, sleep, etc.)
        run_external(args, background)

if __name__ == "__main__":
    main()

