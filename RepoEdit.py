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
        print(f"Scanning file: {file.name}")  # Debugging statement
        if file.name in file_exclusions:
            print(f"Skipping {file.name} as it's in the exclusions list.")
            continue

        process_file(repo, file, deploy_yml_file, str_to_replace, replacement_string, change_repo_name)
