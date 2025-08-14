# stage 2
# split the data and save it in data/preprocessed folder

import os
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from get_data import read_params
from sklearn.preprocessing import LabelEncoder

def split_and_save(config_path):
    config = read_params(config_path)
    train_data_path = config["split_data"]["train_path"]
    test_data_path = config["split_data"]["test_path"]
    raw_data_path = config["load_data"]["raw_dataset"]
    split_ratio = config["split_data"]["test_size"]
    random_state = config["base"]["random_state"]

    df = pd.read_csv(raw_data_path, sep=",")
    le = LabelEncoder()

    # Handle both "sex" and "gender" columns
    if "sex" in df.columns:
        df["sex"] = le.fit_transform(df["sex"])
    elif "gender" in df.columns:
        df["gender"] = le.fit_transform(df["gender"])

    train, test = train_test_split(
        df,
        test_size=split_ratio,
        random_state=random_state
    )

    train.to_csv(train_data_path, sep=",", index=False, encoding="utf-8")
    test.to_csv(test_data_path, sep=",", index=False, encoding="utf-8")

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    split_and_save(config_path=parsed_args.config)
