import scrapy
import re
import time
from bs4 import BeautifulSoup
import json
import requests

# Setting에서 건드릴 것
# USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36"
# ROBOTSTXT_OBEY = False
# COOKIES_ENABLED = True
######

class RelationSpider(scrapy.Spider):
    name = 'relation'

    # 팔로워와 팔로우 목록을 추출할 user 정보(username, id)
    # user_name = 'park_chan_0_0'
    user_id_lst = ['2056152256']
    epoch = 1
    start_end_lst = []
    header = {}
    login_url = 'https://instagram.com/accounts/login/ajax'
    login_data = {}
    over1000_lst = []

    
    def start_requests(self):
        base_url = 'https://instagram.com/accounts/login'

        # 로그인 위해서 필요한 header 1
        RelationSpider.header['referer'] = base_url

        # 로그인 위해서 필요한 키값(csrf) 추출 위해서 requests 활용(Scrapy로 수정해봤으나 계속 오류 발생해서 유지)
        session = requests.Session()
        session.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'}
        session.headers.update({'Referer': base_url})
        req = session.get(base_url)
        soup = BeautifulSoup(req.content, 'html.parser')
        body = soup.find('body')
        pattern = re.compile('window._sharedData')
        script = body.find("script", text=pattern)
        script = script.get_text().replace('window._sharedData = ', '')[:-1]
        data = json.loads(script)
        csrf = data['config'].get('csrf_token')

        # 로그인 위해서 필요한 header 2, 3
        RelationSpider.header['X-CSRFToken'] = csrf
        RelationSpider.header['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'

        # 로그인 위해서 필요한 username과 password(인코딩 된 패스워드)
        str_time = str(int(time.time()))
        PASSWORD = '#PWD_INSTAGRAM_BROWSER:0:' + str_time + ':' + 'ska22055233'
        RelationSpider.login_data = {'username': 'hnamgoisunn', 'enc_password': PASSWORD}

        # 로그인 request
        yield scrapy.FormRequest(RelationSpider.login_url, method='POST', formdata = RelationSpider.login_data, headers=RelationSpider.header, callback=self.start_epoch)



    # epoch마다 다시 로그인 작업 수행
    def start_epoch(self, response):
        # start_end_lst 초기화
        RelationSpider.start_end_lst = []
        # 이번 epoch의 user_id 리스트
        user_id_lst = RelationSpider.user_id_lst
        for idx in range(len(user_id_lst)):
            user_id = user_id_lst[idx]
            follower_url = 'https://www.instagram.com/graphql/query/?query_hash=c76146de99bb02f6415203be841dd25a&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A24%7D'.format(user_id)
            # follower_url 활용해서 follower 목록 페이지 request
            meta = {'user_id' : user_id, 'finished': False}
            if idx == len(user_id_lst)-1:
                meta = {'user_id' : user_id, 'finished' : True}
            yield scrapy.Request(follower_url, callback=self.parse_follower, meta = meta)


    # 팔로워 목록 추출
    def parse_follower(self, response):
        user_id, finished = response.meta['user_id'], response.meta['finished']
        # 팔로워 페이지를 json 형식으로 받아옴
        follower_json = response.json()
        follower_num = follower_json['data']['user']['edge_followed_by']['count']
        # follower 1000명 이상은 따로 리스트에 저장하고 넘어감.
        if follower_num > 1000:
            RelationSpider.over1000_lst.append(user_id)
            if finished:
                print('epoch {} finihsed'.format(RelationSpider.epoch))
                if RelationSpider.epoch >= 2:
                    yield {
                        'over1000': RelationSpider.over1000_lst
                    }
                    return                
                RelationSpider.epoch += 1
                next_user_id_lst = []
                for x, y in RelationSpider.start_end_lst:
                    next_user_id_lst.append(x)
                    next_user_id_lst.append(y)
                RelationSpider.user_id_lst = list(set(next_user_id_lst))
                yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A24%7D'.format(user_id), callback=self.start_epoch)
            else:
                return
        # follower_lst 추출
        follower_lst = follower_json['data']['user']['edge_followed_by']['edges']
        # 개별 팔로워 추출해서 start에 팔로워, end에 대상 user_id 저장
        for follower in follower_lst:
            if not follower['node']['is_private']:
                RelationSpider.start_end_lst.append([follower['node']['id'], user_id])
            # 비공개 아이디는 어차피 필요없는 정보이기 때문에 제외하고 크롤링
            else:
                print('private_id!')

        # end_cursor 정보가 있어야 커서 내리면 나오는 다음 팔로워 목록으로 이동할 수 있음 
        try:
            end_cursor = follower_json['data']['user']['edge_followed_by']['page_info']['end_cursor']
        except:
            end_cursor = False

        # 다음 팔로워 목록 있으면 다음 팔로워 목록 url로 request하고 다시 팔로워 목록 추출
        if end_cursor:
            time.sleep(1)
            follower_url = 'https://www.instagram.com/graphql/query/?query_hash=c76146de99bb02f6415203be841dd25a&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A13%2C%22after%22%3A%22{}%3D%3D%22%7D'.format(user_id, end_cursor[:-2])
            yield scrapy.Request(follower_url, callback=self.parse_follower, meta = {'user_id' : user_id, 'finished': finished})
        # 다음 팔로워 목록 없으면 팔로우 목록 추출 함수로 이동
        else:
            time.sleep(1)
            follow_url = 'https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A24%7D'.format(user_id)
            yield scrapy.Request(follow_url, callback=self.parse_follow, meta = {'user_id' : user_id, 'finished': finished})

    # 팔로우 목록 추출
    def parse_follow(self, response):
        user_id, finished = response.meta['user_id'], response.meta['finished']
        # 팔로우 페이지를 json 형식으로 받아옴
        follow_json = response.json()
        # follow_lst 추출
        follow_lst = follow_json['data']['user']['edge_follow']['edges']

        # 개별 팔로우 추출해서 start에 대상 user_id, end에 팔로우하는 상대 id 저장
        for follow in follow_lst:
            if not follow['node']['is_private']:
                RelationSpider.start_end_lst.append([user_id, follow['node']['id']])
            # 비공개 아이디는 어차피 필요없는 정보이기 때문에 제외하고 크롤링
            else:
                print('private_id!')
        
        # end_cursor 정보가 있어야 커서 내리면 나오는 다음 팔로우 목록으로 이동할 수 있음 
        try:
            end_cursor = follow_json['data']['user']['edge_follow']['page_info']['end_cursor']
        except:
            end_cursor = False

        # 다음 팔로우 목록 있으면 다음 팔로우 목록 url로 request하고 다시 팔로우 목록 추출
        if end_cursor:
            time.sleep(1)
            follow_url = 'https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A13%2C%22after%22%3A%22{}%3D%3D%22%7D'.format(user_id, end_cursor[:-2])
            yield scrapy.Request(follow_url, callback=self.parse_follow, meta = {'user_id' : user_id, 'finished': finished})
        else:
            for start, end in RelationSpider.start_end_lst:
                yield {
                    'start': start,
                    'end' : end
                    }
            # 마지막 팔로우 목록이고, finished = True(마지막 user_id)인 경우
            if finished: 
                print('epoch {} finihsed'.format(RelationSpider.epoch))
                if RelationSpider.epoch >= 2:
                    yield {
                        'over1000': RelationSpider.over1000_lst
                    }
                    return                
                RelationSpider.epoch += 1
                next_user_id_lst = []
                for x, y in RelationSpider.start_end_lst:
                    next_user_id_lst.append(x)
                    next_user_id_lst.append(y)
                RelationSpider.user_id_lst = list(set(next_user_id_lst))
                yield scrapy.Request('https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables=%7B%22id%22%3A%22{}%22%2C%22first%22%3A24%7D'.format(user_id), callback=self.start_epoch)


                
                # # 로그인 위해서 필요한 username과 password(인코딩 된 패스워드)
                # str_time = str(int(time.time()))
                # PASSWORD = '#PWD_INSTAGRAM_BROWSER:0:' + str_time + ':' + 'ska22055233'
                # RelationSpider.login_data = {'username': 'hnamgoisunn', 'enc_password': PASSWORD}
                # yield scrapy.FormRequest(RelationSpider.login_url, method='POST', formdata = RelationSpider.login_data, headers=RelationSpider.header, callback=self.check_login)


        


