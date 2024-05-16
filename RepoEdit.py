from github import Github
import os
import yaml

def process_repository(repo, excluded_repos, namespace_to_match, str_to_replace, replacement_string, change_repo_name):
    print(f"Processing repository: {repo.name}")

    if repo.name in excluded_repos:
        print(f"Skipping repository: {repo.name} as it's excluded.")
        return

    if not check_namespace(repo, namespace_to_match):
        return

    repo_contents = repo.get_contents("")
    deploy_yml_file = get_deploy_yml_file(repo)

    for file in repo_contents:
        if file.name in file_exclusions:
            print(f"Skipping {file.name} as it's in the exclusions list.")
            continue

        process_file(repo, file, deploy_yml_file, str_to_replace, replacement_string, change_repo_name)

def check_namespace(repo, namespace_to_match):
    print("Checking namespace...")
    if not namespace_to_match:
        print("No namespaces to match. Proceeding...")
        return True

    deploy_yml_content = get_deploy_yml_content(repo)
    if deploy_yml_content:
        argo_app = deploy_yml_content.get("jobs", {}).get("Deploy-To-GKE", {}).get("with", {}).get("ARGO_APP")
        if argo_app not in namespace_to_match:
            print(f"Namespace '{argo_app}' does not match, moving to the next repository.")
            return False
    else:
        print("No deploy YAML content found. Moving to the next repository.")
        return False

def get_deploy_yml_file(repo):
    print("Fetching deploy YAML file...")
    deploy_yml_path = ".github/workflows/Deploy.yml"
    try:
        return repo.get_contents(deploy_yml_path)
    except Exception as e:
        print(f"No Deploy.yml found in the repository: {e}")
        return None

def get_deploy_yml_content(repo):
    print("Fetching deploy YAML content...")
    deploy_yml_file = get_deploy_yml_file(repo)
    if deploy_yml_file:
        return yaml.safe_load(deploy_yml_file.decoded_content)
    else:
        return {}

def process_file(repo, file, deploy_yml_file, str_to_replace, replacement_string, change_repo_name):
    print(f"Processing file: {file.name}")
    print(f"Change repo name: {change_repo_name}")  # Debugging statement
    try:
        file_content = repo.get_contents(file.path).decoded_content.decode()
        if str_to_replace in file_content:
            print(f"String '{str_to_replace}' found in {file.name}. Replacing...")
            new_file_content = file_content.replace(str_to_replace, replacement_string)
            repo.update_file(file.path, f"Replace {str_to_replace} with {replacement_string}", new_file_content, file.sha)
            print(f"Replaced in {file.name}")

            if change_repo_name:
                print(f"Repo name before change: {repo.name}")  # Debugging statement
                if str_to_replace in repo.name:
                    print(f"Changing repository name...")
                    new_repo_name = repo.name.replace(str_to_replace, replacement_string)
                    repo.edit(name=new_repo_name)
                    print(f"Repository name changed to: {new_repo_name}")
                else:
                    print(f"String {str_to_replace} not found in repository name: {repo.name}")
        else:
            print(f"The string {str_to_replace} is not found in {file.name}")
    except Exception as e:
        print(f"An error occurred while processing {file.name}: {e}")

def main():
    str_to_replace = os.environ.get('STR_TO_REPLACE')
    replacement_string = os.environ.get('REPLACEMENT_STRING')
    excluded_repos = os.environ.get('EXCLUDED_REPOS', '').split(',')
    namespace_to_match = os.environ.get('NAME_SPACE', '').split(',')
    file_exclusions = os.environ.get('FILE_EXCLUSIONS', '').split(',')
    access_token = os.environ.get('GITHUB_TOKEN')

    g = Github(access_token)

    for repo in g.get_user().get_repos(type="owner"):
        process_repository(repo, excluded_repos, namespace_to_match, str_to_replace, replacement_string, True)  # Pass True for change_repo_name

if __name__ == "__main__":
    main()
