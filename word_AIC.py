import math

class feature_vector():

    def __init__(self):
        pass


    def AIC(self, max_like, free_param_num):
        return -2 * max_like + 2 * free_param_num
        # log가 들어가야 하는건지 안 들어가야 하는 건지 잘 모르겠음
        # 논문 (1) 공식에는 log가 들어가지만,
        # 논문 (3) 공식에는 log가 안 들어감.
        # -> max_likelihood가 음수가 나오면 log 오류남. 그래서 log 일단 빼는 거로 결정.


    # t = term, D_p = Document postivie list, D_n = Document negative list
    def calculation(self, t, D_p, D_n):

        # Documents count for calculation of AIC
        N11_t, N12_t, N21_t, N22_t = 0.001, 0.001, 0.001, 0.001   # t appears in D_p, t does not appear in D_p, t appears in D_n, t does not appear in D_n
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
        # 일단은 모두 초기값을 0.001로 수정해줘서 오류나지 않게 넘어감.
        mll_dm_t = N11_t * math.log(N11_t) + N12_t*math.log(N12_t) + N21_t*math.log(N21_t) + N22_t*math.log(N22_t) - N*math.log(N)
        mll_im_t = N_p*math.log(N_p) + N_t*math.log(N_t) +  N_n*math.log(N_n) + N_not_t*math.log(N_not_t) + (-2)*N*math.log(N)
        
        return mll_dm_t, mll_im_t, N_all
    

    def evaluation(self, term, D_p, D_n):
        mll_dm_t, mll_im_t, N_all = self.calculation(term, D_p, D_n)
        AIC_dm = self.AIC(mll_dm_t, 3)
        AIC_im = self.AIC(mll_im_t, 2)
        if N_all[5]/N_all[3] > N_all[6]/N_all[4]:
            E_t = AIC_im - AIC_dm + 2
        else:
            E_t = AIC_dm - AIC_im - 2
        return E_t


if __name__ == "__main__":
    D_p = ['서울 너무 좋아 짱짱']
    D_n = ['부산 너무 좋아 짱짱', '광주 너무 좋아 짱짱', '강릉 너무 좋아 짱짱', '대전 너무 좋아 짱짱']
    fv = feature_vector()
    print(fv.evaluation('서울', D_p, D_n))
    print(fv.evaluation('부산', D_p, D_n))
    print(fv.evaluation('광주', D_p, D_n))
    print(fv.evaluation('짱짱', D_p, D_n))