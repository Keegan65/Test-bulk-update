from github import Github
import os
import yaml

STR_TO_REPLACE = "this one officer"
REPLACEMENT_STRING = "arrested"
ACCESS_TOKEN = os.getenv('GITHUB_TOKEN')
NAMESPACE_TO_MATCH = "finance"  # Update with your namespace

# Initialize the GitHub instance
g = Github(ACCESS_TOKEN)

# Iterate through all repositories owned by the user
for repo in g.get_user().get_repos(type="owner"):
    print("Processing repository:", repo.name)
    try:
        # Fetch all contents from the repo's root directory
        repo_contents = repo.get_contents("")

        # Check if a .github directory exists
        github_dir = next((content for content in repo_contents if content.name == ".github"), None)
        if github_dir:
            # Fetch all contents from the .github directory
            github_contents = repo.get_contents(".github")

            # Check if a deploy.yaml file exists
            deploy_yml_file = next((content for content in github_contents if content.name.lower() == "deploy.yaml"), None)
            if deploy_yml_file:
                # Fetch the content of deploy.yaml
                deploy_yml_content = yaml.safe_load(deploy_yml_file.decoded_content)

                # Check if the deploy.yaml content contains argo_app with the specified namespace
                if deploy_yml_content.get("argo_app", "").lower() == "your_namespace":
                    # Iterate through each file in the repository
                    for file in repo_contents:
                        if file.name.lower() == "build.gradle":
                            print("Skipping build.gradle")
                            continue  # Skip processing build.gradle files
                        print(file.name)
                        try:
                            # Fetch the file content
                            file_content = repo.get_contents(file.path).decoded_content.decode()

                            # Check if the string to replace exists in the file content
                            if STR_TO_REPLACE in file_content:
                                # Replace the string with the replacement string
                                new_file_content = file_content.replace(STR_TO_REPLACE, REPLACEMENT_STRING)

                                # Commit the updated file content
                                repo.update_file(file.path, f"Replace {STR_TO_REPLACE} with {REPLACEMENT_STRING}", new_file_content, file.sha)
                                print(f"Replaced in {file.name}")
                            else:
                                print(f"The string {STR_TO_REPLACE} is not found in {file.name}")
                        except Exception as e:
                            print(f"An error occurred while processing {file.name}: {e}")
            else:
                print("No deploy.yaml found in the repository")
        else:
            print("No .github directory found in the repository")
    except Exception as e:
        print(f"An error occurred while processing the repository: {e}")
