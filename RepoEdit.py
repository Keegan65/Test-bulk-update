from github import Github
import os

STR_TO_REPLACE = "this one officer"
REPLACEMENT_STRING = "arrested"
ACCESS_TOKEN = os.getenv('GITHUB_TOKEN')
NAMESPACE_TO_MATCH = "finance"  # Update with your namespace

# Initialize the GitHub instance
g = Github(ACCESS_TOKEN)

# Iterate through all repositories owned by the user
for repo in g.get_user().get_repos(type="owner"):
    print(f"Processing repository: {repo.name}")

    # Check if the repository has a deploy.yaml file
    deploy_yaml_path = "deploy.yaml"
    deploy_yaml_file = None
    try:
        deploy_yaml_file = repo.get_contents(deploy_yaml_path)
    except Exception as e:
        print(f"No deploy.yaml found in the repository: {e}")
        continue  # Move to the next repository

    # If deploy.yaml exists, parse its contents and compare the namespace
    deploy_yaml_content = yaml.safe_load(deploy_yaml_file.decoded_content)
    argo_app = deploy_yaml_content.get("jobs", {}).get("Deploy-To-GKE", {}).get("with", {}).get("ARGO_APP")
    if argo_app != NAMESPACE_TO_MATCH:
        print(f"Namespace '{NAMESPACE_TO_MATCH}' does not match, moving to the next repository.")
        continue  # Move to the next repository

    # Fetch all content from the repo's root directory
    repo_contents = repo.get_contents("")

    # Iterate through each file in the repository
    for file in repo_contents:
        print(f"Processing file: {file.name}")
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
            else:
                print(f"The string {STR_TO_REPLACE} is not found in {file.name}")
        except Exception as e:
            print(f"An error occurred while processing {file.name}: {e}")
