import os

def main():
#hi, this the next line will read out PID
    print("PID: ", os.getpid())

#and this next line wil out put to the screen the PPID
    print("PPID: ", os.getppid())

# nextStep environment variable
    print("Environment Variable: ", os.environ["HOME"])

for key, value in os.environ.items():
    print(f"{key}={value}")

# moving on to the file descriptor
    print("Open File Descriptors:")
    fds = os.listdir("/proc/self/fd")

    for fd in fds:
        print(fd)
# wrapping it in the main guard
if __name__ == "__main__":
    main()


