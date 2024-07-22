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
        
        # Check output for expected columns
        output_lines = result.stdout.split("\n")
        if any("id" in line and "date" in line and "w" in line for line in output_lines):
            return True, "Runtime checks passed"
        else:
            return False, "Output does not contain required columns (id, eom, w)"
    except subprocess.CalledProcessError as e:
        return False, f"Runtime Error: {e.output}"
