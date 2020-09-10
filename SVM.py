from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import KFold
import numpy as np

class SVM():

    def linear_SVM(self, X, y, epoch=5):
        best_score = 0

        for C in [0.001, 0.01, 0.1, 1, 10, 100]:
            tmp_score = []
            for e in range(epoch):
                linear_svc = SVC(kernel = 'linear', C = C)
                kfold = KFold(n_splits=2, shuffle=True)
                scores = cross_val_score(linear_svc, X, y, cv=kfold)
                tmp_score.append(np.mean(scores))
            if np.mean(tmp_score) > best_score:
                best_score = np.mean(tmp_score)
                best_parameters = {'C': C}

            print('C: {} => Score: {:.3f}'.format(C, np.mean(tmp_score)))

        linear_svc = SVC(kernel = 'linear', **best_parameters)
        linear_svc.fit(X, y)

        return best_score, linear_svc


    def polynomial_SVM(self, X, y, epoch=5):
        best_score = 0

        for gamma in [0.001, 0.01, 0.1, 1, 10, 100]:
            for C in [0.001, 0.01, 0.1, 1, 10, 100]:
                print('{}, {}'.format(gamma, C))
                tmp_score = []
                for e in range(epoch):
                    print(tmp_score)
                    poly_svc = SVC(kernel = 'poly', C = C, gamma = gamma)
                    kfold = KFold(n_splits=2, shuffle=True)
                    scores = cross_val_score(poly_svc, X, y, cv=kfold)
                    tmp_score.append(np.mean(scores))
                if np.mean(tmp_score) > best_score:
                    best_score = np.mean(tmp_score)
                    best_parameters = {'C': C, 'gamma': gamma}

                print('gamma: {}, C: {} => Score: {:.3f}'.format(gamma, C, np.mean(tmp_score)))

        poly_svm = SVC(kernel = 'poly', **best_parameters)
        poly_svm.fit(X, y)

        return best_score, poly_svc


    def gaussian_SVM(self, X, y, epoch=5):
        best_score = 0

        for gamma in [0.001, 0.01, 0.1, 1, 10, 100]:
            for C in [0.001, 0.01, 0.1, 1, 10, 100]:
                tmp_score = []
                for e in range(epoch):
                    rbf_svc = SVC(kernel = 'rbf', C = C, gamma = gamma)
                    kfold = KFold(n_splits=2, shuffle=True)
                    scores = cross_val_score(rbf_svc, X, y, cv=kfold)
                    tmp_score.append(np.mean(scores))
                if np.mean(tmp_score) > best_score:
                    best_score = np.mean(tmp_score)
                    best_parameters = {'C': C, 'gamma': gamma}
                
                print('gamma: {}, C: {} => Score: {:.3f}'.format(gamma, C, np.mean(tmp_score)))

        rbf_svm = SVC(kernel = 'rbf', **best_parameters)
        rbf_svm.fit(X, y)

        return best_score, rbf_svc


    def predict(self, X, model):
        return model.predict(X)


if __name__ == "__main__":
    # 테스트 데이터 생성
    from sklearn.datasets import make_moons
    X, y = make_moons(n_samples = 400, noise = 0.25, random_state = 42)

    svm = SVM()
    accuracy, model = svm.linear_SVM(X, y, epoch=5)
    print('best accuracy: {}'.format(accuracy))
    print(model)
    
    predict_target = svm.predict(X, model)
    