"""
The purpose of this module is to quickly launch an XGB classifier, training the model and serializing it for use
in the Flask application. We also write out a sample predictions file, to verify that all processes worked.

All contained processes get used in the modeling pipeline.
"""

import os
import pickle
import datetime
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from collections import defaultdict

# Use all the features from the original dataset (note typo in 'average_montly_hours')
FEATURES = [
    'satisfaction_level',
    'last_evaluation',
    'number_project',
    'average_montly_hours',
    'time_spend_company',
    'Work_accident',
    'promotion_last_5years',
    'department', 'salary'
]

DEPARTMENT_OPTIONS = [
    'IT',
    'RandD',
    'accounting',
    'hr',
    'management',
    'marketing',
    'product_mng',
    'sales',
    'support',
    'technical']

SALARY_OPTIONS = ['high', 'low', 'medium']

# sklearn doesn't handle categorical features automatically, so we need to change them to columns of integer values.
NONNUMERIC_COLUMNS = ['department', 'salary']


def proc_df(df, d=None):
    """
    Pre-process data frame, applying label encoding.

    :param df: Data frame to process
    :param d: Lookup table for label encoding. Will use if provided, will generate if not.
    :return: Processed data frame, mappings
    """

    if d is None:
        d = defaultdict(preprocessing.LabelEncoder)
        df[NONNUMERIC_COLUMNS] = df[NONNUMERIC_COLUMNS].apply(lambda x: d[x.name].fit_transform(x))
    else:
        df[NONNUMERIC_COLUMNS] = df[NONNUMERIC_COLUMNS].apply(lambda x: d[x.name].transform(x))
    return df, d


def train_model(train_df, n_est=100, seed=1234):
    """
    This example uses Gradient Boosted Decision Trees from scikit-learn

    :param train_df: training data frame for the model
    :param n_est: Number of estimators to use
    :param seed: Random seed for reporducible results
    :return: Trained model
    """
    GB = GradientBoostingClassifier(n_estimators=n_est,
                                    random_state=seed
                                    ).fit(train_df[FEATURES], train_df['left'])
    return GB


def dump_pickle(object, out_path):
    """
    Dump an object into a pickle serialization for later use

    :param object: Object that we wish to serialize
    :param out_path: Where to write object out to
    :return: None
    """
    output = open(out_path, 'wb')
    pickle.dump(object, output)
    output.close()


def df_new_emp(satisfaction_level, last_evaluation, number_project,
    average_montly_hours, time_spend_company, Work_accident,
    promotion_last_5years, department, salary):
    """
    When given the information about an employee, construct a data frame that holds their information

    :param satisfaction_level:
    :param last_evaluation:
    :param number_project:
    :param average_montly_hours:
    :param time_spend_company:
    :param Work_accident:
    :param promotion_last_5years:
    :param department:
    :param salary:
    :return: hard prediction, class porbability, original data
    """
    df_row = [[
        satisfaction_level, last_evaluation, number_project,
        average_montly_hours, time_spend_company, Work_accident,
        promotion_last_5years, department, salary
    ]]
    test_df = pd.DataFrame(df_row, columns=FEATURES)

    return test_df


def most_recent_model():
    """
    Get most recently trained model and encodings for use in model predictions
    :return: Model and encodings
    """
    GB_path = max([m.split("_", 1)[1] for m in os.listdir("models")])
    le_path = max([m.split("_", 1)[1] for m in os.listdir("encodings")])

    d = pickle.load(open('encodings/le_{}'.format(le_path), "rb"))
    GB = pickle.load(open('models/GB_{}'.format(GB_path), "rb"))
    return GB, d


def predict_employee_churn(test_df):
    """
    When given the information about an employee, predict whether or not they will churn and return related info

    :param test_df:
    :return:
    """
    GB, d = most_recent_model()
    test_df, _ = proc_df(test_df, d)
    pred = GB.predict(test_df)[0]
    proba = GB.predict_proba(test_df)[0][pred]

    # recomstruct original info
    test_df[NONNUMERIC_COLUMNS] = test_df[NONNUMERIC_COLUMNS].apply(lambda x: d[x.name].inverse_transform(x))

    return bool(pred), round(proba, 4), test_df


def df_row_to_dict(df):
    """
    Convert prediction into usable dictionary for pretty printing within app

    :param df: Row of data frame to convert. If more than one row, will just take first
    :return: Dictionary representation of data frame.
    """
    orig = df.to_dict()
    [orig.update({k: list(orig[k].values())[0]}) for k in orig.keys()]
    for c in ["Work_accident", "promotion_last_5years"]:
        orig[c] = bool(orig[c])
    return list(orig.items())


if __name__ == "__main__":

    # Grab time stamp
    now = str(datetime.datetime.now()).replace(" ", "_")

    # Load the train and test data frames, as provided in the challenge zip file
    train_df = pd.read_csv('data/train.csv', header=0)
    test_df = pd.read_csv('data/test.csv', header=0)

    train_df, d = proc_df(train_df)
    test_df, _ = proc_df(test_df, d)
    GB = train_model(train_df=train_df)

    # Run model on test data set - it gets a precision of 0.97 and recall of 0.93
    predictions = GB.predict(test_df[FEATURES])
    test_score = GB.score(test_df[FEATURES], test_df['left'])
    print("Score: ", test_score)

    dump_pickle(d, 'encodings/le_{}.pkl'.format(now))
    dump_pickle(GB, 'models/GB_{}.pkl'.format(now))

    # Change categoricals back to original values
    test_df[NONNUMERIC_COLUMNS] = test_df[NONNUMERIC_COLUMNS].apply(lambda x: d[x.name].inverse_transform(x))
    test_df['Prediction'] = pd.Series(predictions, index=test_df.index)

    # Submit final predictions on test data set
    test_df.to_csv("predictions/submission_GB.csv", index=False)
