import twscrape
import asyncio
from twscrape import API

import json
import os
import os.path
from shutil import copytree
from datetime import date

import yaml



# Variables for Creating Directories
date_string = date.today().strftime("%Y%m%d")
temp_data_path = '../tmp'
gdrive_data_path = '../../../verituslabs_gdrive/smm/smm_data/projs/louisiana_state_politics/reference'
platform='twitter'
config = []



# reading config.yaml file
def read_config():
    with open("config.yml", 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

read_config()



# Class to login bot accounts
class AuthInfo:
    def __init__(self, username, password, email, email_password="mail_pass3", cookies=None):
        self.username = username
        self.password = password
        self.email = email
        self.email_password = email_password
        self.cookies = cookies

# All Three Bot Accounts
auth_info_objects = [
    AuthInfo(config['accounts']['account_1']['username'],config['accounts']['account_1']['password'],config['accounts']['account_1']['usermail']),
    AuthInfo(config['accounts']['account_2']['username'],config['accounts']['account_2']['password'],config['accounts']['account_2']['usermail']),
    AuthInfo(config['accounts']['account_3']['username'],config['accounts']['account_3']['password'],config['accounts']['account_3']['usermail'])
]
scraper_api = API()



# Function to Login Bot Accounts
async def login():
    if not os.path.isfile("accounts.db"):
        for each in auth_info_objects:
            await scraper_api.pool.delete_accounts(each.username)
            await scraper_api.pool.add_account(
                username=each.username,
                password=each.password,
                email=each.email,
                email_password=each.email_password,
            )
        await scraper_api.pool.login_all()
        print("Session File Created\n")
    else:
        print("Session File Exists\n")



# Function to create directories to store data
def get_data_export_directory_dict(export_directory_path, platform, subject_username, date_string, filename_keys) -> str:
    os.makedirs(f'{export_directory_path}/{platform}/{subject_username}', exist_ok=True)

    export_directory = {}
    for filename_key in filename_keys:
        export_directory[filename_key] = f"{export_directory_path}/{platform}/{subject_username}/{platform}_{subject_username}_{filename_key}_{date_string}.json"
    return export_directory



# Function to Download User Info
async def download_user_info(username, output_filepath):
    _user_object = await scraper_api.user_by_login(username)
    user_json = _user_object.json()
    with open(output_filepath, "w+") as f:
        f.write(user_json)
    # print(json.dumps(json.loads(_user_object.json()), indent=4))
    return _user_object



# Function to Download Tweets
async def download_tweets(user_id, output_filepath, limit=-1):
    with open(output_filepath, "w+") as f:
        f.write("[")
    is_first = True
    i = 0
    async for tweet in scraper_api.user_tweets(user_id, limit=-1):
        with open(output_filepath, "a+") as f:
            if not is_first:
                f.write(",")
            else:
                with open("object_one.json", "w+") as ff:
                    ff.write(str(tweet.id))
                is_first = False
            f.write(tweet.json())
            i += 1
    with open(output_filepath, "a+") as f:
        f.write("]")
    print(f"Tweets Count: {i}")



# Function to Download Followings Data
async def download_following_profiles(user_id, output_filepath, limit=-1):
    with open(output_filepath, "w+") as f:
        f.write("[")
    is_first = True
    i = 0
    async for tweet in scraper_api.following(user_id, limit=limit):
        with open(output_filepath, "a+") as f:
            if not is_first:
                f.write(",")
            else:
                is_first = False
            f.write(tweet.json())
            i += 1
    with open(output_filepath, "a+") as f:
        f.write("]")
    print(f"Following Count: {i}")



# Function to Download Followers Data
async def download_follower_profiles(user_id, output_filepath, limit=-1):
    with open(output_filepath, "w+") as f:
        f.write("[")
    is_first = True
    i = 0
    async for tweet in scraper_api.followers(user_id, limit=limit):
        with open(output_filepath, "a+") as f:
            if not is_first:
                f.write(",")
            else:
                is_first = False
            f.write(tweet.json())
            i += 1
    with open(output_filepath, "a+") as f:
        f.write("]")
    print(f"Followers Count: {i}")



# Function to Download Latest Tweets Data
async def download_latest_tweets(user_id, output_filepath):    
    with open("Object_one.json") as file:
        data = file.read()

    with open(output_filepath, "w+") as f:
        f.write("[")
    is_first = True
    i = 0
    async for tweet in scraper_api.user_tweets(user_id, limit=-1):
        if str(tweet.id) == str(data):
            break
        with open(output_filepath, "a+") as f:
            if not is_first:
                f.write(",")
            else:
                is_first = False
            f.write(tweet.json())
            i += 1
    with open(output_filepath, "a+") as f:
        f.write("]")
    print(f"Latest Tweets Count: {i}")



# Dumping Followers based on some freshness criteria

# Function to Download Verified Followers Data
async def verified_followers(user_id, output_filepath, limit=-1):
    with open(output_filepath, "w+") as f:
        f.write("[")
    is_first = True
    i = 0
    async for follower in scraper_api.followers(user_id, limit=limit):
        if follower.blue == True:
            with open(output_filepath, "a+") as f:
                if not is_first:
                    f.write(",")
                else: 
                    is_first = False
                f.write(follower.json())
                i += 1
    with open(output_filepath, "a+") as f:
        f.write("]")
    print(f"Verified Followers Count: {i}")



# Function to Download Verified Followers Data
async def famous_followers(user_id, output_filepath, limit=-1):
    with open(output_filepath, "w+") as f:
        f.write("[")
    is_first = True
    i = 0
    async for follower in scraper_api.followers(user_id, limit=limit):
        if follower.followersCount >= 5000:
            with open(output_filepath, "a+") as f:
                if not is_first:
                    f.write(",")
                else: 
                    is_first = False
                f.write(follower.json())
                i += 1
    with open(output_filepath, "a+") as f:
        f.write("]")
    print(f"Famous Followers Count: {i}")



async def hashtags_handles_data(user_id, output_filepath):
    with open(output_filepath, "w+") as f:
        f.write("[")
    is_first = True
    i = 0
    async for search in scraper_api.search(user_id, limit=200):
        with open(output_filepath, "a+") as f:
                if not is_first:
                    f.write(",")
                else: 
                    is_first = False
                f.write(search.json())
                i += 1
    with open(output_filepath, "a+") as f:
        f.write("]")
    print(f"Total Results Found: {i}")



# Functions to Download Followers Tweets Data

# Function to Download Tweets
async def downloading_follower_tweets(user_id, output_filepath, limit=5):
    with open(output_filepath, "w+") as f:
        f.write("[")
    is_first = True
    i = 0
    async for tweet in scraper_api.user_tweets(user_id, limit=5):
        with open(output_filepath, "a+") as f:
            if not is_first:
                f.write(",")
            else:
                is_first = False
            f.write(tweet.json())
            i += 1
    with open(output_filepath, "a+") as f:
        f.write("]\n\n\n\n\n\n\n\n\n\n")
    print(f"Followers Tweets Count: {i}")

# Called Function
async def download_follower_tweets(user_id, output_filepath, limit=5):
    async for follower in scraper_api.followers(user_id, limit=5):
        follower_username = await scraper_api.user_by_login(follower.username)
        await downloading_follower_tweets(follower_username.id, output_filepath)



# Functions to Download Followings Tweets Data

# Function to Download Tweets
async def downloading_following_tweets(user_id, output_filepath, limit=5):
    with open(output_filepath, "w+") as f:
        f.write("[")
    is_first = True
    i = 0
    async for tweet in scraper_api.user_tweets(user_id, limit=5):
        with open(output_filepath, "a+") as f:
            if not is_first:
                f.write(",")
            else:
                is_first = False
            f.write(tweet.json())
            i += 1
    with open(output_filepath, "a+") as f:
        f.write("]\n\n\n\n\n\n\n\n\n\n")
    print(f"Following Tweets Count: {i}")

# Called Function
async def download_following_tweets(user_id, output_filepath, limit=5):
    async for following in scraper_api.following(user_id, limit=5):
        following_username = await scraper_api.user_by_login(following.username)
        await downloading_following_tweets(following_username.id, output_filepath)



# main function
async def main():
    subject_username = 'ctravisjohnson'
    export_directory_dict = get_data_export_directory_dict(
        temp_data_path, platform, subject_username, date_string,
        ['info', 'all_tweets', 'following', 'followers','latest_tweets','verified_followers','famous_followers','hashtags_handles','tweets_of_followers']                                                       
    )

    user_object = await download_user_info(subject_username, export_directory_dict['info'])
    await download_tweets(user_object.id, export_directory_dict['all_tweets'])
    await download_follower_profiles(user_object.id, export_directory_dict['followers'])
    await download_latest_tweets(user_object.id, export_directory_dict['latest_tweets'])
    await verified_followers(user_object.id, export_directory_dict['verified_followers'])
    await famous_followers(user_object.id, export_directory_dict['famous_followers'])
    await hashtags_handles_data(subject_username, export_directory_dict['hashtags_handles'])
    # await download_follower_tweets(user_object.id, export_directory_dict['tweets_of_followers'])
    # await download_following_tweets(user_object.id, export_directory_dict['tweets_of_followings'])


if __name__ == "__main__":
    asyncio.run(login())
    # asyncio.run(main())