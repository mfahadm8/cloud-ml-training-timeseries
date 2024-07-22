import subprocess

def run_script_in_docker():
    try:
        result = subprocess.run(
            ["docker", "build", "-t", "training_script", "."],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)

        result = subprocess.run(
            ["docker", "run", "--rm", "training_script"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        # Check output for expected columns
        output_lines = result.stdout.split("\n")
        if any("id" in line and "eom" in line and "w" in line for line in output_lines):
            return True, "Runtime checks passed"
        else:
            return False, "Output does not contain required columns (id, eom, w)"
    except subprocess.CalledProcessError as e:
        return False, f"Runtime Error: {e.output}"

# Example usage
is_valid, message = run_script_in_docker()
print(message)
