# import pandas as pd
# train = pd.read_csv("features_train.csv")
# test = pd.read_csv("features_test.csv")
# #print("TRAIN:\n", train["label"].value_counts())
# #print("\nTEST:\n", test["label"].value_counts())

# print(test[["chin_to_jaw_ratio", "jaw_angle", "jowl_taper_ratio"]].describe())

from src.recommender import recommend_glasses

result = recommend_glasses("Oval")
print(result)