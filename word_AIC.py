import math
from nltk.tokenize import RegexpTokenizer
from chatspace import ChatSpace
from konlpy.tag import Mecab
from tc_tagger.TC_tagger import Tagger
import pandas as pd
import os


class feature_vector:

    def __init__(self, tokenizer = 'tc'):
        self.spacer = ChatSpace()
        self.mecab = Mecab()
        self.tc_tagger = Tagger()
        self.tokenizer = tokenizer
        self.retokenize = RegexpTokenizer("[\w]+")
        


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
        tmp = []
        print('tokenizer: '+self.tokenizer)
        for text in D:
            # text = self.spacer.space(text)
            if self.tokenizer == 'tc':
                tmp.extend(self.tc_tagger.tokenizer(text))
            else:
                text = ' '.join([x for x in self.retokenize.tokenize(text)])
                tmp.extend(self.mecab.morphs(text))
        term_lst = list(set(tmp))
        return term_lst

    def key_terms(self, D_p, D_n, evaluation_threshold = 2000):
        D = D_p + D_n
        term_lst = self._term_lst(D)
        eval_dic = {t:round(self.evaluation(t, D_p, D_n), 5) for t in term_lst}
        eval_sort = sorted(eval_dic.items(), key=lambda x:x[1], reverse=True)
        key_terms = dict(eval_sort[:evaluation_threshold])
        return key_terms
        

    def get_feature_vec(self, key_terms, D_p, D_n, D_p_id, D_n_id):
        feature_vec = []
        feature_vec_label = []
        key_terms_lst = key_terms.keys()
        feature_dic = {idx:t for idx, t in enumerate(key_terms_lst)}

        for p, p_id in zip(D_p, D_p_id):
            tmp = []
            tmp.append(p_id)
            for t in key_terms_lst:
                if t in p:
                    tmp.append(1)
                else:
                    tmp.append(0)
            feature_vec.append(tmp)
            feature_vec_label.append(1)

        for n, n_id in zip(D_n, D_n_id):
            tmp = []
            tmp.append(n_id)
            for t in key_terms_lst:
                if t in n:
                    tmp.append(1)
                else:
                    tmp.append(0)
            feature_vec.append(tmp)
            feature_vec_label.append(0)

        return feature_dic, feature_vec, feature_vec_label


if __name__ == "__main__":
    root = r'D:\local\insta_profiling\content_labeled'
    content_lst = os.listdir(root)
    cc = pd.read_csv(root+'\\'+content_lst[0])
    gs = pd.read_csv(root+'\\'+content_lst[1])
    gw = pd.read_csv(root+'\\'+content_lst[2])
    jl = pd.read_csv(root+'\\'+content_lst[3])
    sd = pd.read_csv(root+'\\'+content_lst[4])
    df_lst = [cc, gs, gw, jl, sd]
    region_lst = ['cc', 'gs', 'gw', 'jl', 'sd']
    tokenizer = 'mc'  # 'mc'이면 mecab

    for idx in range(len(df_lst)):
        D_p = list(df_lst[idx]['content'])
        D_p_id = list(df_lst[idx]['inner_id'])
        D_n = []
        D_n_id = []

        for other in range(len(df_lst)):
            if other == idx:
                pass
            else:
                D_n.extend(list(df_lst[other]['content']))
                D_n_id.extend(list(df_lst[other]['inner_id']))
        
        fv = feature_vector(tokenizer = tokenizer)

        # keyterms 2000개
        key_terms = fv.key_terms(D_p, D_n, evaluation_threshold=2000)
        print(region_lst[idx])
        print(list(key_terms.keys())[:100])

        feature_dic, vec, vec_label = fv.get_feature_vec(key_terms, D_p, D_n, D_p_id, D_n_id)

        df = pd.DataFrame(columns = ['inner_id'] + list(feature_dic.values()), data = vec)
        df['label'] = vec_label
        df.to_csv(tokenizer+region_lst[idx]+'_fv.csv', index=False)