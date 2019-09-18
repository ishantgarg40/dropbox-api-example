import requests
import json
import time
from pprint import pprint
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

BASE_URL = "https://api.dropboxapi.com/2"

class GetCompleteDropBoxInfo(object):
    
    def __init__(self, token: dict):
        # access token, team, url
        self.access_token = token["access_token"]
        self.team_management_token = token["team_management_token"]

    def get_team_files(self):
        # some debugging prints
        print("A<--------------------------------------------------------------->A")
        url = f"{BASE_URL}/files/list_folder"
        param = {
                        "path": "",
                        "recursive": True,

                    }
        while True:
            try:
                response = requests.post(url,
                    headers = {
                    "Content-Type" : "application/json",
                    "Authorization" : f"Bearer {self.access_token}",
                    "Dropbox-API-Select-Admin" : 'dbmid:AAA9e41n7iJALbwB_X8NOp7cx4t3M2xfjLs',
                    "Dropbox-API-Path-Root" : json.dumps({
                        ".tag" : "root",
                        "root" : "6203474896"
                    })
                    },
                    data = json.dumps(param)
                    )
                result = response.json()
                yield result
                if result.get("has_more"):
                        cursor = result["cursor"]
                        url = f'{url}/continue' if "/continue" not in url else url
                        param = {"cursor": cursor}
                else:
                    break
            
            except Exception as e:
                return
    def get_shared_files(self):
        # some debugging prints
        print("B<------------------------------------------------------------------------------------------->B")
        response = requests.post(f"{BASE_URL}/team/members/list",
        data = json.dumps({
        
        "limit" : 100,
        "include_removed" : False
        
        }),

        headers = {
            "Content-Type" : "application/json",
            "Authorization" : f"Bearer {self.access_token}"
        }
        
        )
        all_member_info = response.json()
        team_member_ids = []
        for info in all_member_info['members']:
            team_member_ids.append(info.get("profile",{}).get("team_member_id"))
        print(team_member_ids)
        for mem_id in team_member_ids:
            try:
                response = requests.post(f"{BASE_URL}/sharing/list_received_files",
                headers = {
                    "Content-Type" : "application/json",
                    "Authorization" : f"Bearer {self.access_token}",
                    "Dropbox-API-Select-User" : f"{mem_id}"

                },
                data = json.dumps({
                    "actions" : []
                })
                )
                result =  response.json()
                if result["entries"] == []:
                    return
                yield result
            except Exception as e:
                return
    
    def get_member_files(self):
        # some debugging prints
        print("C<-------------------------------------------------------------------------------------------------->C")
        response = requests.post(f"{BASE_URL}/team/members/list",
        data = json.dumps({
        
        "limit" : 100,
        "include_removed" : False
        
        }),

        headers = {
            "Content-Type" : "application/json",
            "Authorization" : f"Bearer {self.access_token}"
        }
        
        )
        all_member_info = response.json()
        team_member_ids = []
        for info in all_member_info['members']:
            team_member_ids.append([info.get("profile",{}).get("team_member_id"),info.get("profile",{}).get("member_folder_id")])
        
        print(team_member_ids)
        for member_id,folder_id in team_member_ids:
            url = f"{BASE_URL}/files/list_folder"
            param = {
                        "path": "",
                        "recursive": True,
                        "limit" : 5
                    }
            while True:
                try:
                    response = requests.post(url,
                    headers = {
                    "Content-Type" : "application/json",
                    "Authorization" : f"Bearer {self.access_token}",
                    "Dropbox-API-Select-User" : member_id,
                    "Dropbox-API-Path-Root" : json.dumps({ 
                        ".tag" : "namespace_id",
                        "namespace_id" : folder_id
                    })
                    },
                    data = json.dumps(param)
                    )
                    result = response.json()
                    yield result
                    if result.get("has_more"):
                        cursor = result["cursor"]
                        url = f'{url}/continue' if "/continue" not in url else url
                        param = {"cursor": cursor}
                    else:
                        break
                except Exception as e:
                    return 




fetch_data = GetCompleteDropBoxInfo(
    {
    "access_token" : "<Your Access Token Here>",
    "team_management_token" : "<Your Team Managemant Token Here>"
}
)



tasks = [fetch_data.get_member_files,fetch_data.get_team_files,fetch_data.get_shared_files]

def call_task(function):
    return function()


start = time.time()
with ThreadPoolExecutor(max_workers = 8) as executor:
    future_to_task = { executor.submit(call_task , task) : task for task in tasks }
    for future in as_completed(future_to_task):
        data = future_to_task[future]
        try:
            for i in future.result():
                pass
        except Exception as e:
            pprint(e)
end = time.time()
pprint(f"{end-start} units of time")
		
        