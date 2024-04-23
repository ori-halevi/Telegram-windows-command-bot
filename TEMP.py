import subprocess

def get_running_processes():
    result = subprocess.run(['tasklist'], stdout=subprocess.PIPE, text=True)
    return result.stdout

print(get_running_processes())
