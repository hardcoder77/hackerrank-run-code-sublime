import json
import os
import sys
import itertools

sys.path.append(os.path.join(os.path.dirname(__file__), "lxml-3.4.4"))
sys.path.append(os.path.join(os.path.dirname(__file__), "requests-2.7.0"))
import requests


class HackerRankClient():
    def __init__(self):
        self.host = "https://www.hackerrank.com"
        self.run_code_path = "/rest/contests/master/challenges/%s/compile_tests"
        self.cookie_header = None
        self.language_map = self.get_language_map()
        self.compile_url = self.host + self.run_code_path
        self.login_url = self.host + "/login"
        self.csrf_token = None
        self.csrf_token_header = None
        self.login()


    def get_compile_id(self, content, language, problem_name):
        self.compile_url = self.host + self.run_code_path % problem_name
        payload = self.build_run_code_payload(content, language)
        compile_headers = {'Content-Type': "application/json"}
        compile_headers.update(self.cookie_header)
        compile_headers.update(self.csrf_token_header)
        response = requests.post(self.compile_url, headers=compile_headers, data=json.dumps(payload))
        response_text = json.loads(response.text)
        id = str(response_text["model"]["id"])
        return id

    def get_run_status(self, id):
        headers = {}
        headers.update(self.cookie_header)
        headers.update(self.csrf_token_header)
        status_url = self.compile_url + "/" + id + "?_=1"
        status_response = requests.get(status_url, headers=headers)
        status_response_text = status_response.text
        status_response_text = json.loads(status_response_text)
        while status_response_text["model"]["status"] == 0:
            print(status_response_text["model"]["status_string"])
            status_response = requests.get(status_url, headers=headers)
            status_response_text = status_response.text
            status_response_text = json.loads(status_response_text)
        return status_response_text

    def print_results(self, status_response_text):
        print("Input(stdin)")
        print(status_response_text["model"]["stdin"][0])
        print("Your Output(stdout)")
        print(status_response_text["model"]["stdout"][0])
        print("Expected Output")
        print(status_response_text["model"]["expected_output"][0])
        expected_list = status_response_text["model"]["expected_output"][0].split("\n")
        actual_list = status_response_text["model"]["stdout"][0].split("\n")
        passed = []
        failed = []
        for expected, actual in zip(expected_list, actual_list):
            if expected == actual:
                passed.append(expected)
            else:
                failed.append(expected)
        print("Number of test cases passed: ", len(passed))

    def run_code(self, problem_name, language, content):
        id = self.get_compile_id(content, language, problem_name)
        status_response_text = self.get_run_status(id)
        self.print_results(status_response_text)



    def set_cookie_header(self, value):
        self.cookie_header = {"Cookie": value}

    def get_language_map(self):
        return {
            "python2": "python"
        }

    def build_run_code_payload(self, content, language):
        return {"code": content,
                "customtestcase": False,
                "language": self.language_map[language]}

    def get_csrf_token_set_cookie(self):
        login_page_get_response = requests.get(self.login_url)
        login_page_get_response_text = str(login_page_get_response.text)
        csrf_token_index = login_page_get_response_text.find("csrf-token")
        csrf_content_end_token = login_page_get_response_text[:csrf_token_index - 2].rfind('"')
        csrf_content_start_token = login_page_get_response_text[:csrf_content_end_token].rfind('"')
        self.csrf_token = login_page_get_response_text[csrf_content_start_token + 1:csrf_content_end_token]
        self.set_csrf_token_header()
        login_page_get_response_headers = login_page_get_response.headers
        self.set_cookie_header(login_page_get_response_headers['set-cookie'])

    def get_auth_dict(self):
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(__location__, "auth.json")) as f:
            content = f.read()
        content = json.loads(content)
        return content

    def post_auth_data(self, auth_dict):
        post_auth_headers = {}
        post_auth_headers.update(self.cookie_header)
        post_auth_headers.update(self.csrf_token_header)
        post_auth_response = requests.post(self.login_url, headers=post_auth_headers, data=auth_dict)
        return post_auth_response

    def login(self):
        self.get_csrf_token_set_cookie()
        auth_dict = self.get_auth_dict()
        post_auth_response = self.post_auth_data(auth_dict)
        post_auth_response_headers = post_auth_response.headers
        self.set_cookie_header(post_auth_response_headers['set-cookie'])
        print("Logged in successfully")


    def set_csrf_token_header(self):
        self.csrf_token_header = {"X-CSRF-Token": self.csrf_token}

