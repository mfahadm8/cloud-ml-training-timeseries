import subprocess

def run_script(script_file):
    try:
        result = subprocess.run(
            ["python3", script_file],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        if result.returncode!=0:
            return False, "Runtime checks failed"   
        else:
            return True, "Runtime checks passed"
    except subprocess.CalledProcessError as e:
        return False, f"Runtime Error: {e.output}"
