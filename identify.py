import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from app.models import User, Questions, Answers, Normalizations

df = pd.read_csv(r"./Synthetic_dataset.csv")

l = []
for i in range(1, 7):
    kmeans = KMeans(i)
    kmeans.fit(df)
    l_iter = kmeans.inertia_
    l.append(l_iter)
n = range(1, 7)
kmeans = KMeans(2)
kmeans.fit(df)
id_clusters = kmeans.fit_predict(df)
d_clusters = df.copy()
d_clusters["Clusters"] = id_clusters
df["Result"] = id_clusters
x = ["Total", "Emotion"]
X = df.loc[:, x].values
y = ["Result"]
Y = df.loc[:, y].values
x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.25)
svc = SVC()
svc.fit(x_train, y_train)


def learning_speed(user_id):

    answers = Answers.query.filter_by(user_id=user_id).all()
    score = 0.5
    for answer in answers:
        if answer.is_correct == 1:
            question = Questions.query.filter_by(q_id=answer.question_id).first()
            print(question.a, question.score)
            if question.score:
                score = score + question.score
    normalization = Normalizations.query.filter_by(user_id=user_id).first()

    y_predict = svc.predict(
        [[score, normalization.normalization / normalization.current_question]]
    )
    print(y_predict)
    return str(y_predict[0])
