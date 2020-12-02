from bs4 import BeautifulSoup
import json
import os
import re
import requests
import random
import string
import time
import logging
from logging.config import fileConfig
from distutils.util import strtobool
import datetime
from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from django.http import HttpResponseRedirect
from instagram.models import InstagramList, InstagramProfile, InstagramPosts, InstagramComments

fileConfig('config.ini')
logger = logging.getLogger('InstagramScraper_Log:')

banner = '''

██╗███╗   ██╗███████╗████████╗ █████╗  ██████╗ ██████╗  █████╗ ███╗   ███╗
██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
██║██╔██╗ ██║███████╗   ██║   ███████║██║  ███╗██████╔╝███████║██╔████╔██║
██║██║╚██╗██║╚════██║   ██║   ██╔══██║██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║
██║██║ ╚████║███████║   ██║   ██║  ██║╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝

'''


class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class InstagramScraper:

    def __init__(self, username):
        self.username = username
        self.home_url = 'https://instagram.com/'
        self.base_url = 'https://www.instagram.com/graphql/query/?query_hash=7c8a1055f69ff97dc201e752cf6f0093&variables='
        self.useragents = [
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0']
        self.cookies = {'sessionid': f'{InstagramList.objects.get(user_name=username).admin.session_id}'}
        self.driver_cookie = InstagramList.objects.get(user_name=username).admin.cookie
        self.profile_data, self.profile_meta = self.scrape_profile()
        self.driver = self.get_driver()

    def __getitem__(self, i):
        return self.profile_data[i]

    def scrape_profile(self):
        """
        This is the main scrape which takes the profile data retrieved and saves it into profile_data
        :return: profile data
        :param: none
        """
        logger.info(f'{colors.OKGREEN}Starting scan on "{self.username}" profile{colors.ENDC}')
        response = self.get_response(f'{self.home_url}{self.username}')
        soup = BeautifulSoup(response.text, 'lxml')
        # Find the tags that hold the data we want to parse
        general_data = soup.find_all('meta', attrs={'property': 'og:description'})
        more_data = soup.find_all('script', attrs={'type': 'text/javascript'})
        # Try to parse the content -- if it fails then the program exits
        try:
            text = general_data[0].get('content').split()
            profile_meta = json.loads(re.search(r'{(...)+', str(more_data[3])).group().strip(';</script>'))
        except:
            logger.warning(f'{colors.FAIL}Username "{self.username}" not found{colors.ENDC}')
            return 1
        profile_data = {
            "Username": profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['username'],
            "User_id": profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['id'],
            "Profile name": profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['full_name'],
            "URL": f'{self.home_url}{self.username}',
            "Followers": profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count'],
            "Following": profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count'],
            "Posts": text[4],
            "Bio": str(profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['biography']),
            "profile_pic_url": str(
                profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['profile_pic_url_hd']),
            "is_business_account": str(
                profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['is_business_account']),
            "connected_to_fb": str(
                profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['connected_fb_page']),
            "external_url": str(profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['external_url']),
            "joined_recently": str(
                profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['is_joined_recently']),
            "business_category_name": str(
                profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['business_category_name']),
            "is_private": str(profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['is_private']),
            "is_verified": str(profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['is_verified']),
            "Page_Cursor":
                profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media'][
                    'page_info'][
                    'end_cursor'],
        }
        # save to db
        ip = InstagramProfile(
            user_name=profile_data["Username"],
            profile_name=profile_data["Profile name"],
            profile_url=profile_data["URL"],
            followers=profile_data["Followers"],
            following=profile_data["Following"],
            posts=profile_data["Posts"],
            bio=profile_data["Bio"],
            profile_pic_url=profile_data["profile_pic_url"],
            is_business_account=profile_data["is_business_account"],
            connected_to_fb=profile_data["connected_to_fb"],
            is_private=profile_data["is_private"],
            is_verified=profile_data["is_verified"],
        )
        ip.save()
        logger.info(f'{colors.OKBLUE}Finished scan on "{self.username}" profile{colors.ENDC}')

        return profile_data, profile_meta

    def scrape_posts(self):
        """
        Scrapes all posts and downloads them
        :return: none
        :param: none
        """
        if strtobool(self.profile_data["is_private"]):
            logger.info(f'{colors.FAIL} This account "{self.username}" is private')
            return 1
        logger.info(f'{colors.OKGREEN}Starting scan on {self.username} posts')
        if strtobool(self.profile_data['is_private']):
            logger.warning(f"{self.username} is private profile, cannot scrape photos!")
            # save profile is private
            return 1
        else:
            posts = {}
            index = 0
            next_page_cursor = self.profile_data["Page_Cursor"]
            post_data = \
                self.profile_meta['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media'][
                    'edges']
            while post_data:
                for post in post_data:
                    posts[index] = {"Post URL": f'{self.home_url}p/{post["node"]["shortcode"]}',
                                    "Post Type": post['node']['__typename'],
                                    "Comments": post['node']['edge_media_to_comment']['count'],
                                    "Comments Disabled": str(post['node']['comments_disabled']),
                                    "DateTime": datetime.datetime.fromtimestamp(post['node']['taken_at_timestamp']),
                                    # "Likes": post['node']['edge_liked_by']['count'],
                                    }
                    # get post message but maybe dont have message in post
                    try:
                        posts[index].update({"Message": str(
                            post['node']['edge_media_to_caption']['edges'][0]['node']['text']).replace('\n', '')})
                    except:
                        posts[index].update({"Message": ''})
                    post_profile_meta, interaction_count = self.get_profile_in_post(posts[index]['Post URL'])
                    posts[index].update({"Interaction Count": interaction_count})
                    # save pic(s) url or video url
                    pic_or_video_url = []
                    if posts[index]["Post Type"] == 'GraphImage':  # only one pic
                        pic_or_video_url = post['node']['display_url']
                        # self.download_post_picture_or_video(index, posts[index][f"The Photo 1 URL"], '.jpg')
                    elif posts[index]["Post Type"] == 'GraphSidecar':  # more than 2 pics
                        for photo_index, edge in enumerate(post['node']['edge_sidecar_to_children']['edges'], start=1):
                            pic_or_video_url.append(edge['node']['display_url'])
                            # self.download_post_picture_or_video(index, posts[index][f"The Photo/Video {photo_index} URL"], '.jpg')
                    elif posts[index]["Post Type"] == 'GraphVideo':
                        pic_or_video_url = post_profile_meta['entry_data']['PostPage'][0]['graphql'][
                            'shortcode_media']['video_url']
                        # self.download_post_picture_or_video(index, posts[index]["The Video URL"], '.mp4')
                    """judge post is it exist in db"""
                    if InstagramPosts.objects.filter(post_url=posts[index]["Post URL"]):
                        continue
                    # save to db
                    igp = InstagramPosts(
                        user_name=self.profile_data["Username"],
                        post_url=posts[index]["Post URL"],
                        post_type=posts[index]["Post Type"],
                        post_message=posts[index]["Message"],
                        comments_disable=posts[index]["Comments Disabled"],
                        comments=posts[index]["Comments"],
                        interactions=posts[index]["Interaction Count"],
                        created_time=posts[index]["DateTime"],
                        pic_or_video_url=pic_or_video_url,
                    )
                    igp.save()
                    # get comment in post
                    if InstagramList.objects.get(user_name=self.profile_data["Username"]).get_comments_uid:
                        if not strtobool(posts[index]['Comments Disabled']):
                            self.get_comment_from_post(posts[index]["Post URL"])
                    index += 1

                # The Next Page For 12 Posts
                if next_page_cursor is not None:
                    var_num = {"id": self.profile_data.get('User_id'),
                               "first": '12', "after": next_page_cursor}
                    var_num_code = parse.quote(json.dumps(var_num))
                    next_response = self.get_response(f'{self.base_url}{var_num_code}')
                    post_data = json.loads(next_response.text)['data']['user']['edge_owner_to_timeline_media']['edges']
                    next_page_cursor = \
                        json.loads(next_response.text)['data']['user']['edge_owner_to_timeline_media']['page_info'][
                            'end_cursor']
                else:
                    break
        self.driver.quit()
        logger.info(f'{colors.OKGREEN}Finished scan on {self.username} posts')

    def get_comment_from_post(self, post_url):
        """
        Get all comment in each post with selenium
        :param post_url:
        :return:
        """
        logger.info(f'{colors.OKGREEN}Starting scan on {self.username}:{post_url}{colors.ENDC}')
        driver = self.driver
        driver.get(post_url)
        comments_count = 0
        # expand comment list
        while True:
            try:
                WebDriverWait(driver, 4, 0.5).until(
                    ec.visibility_of_element_located((By.CSS_SELECTOR, ('.dCJp8')))).click()
                soup = BeautifulSoup(driver.page_source, 'lxml')
                comments_len = len(soup.find_all('ul', class_='Mr508'))
                if comments_len == comments_count:
                    break
            except:
                logger.warning(f'{colors.FAIL}STH error in expand comments{colors.ENDC}')
                break
        soup = BeautifulSoup(driver.page_source, 'lxml')
        # get comment info
        try:
            all_comments = soup.find_all('ul', class_='Mr508')
            for comment in all_comments:
                comment_row = comment.find('div', class_='C4VMK', recursive=True)
                try:
                    user_name = comment_row.find('a', href=True).text
                except:
                    logger.exception(f'{colors.FAIL}error in commment username{colors.ENDC}')
                try:
                    created_time = \
                        re.search(r'datetime="(...)+"', str(comment_row.find('time', datetime=True))).group().split(
                            '"')[1]
                    created_time = datetime.datetime.strptime(created_time[:-5], '%Y-%m-%dT%H:%M:%S')
                except:
                    created_time = None
                    logger.exception(f'{colors.FAIL}error in commment created time{colors.ENDC}')
                try:
                    comment_message = comment_row.find('span', class_="").text
                except:
                    comment_message = ''
                    logger.exception(f'{colors.FAIL}error in commment message{colors.ENDC}')
                logger.info(f'Comment Post: {post_url}-{user_name}-{comment_message}-{created_time} get success')
                # save to db
                ic = InstagramComments(
                    user_name=user_name,
                    post_url=post_url,
                    comment_message=comment_message,
                    created_time=created_time,
                )
                ic.save()
        except:
            logger.exception(f'{colors.FAIL}STH error in comments scrap{colors.ENDC}')
        logger.info(f'{colors.OKGREEN}Finished scan on {self.username}:{post_url}{colors.ENDC}')

    def get_driver(self):
        """
        get driver and login with cookie
        :return: driver
        """
        options = Options()
        options.add_argument('--headless')
        options.add_argument('blink-settings=imagesEnabled=false')
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(self.home_url)
        cookie = self.driver_cookie
        cookie_data = cookie.split('; ')
        for item in cookie_data:
            item = item.split('=')
            driver.add_cookie({
                'domain': '.instagram.com',
                'name': item[0],
                'value': item[1],
                'path': '/',
                'expires': None
            })
        driver.refresh()
        return driver

    def get_response(self, url):
        """
        get response from requests
        :param url:
        :return: True
        """
        while 3:
            try:
                response = requests.get(url=url, headers={'User-Agent': random.choice(self.useragents)},
                                        cookies=self.cookies)
                return response
            except:
                pass
        logger.warning(f'{colors.FAIL} Get {url} response fail{colors.ENDC}')
        return 1

    def download_profile_picture(self):
        """
        Downloads the profile pic and saves it to the directory
        :return: none
        """
        with open("profile_pic.jpg", "wb") as f:
            time.sleep(1)
            profile_picture_url = self.get_response(self.profile_data['profile_pic_url'])
            f.write(profile_picture_url.content)

    def download_post_picture_or_video(self, index, url, download_type):
        """
        Downloads the post pic(s) and saves it to directory
        :param index: which pic in post
        :param url: each pic url
        :param download_type: if is pic = .jpg elif video = .mp4
        :return: none
        """
        with open(f'{os.getcwd()}/{index}/' + ''.join(
            [random.choice(string.ascii_uppercase) for x in range(random.randint(1, 9))]) + f'{download_type}',
              'wb') as f:
            time.sleep(random.randint(5, 10))
            pic_or_video_response = self.get_response(url)

            f.write(pic_or_video_response.content)

    def get_profile_in_post(self, url):
        """
        Get profile from each post
        :param url: post url
        :return: True
        """
        logger.info(f'{colors.OKGREEN}{url} starting to get post profile')
        post_response = self.get_response(url)
        soup = BeautifulSoup(post_response.text, 'lxml')
        profile = soup.find_all('script', attrs={'type': 'text/javascript'})
        post_profile_meta = json.loads(re.search(r'{(...)+', str(profile[3])).group().strip(';</script>'))
        description = soup.find('script', attrs={'type': 'application/ld+json'})
        try:
            description = json.loads(re.search(r'{(...)+"*}*', str(description)).group())
            interaction_count = description['interactionStatistic']['userInteractionCount']
        except AttributeError:
            interaction_count = \
                post_profile_meta['entry_data']['PostPage'][0]['graphql']['shortcode_media']['edge_media_preview_like'][
                    'count']
        except:
            interaction_count = 0
            logger.exception(f'{colors.FAIL}{url} get interaction count fail{colors.ENDC}')
        logger.info(f'{colors.OKBLUE}{url} finished get post profile')
        return post_profile_meta, interaction_count


def main(request):
    username = request.GET['user_name']
    print(f'{colors.HEADER}{banner}{colors.ENDC}')
    profile = InstagramScraper(username=username)
    profile.scrape_posts()
    return HttpResponseRedirect('/')
