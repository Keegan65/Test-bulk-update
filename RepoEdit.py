from github import Github
import os

STR_TO_REPLACE = "abcdefghijk"
REPLACEMENT_STRING = "deleted"
ACCESS_TOKEN = os.getenv('BULK_TOKEN')

# Initialize the GitHub instance
g = Github(ACCESS_TOKEN)

try:
    # Get the repository
    repo = g.get_repo("Repo2")

    # Fetch all content from the repo's root directory
    repo_contents = repo.get_contents("")

    # Iterate through each file in the repository
    for file in repo_contents:
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

except Exception as ex:
    print(f"An error occurred: {ex}")
