"""
Helper functions for querying and writing to the SQLite database
"""

import os
import sys
from sqlalchemy import create_engine, func, funcfilter
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from jellyfish import jaro_winkler
import pandas as pd
import numpy as np


from sqlite_declarative import Employee, Base
from HRmodel import FEATURES, DEPARTMENT_OPTIONS, SALARY_OPTIONS


def get_session(database_address):
    """
    Helper function for instantiating a database session.

    :param database_address: Address of the database
    :return: Session object
    """
    engine = create_engine(database_address)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def get_employee_by_id(Emp_ID):
    """
    Ideally, we can generalize this to allow for querying employees by any of their features

    :param Emp_ID: Employee ID number
    :return: employee record or empty if employee not found.
    """
    session = get_session('sqlite:///HR_sqlite.db')
    employee = session.query(Employee).filter(Employee.Emp_ID == Emp_ID).first()
    session.commit()
    return employee


def get_employees_by_max_id(Emp_ID):
    """
    Get a set of all employees, up to a nax enmoloyee ID, for use in retraining model.

    :param Emp_ID: MAx employee ID considered
    :return: Set of employees
    """
    session = get_session('sqlite:///HR_sqlite.db')
    employees = session.query(Employee).filter(Employee.Emp_ID <= Emp_ID).all()
    session.commit()
    return employees


def employee_to_df(employee):
    """
    Wnen given an Employee instance, return observation in the form of a data frame. Fuzzy match appropriate fields.

    :param employee: Employee class instance from sqlite_declarative.
    :return: Single row data frame.
    """
    payload = [[
        employee.satisfaction_level,
        employee.last_evaluation,
        employee.number_project,
        employee.average_montly_hours,
        employee.time_spend_company,
        employee.Work_accident,
        employee.promotion_last_5years,
        fuzzy_match(employee.department, DEPARTMENT_OPTIONS),
        fuzzy_match(employee.salary, SALARY_OPTIONS)
    ]]
    return pd.DataFrame(payload, columns=FEATURES)


def employee_group_to_df(employees):
    """
    Wnen given an set of Employee instances, return observations in the form of a data frame.
    Fuzzy match appropriate fields.

    :param employees: List of Employee class instances from sqlite_declarative.
    :return: Single row data frame.
    """
    payload = []
    for employee in employees:
        row = [
            employee.Emp_ID,
            employee.satisfaction_level,
            employee.last_evaluation,
            employee.number_project,
            employee.average_montly_hours,
            employee.time_spend_company,
            employee.Work_accident,
            employee.promotion_last_5years,
            fuzzy_match(employee.department, DEPARTMENT_OPTIONS),
            fuzzy_match(employee.salary, SALARY_OPTIONS),
            employee.left
        ]
        payload.append(row)

    colnames = ["Emp_ID"]
    colnames.extend(FEATURES)
    colnames.append("left")
    return pd.DataFrame(payload, columns=colnames)


def get_max_id():
    """
    :return: Maximum employee ID from database, for use in adding new employees
    """
    session = get_session('sqlite:///HR_sqlite.db')
    max_id = session.query(Employee, func.max(Employee.Emp_ID)).first()[1]
    session.commit()
    return max_id



def add_employee(Emp_ID=None, satisfaction_level=None, last_evaluation=None, number_project=None,
                 average_montly_hours=None, time_spend_company=None, Work_accident=None,
                 promotion_last_5years=None, department=None, salary=None, left=None):
    """
    If the form was successfully and completely filled out, add a new employee to our HR database.

    :param Emp_ID: Only to be set if we are okay with overwriting a current employee
    :param satisfaction_level: Must be filled out, if out of bounds, clip to range (0, 1)
    :param last_evaluation: Must be filled out, if out of bounds, clip to range (0, 1)
    :param number_project: Must be filled out, default 0
    :param average_montly_hours:
    :param time_spend_company:
    :param Work_accident:
    :param promotion_last_5years:
    :param department:
    :param salary:
    :param left:
    :return: True if addition was successful, false otherwise.
    """

    # Replace input terms with fuzzy match for ease of use
    department = fuzzy_match(department, DEPARTMENT_OPTIONS)
    salary = fuzzy_match(salary, SALARY_OPTIONS)

    # auto increment employee ID
    if Emp_ID is None:
        Emp_ID = get_max_id() + 1

    # record employee information
    session = get_session('sqlite:///HR_sqlite.db')
    try:
        session.add(Emp_ID=Emp_ID,
                    satisfaction_level=satisfaction_level,
                    last_evaluation=last_evaluation,
                    number_project=number_project,
                    average_montly_hours=average_montly_hours,
                    time_spend_company=time_spend_company,
                    Work_accident=Work_accident,
                    promotion_last_5years=promotion_last_5years,
                    department=department, salary=salary, left=left
                    )
    except Exception:
        return False

    session.commit()
    return True


def fuzzy_match(term, options):
    """
    Helper function for fuzzy matching malformed text fields

    :param term: Term to fuzzy match
    :param options: Accepted field values for column of given term
    :return: Closest accepted field value
    """
    scores = [jaro_winkler(term.lower(), o.lower()) for o in options]
    closest = options[np.argmax(scores)]
    return closest


def clip_numeric(val, min_val=None, max_val=None):
    """
    Helper function for keeping search and input terms in bounds.

    :param val: Value that we wish to keep "in bounds"
    :param min_val: Minimum accepted value
    :param max_val: Maximum accepted value
    :return: Clipped numeric value
    """

    if min_val:
        val = np.max([val, min_val])

    if max_val:
        val = np.min([val, max_val])

    return val