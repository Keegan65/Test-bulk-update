from github import Github
import os
import yaml

# Get inputs from environment variables
STR_TO_REPLACE = os.getenv('STR_TO_REPLACE', '-this-one-officer')
REPLACEMENT_STRING = os.getenv('REPLACEMENT_STRING', 'arrested')
REPOS_TO_CHANGE = os.getenv('REPOS_TO_CHANGE', '').split(',')
EXCLUDED_REPOS = os.getenv('EXCLUDED_REPOS', '').split(',')
NAMESPACE_TO_MATCH = os.getenv('NAME_SPACE').split(',')
FILE_EXCLUSIONS = os.getenv('FILE_EXCLUSIONS', '').split(',')
CHANGE_REPO_NAME = os.getenv('CHANGE_REPO_NAME', 'false').lower() == 'false'
ACCESS_TOKEN = os.getenv('GITHUB_TOKEN')

# Initialize the GitHub instance
g = Github(ACCESS_TOKEN)

# Iterate through all repositories owned by the user
for repo in g.get_user().get_repos(type="owner"):
    print(f"Processing repository: {repo.name}")

    # Check if the repository should be excluded
    if repo.name in EXCLUDED_REPOS:
        print(f"Skipping repository: {repo.name} as it's excluded.")
        continue

    # Fetch all content from the repo's root directory
    repo_contents = repo.get_contents("")

    # Check if the repository has a Deploy.yml file under .github/workflows
    deploy_yml_path = ".github/workflows/Deploy.yml"
    deploy_yml_file = None
    try:
        deploy_yml_file = repo.get_contents(deploy_yml_path)
    except Exception as e:
        print(f"No Deploy.yml found in the repository: {e}")
        continue  # Move to the next repository

    # If namespaces are provided, check if the repository matches any of them
    deploy_yml_content = None
    if NAMESPACE_TO_MATCH != ['']:  # Check if NAMESPACE_TO_MATCH is not an empty string
        if deploy_yml_file:
            deploy_yml_content = yaml.safe_load(deploy_yml_file.decoded_content)
            argo_app = deploy_yml_content.get("jobs", {}).get("Deploy-To-GKE", {}).get("with", {}).get("ARGO_APP")
            if argo_app not in NAMESPACE_TO_MATCH:
                print(f"Namespace '{argo_app}' does not match, moving to the next repository.")
                continue  # Move to the next repository
    else:
        print("No namespaces provided, skipping namespace matching.")
        

    # Process only specific repositories if provided
    if REPOS_TO_CHANGE:
        if repo.name not in REPOS_TO_CHANGE:
            print(f"Skipping repository: {repo.name} as it's not in the specified repositories list.")
            continue
    else:
        print("No specific repositories provided, processing all repositories.")

    # Iterate through each file in the repository
    for file in repo_contents:
        print(f"Processing file: {file.name}")

        # Skip processing excluded files
        if file.name in FILE_EXCLUSIONS:
            print(f"Skipping {file.name} as it's in the exclusions list.")
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

                # Change repository name if specified
                if CHANGE_REPO_NAME and STR_TO_REPLACE in repo.name:
                    new_repo_name = repo.name.replace(STR_TO_REPLACE, REPLACEMENT_STRING)
                    repo.edit(name=new_repo_name)
                    print(f"Repository name changed to: {new_repo_name}")
            else:
                print(f"The string {STR_TO_REPLACE} is not found in {file.name}")
        except Exception as e:
            print(f"An error occurred while processing {file.name}: {e}")
