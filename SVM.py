from sklearn.svm import SVC

class SVM():

    def linear_SVM(self, X, y):
        linear_svc = SVC(kernel = 'linear', probability=True)
        linear_svc.fit(X, y)

        return linear_svc


    def polynomial_SVM(self, X, y):
        poly_svc = SVC(kernel = 'poly', probability=True)
        poly_svc.fit(X, y)

        return poly_svc


    def gaussian_SVM(self, X, y):
        rbf_svc = SVC(kernel = 'rbf', probability=True)
        rbf_svc.fit(X, y)

        return rbf_svc


    def predict(self, X, model):
        return model.predict_proba(X)