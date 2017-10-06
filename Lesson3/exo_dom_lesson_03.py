#!/usr/bin/python3.5

import json
import functools
import requests
from bs4 import BeautifulSoup
from multiprocessing import Process, Queue

most_active_users_url = "https://gist.github.com/paulmillr/2657075"


class GitUser:
    def __init__(self, login, repositories):
        self.login = login
        self.repositories = repositories
        self.repository_numbers = len(repositories)
        if self.repository_numbers > 0:
            stars_by_repo = map(lambda repo: repo['stargazers_count'], repositories)
            self.average_stars_by_project = functools.reduce(self.add, stars_by_repo) / self.repository_numbers
        else:
            self.average_stars_by_project = 0

    def add(self, c1, c2):
        return c1 + c2

    def print(self):
        print("User " + self.login + ":")
        print("Number of projects: " + str(self.repository_numbers))
        print("Average number of stars: " + str(self.average_stars_by_project))


class GitCrawler:
    def __init__(self):
        self.token = "e4304c97c0c7efb5fd307c72d71c5023cf6b9e94"

    def crawl_most_active_users(self, url):
        request_result = requests.get(url)
        soup = BeautifulSoup(request_result.text, 'html.parser')
        article = soup.find("article", attrs={'class': 'markdown-body'})
        user_rows = article.find_all("tr")[1:]
        return [row.select('td > a')[0].text for row in user_rows]

    def get_git_user(self, user_login):
        headers = {'Authorization': 'token ' + self.token}
        repositories_result = requests.get("https://api.github.com/users/" + user_login + "/repos", headers=headers)
        return GitUser(user_login, json.loads(repositories_result.text))


def get_git_user(users, crawler, user_login):
    users.put(crawler.get_git_user(user_login))


if __name__ == '__main__':
    crawler = GitCrawler()
    print("Crawling most active users on github")
    users_logins = crawler.crawl_most_active_users(most_active_users_url)
    users_queue = Queue()
    processes = []

    # start one process for each user to crawl
    print("Preparing API requests")
    for user_login in users_logins:
        p = Process(target=get_git_user, args=(users_queue, crawler, user_login))
        p.start()
        processes.append(p)

    # get results from queue
    users = []
    print("Requesting API for users")
    for user_login in users_logins:
        users.append(users_queue.get())
        print('.', end='', flush=True)

    # terminate processes
    for p in processes:
        p.join()

    # Sort & display users
    users.sort(key=lambda user: user.average_stars_by_project, reverse=True)
    print("")
    print("")
    print("Average number of stars for github 250 most active users\n")
    for user in users:
        print(user.login + ": " + str(user.average_stars_by_project))
