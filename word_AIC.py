import math
from nltk.tokenize import RegexpTokenizer
from chatspace import ChatSpace
from konlpy.tag import Mecab


class feature_vector():

    def __init__(self):
        self.spacer = ChatSpace()
        self.retokenize = RegexpTokenizer("[가-힣ㄱ-ㅎㅏ-ㅣ]+")
        self.retokenize_hash = RegexpTokenizer("#[가-힣ㄱ-ㅎㅏ-ㅣ]+")
        self.mecab = Mecab()


    def _AIC(self, max_like, free_param_num):
        return -2 * max_like + 2 * free_param_num
        # log가 들어가야 하는건지 안 들어가야 하는 건지 잘 모르겠음
        # 논문 (1) 공식에는 log가 들어가지만,
        # 논문 (3) 공식에는 log가 안 들어감.
        # -> max_likelihood가 음수가 나오면 log 오류남. 그래서 log 일단 빼는 거로 결정.


    # t = term, D_p = Document postivie list, D_n = Document negative list
    def _calculation(self, t, D_p, D_n):
        # Documents count for calculation of AIC
        N11_t, N12_t, N21_t, N22_t = 0.000001, 0.000001, 0.000001, 0.000001   # t appears in D_p, t does not appear in D_p, t appears in D_n, t does not appear in D_n
        for d in D_p:
            if t in d:
                N11_t += 1
            else:
                N12_t += 1
        for d in D_n:
            if t in d:
                N21_t += 1
            else:
                N22_t += 1

        N_p, N_n = len(D_p), len(D_n)   # postive 문서 수, negative 문서 수
        N = N_p + N_n   # 전체 문서 수
        N_t = N11_t + N21_t     # 전체 문서에서 t가 들어가는 문서 수
        N_not_t = N12_t + N22_t     # 전체 문서에서 t가 안 들어가는 문서 수
        N_all = [N, N_p, N_n, N_t, N_not_t, N11_t, N12_t, N21_t, N22_t]


        # maximum likelihood 계산
        # 오류 발생: math.log(0)일 경우 계산이 되지 않음. count가 0일 때는 어떻게 처리할지 확인해야 함.
        # 일단은 모두 초기값을 매우 작은 수로 수정해줘서 오류나지 않게 넘어감. -> 이렇게 하는게 일반적이라고 함.
        mll_dm_t = N11_t * math.log(N11_t) + N12_t*math.log(N12_t) + N21_t*math.log(N21_t) + N22_t*math.log(N22_t) - N*math.log(N)
        mll_im_t = N_p*math.log(N_p) + N_t*math.log(N_t) +  N_n*math.log(N_n) + N_not_t*math.log(N_not_t) + (-2)*N*math.log(N)
        
        return mll_dm_t, mll_im_t, N_all
    

    def evaluation(self, term, D_p, D_n):
        mll_dm_t, mll_im_t, N_all = self._calculation(term, D_p, D_n)
        AIC_dm = self._AIC(mll_dm_t, 3)
        AIC_im = self._AIC(mll_im_t, 2)
        if N_all[5]/N_all[3] > N_all[6]/N_all[4]:
            E_t = AIC_im - AIC_dm + 2
        else:
            E_t = AIC_dm - AIC_im - 2
        return E_t
    

    # 한글만 남겨둔 뒤에, 띄어쓰기 교정 후에, mecab 통해서 tokenize
    def _tokenizer(self, doc):
        text = ' '.join(self.retokenize.tokenize(doc))
        text = self.spacer.space(text)
        token_lst = self.mecab.morphs(text)
        return token_lst

    # 해쉬태그용 tokenize 함수
    def _hashtag_tokenizer(self, doc):
        text = ' '.join([h[1:] for h in self.retokenize_hash.tokenize(doc)])
        text = self.spacer.space(text)
        token_lst = self.mecab.morphs(text)
        return token_lst

    def _term_lst(self, D):
        term_lst = []
        for doc in D:
            if '#' in doc:
                term_lst += self._hashtag_tokenizer(doc)
            else:
                term_lst += self._tokenizer(doc)
        term_lst = list(set(term_lst))
        print(term_lst)
        return term_lst

    def key_terms(self, D_p, D_n, evaluation_threshold = 2000):
        D = D_p + D_n
        term_lst = self._term_lst(D)
        eval_dic = {t:round(self.evaluation(t, D_p, D_n), 5) for t in term_lst}
        eval_sort = sorted(eval_dic.items(), key=lambda x:x[1], reverse=True)
        key_terms = dict(eval_sort[:evaluation_threshold])
        return key_terms
        

    def get_feature_vec(self, key_terms, D_p, D_n):
        feature_vec = []
        feature_vec_label = []

        for p in D_p:
            tmp = []
            for t in key_terms:
                if t in p:
                    tmp.append(1)
                else:
                    tmp.append(0)
            feature_vec.append(tmp)
            feature_vec_label.append(1)

        for n in D_n:
            tmp = []
            for t in key_terms:
                if t in n:
                    tmp.append(1)
                else:
                    tmp.append(0)
            feature_vec.append(tmp)
            feature_vec_label.append(0)

        return feature_vec, feature_vec_label


if __name__ == "__main__":
    D_p = ['서울 너무 좋아 짱짱', '서울 광진구 너무 좋아 짱짱', '#경기도 #너무 #좋아 #짱짱', '경기도가 최고']
    D_n = ['부산 너무 좋아 짱짱', '광주 너무 좋아 짱짱', '강릉 너무 좋아 짱짱', '대전 너무 좋아 짱짱', '충청도 대전 좋아']

    fv = feature_vector()

    print(fv.evaluation('서울', D_p, D_n))
    print(fv.evaluation('광진구', D_p, D_n))
    print(fv.evaluation('경기도', D_p, D_n))
    print(fv.evaluation('부산', D_p, D_n))
    print(fv.evaluation('광주', D_p, D_n))
    print(fv.evaluation('짱짱', D_p, D_n))

    # keyterms 5개까지 뽑음
    key_terms = fv.key_terms(D_p, D_n, evaluation_threshold=5)
    print(key_terms)

    vec, vec_label = fv.get_feature_vec(key_terms, D_p, D_n)
    print(vec)
    print(vec_label)