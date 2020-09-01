import scrapy
import json
import time
import re
import pandas as pd
import numpy as np


class ProfileSpider(scrapy.Spider):
    name = 'profile'

    def __init__(self):
        try:
            post_file = input('id 파일명(경로 포함)을 입력해 주세요(ex. D:\Scrapy\insta_crawling\insta_crawling\jl_1.csv)\n')
            df = pd.read_csv(r'{}'.format(post_file))
            self.user_name_lst = list(map(str, list(np.unique(df['insta_id']))))
            self.user_id_lst = list(map(str, list(np.unique(df['inner_id']))))
        except:
            print('file_error!')

        self.starttime = time.time()
        self.request_count = 0
        self.business_number = 0
    
    # profile 페이지 request
    def start_requests(self):
        for user_id, user_name in zip(self.user_id_lst, self.user_name_lst):

            # 진행상황 출력
            timer = round((self.starttime-time.time())/60)
            percentage = round(self.request_count/len(self.user_id_lst), 2)
            print('{}분 경과, {}개 중 {}개 request 완료({}%)'.format(timer, len(self.user_id_lst), self.request_count, percentage))
            profile_url = 'https://www.instagram.com/{}/?__a=1'.format(user_name)
            yield scrapy.Request(profile_url, callback=self.profile_parse, meta={'user_id': user_id, 'user_name':user_name})        
    
    # 프로필 정보 크롤링해서 저장
    def profile_parse(self, response):
        res = response.json()
        business = res['graphql']['user']['is_business_account']
        # business 계정이면 저장하지 않음
        if not business:
            user_id = response.meta['user_id']
            user_name = response.meta['user_name']
            profile_text = res['graphql']['user']['biography']
            profile_text_2 = re.sub('\n', ', ', profile_text)
            post_num = res['graphql']['user']['edge_owner_to_timeline_media']['count']        
            yield {
                'inner_id' : user_id,
                'insta_id' : user_name,
                'profile' : profile_text_2,
                'gender' : None,
                'region' : None,
                'age' : None,
                'job' : None,
                'interest' : None,
                'post_num' : post_num
                }
        else:
            self.business_number += 1
            print('business account! (total: {})'.format(self.business_number))
            
