import requests

DELETE_PROFILE_URL = "https://flask-server-thesis-ssa7.onrender.com/delete_profile"

def delete_profile(profile):
    response = requests.post(DELETE_PROFILE_URL, json={"profile": profile})

    if response.status_code == 200:
        print(f"✅ Successfully deleted profile '{profile}'.")
    else:
        print(f"❌ Failed to delete profile '{profile}': {response.status_code} - {response.text}")

if __name__ == "__main__":
    profile_name = input("Enter the profile name to delete: ").strip()
    delete_profile(profile_name)
