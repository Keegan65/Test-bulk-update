from github import Github
import os
import yaml

STR_TO_REPLACE = "-this-one-officer"
REPLACEMENT_STRING = "arrested"
ACCESS_TOKEN = os.getenv('GITHUB_TOKEN')
NAMESPACE_TO_MATCH = "finance"  # Update with your namespace

# Initialize the GitHub instance
g = Github(ACCESS_TOKEN)

# Iterate through all repositories owned by the user
for repo in g.get_user().get_repos(type="owner"):
    print(f"Processing repository: {repo.name}")

    # Check if the repository has a Deploy.yml file under .github/workflows
    deploy_yml_path = ".github/workflows/Deploy.yml"
    deploy_yml_file = None
    try:
        deploy_yml_file = repo.get_contents(deploy_yml_path)
    except Exception as e:
        print(f"No Deploy.yml found in the repository: {e}")
        continue  # Move to the next repository

    # If Deploy.yml exists, parse its contents and compare the namespace
    deploy_yml_content = yaml.safe_load(deploy_yml_file.decoded_content)
    argo_app = deploy_yml_content.get("jobs", {}).get("Deploy-To-GKE", {}).get("with", {}).get("ARGO_APP")
    if argo_app != NAMESPACE_TO_MATCH:
        print(f"Namespace '{NAMESPACE_TO_MATCH}' does not match, moving to the next repository.")
        continue  # Move to the next repository

    # Fetch all content from the repo's root directory
    repo_contents = repo.get_contents("")

    # Iterate through each file in the repository
    for file in repo_contents:
        print(f"Processing file: {file.name}")

        # Skip processing build.gradle files
        if file.name.lower() == "build.gradle":
            print("Skipping build.gradle")
            continue

        try:
            # Fetch the file content
            file_content = repo.get_contents(file.path).decoded_content.decode()

            # Check if the string to replace exists in the file content
            if STR_TO_REPLACE in file_content:
                # Replace the string with the replacement string
                new_file_content = file_content.replace(STR_TO_REPLACE, REPLACEMENT_STRING)

                # Commit the updated file content directly to the default branch
                repo.update_file(file.path, f"Replace {STR_TO_REPLACE} with {REPLACEMENT_STRING}", new_file_content, file.sha)
                print(f"Replaced in {file.name}")

                # Check if the repository name contains the string to replace
                if STR_TO_REPLACE in repo.name:
                    new_repo_name = repo.name.replace(STR_TO_REPLACE, REPLACEMENT_STRING)
                    repo.edit(name=new_repo_name)
                    print(f"Repository name changed to: {new_repo_name}")
            else:
                print(f"The string {STR_TO_REPLACE} is not found in {file.name}")
        except Exception as e:
            print(f"An error occurred while processing {file.name}: {e}")
