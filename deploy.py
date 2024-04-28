import asyncio
import os
import subprocess
import sys

async def deploy_function(func_name, dir_path):
    # Construct the gcloud command for deploying the function with all specified flags
    cmd = [
        "gcloud", "functions", "deploy", func_name,
        "--gen2",
        "--region", "us-west1",
        "--runtime", "python312",
        "--trigger-http",
        "--entry-point", "handler",
        "--source", dir_path,
        "--allow-unauthenticated",
    ]
    
    # Check if .env.yaml exists in the directory and add it to the command if it does
    env_vars_file = os.path.join(dir_path, ".env.yaml")
    if os.path.exists(env_vars_file):
        cmd.extend(["--env-vars-file", env_vars_file])

    # Run the gcloud command
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Wait for the deployment to finish and capture the output
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"Deployed {func_name} successfully")
    else:
        print(f"Error deploying {func_name}: {stderr.decode()}")

async def main():
    # Path to the directory containing all function subdirectories
    functions_dir = "."  # Adjust this path
    os.chdir(functions_dir)

    # List all subdirectories in the functions directory
    dirs = [d for d in os.listdir('.') if os.path.isdir(d)]
    tasks = []

    # Check if specific function names are provided as command-line arguments
    specific_funcs = sys.argv[1:]  # Skip the first argument, which is the script name

    for dir in dirs:
        func_name = dir  # Assuming directory name is the function name
        # If specific functions are specified, only deploy those; otherwise, deploy all
        if not specific_funcs or func_name in specific_funcs:
            tasks.append(deploy_function(func_name, os.path.join(functions_dir, dir)))

    # Run deployment tasks asynchronously
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())