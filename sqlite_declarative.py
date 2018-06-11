"""
Declare SQL Alchemy class objects for database interactions.
When run as main method, initialize class references.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy import BIGINT, Column, FLOAT, INTEGER, TEXT
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Employee(Base):
    __tablename__ = 'all_HR_data'
    Emp_ID = Column(INTEGER, primary_key=True)
    satisfaction_level = Column(FLOAT, nullable=False)
    last_evaluation = Column(FLOAT, nullable=False)
    number_project = Column(BIGINT, nullable=False)
    average_montly_hours = Column(BIGINT, nullable=False)
    time_spend_company = Column(BIGINT, nullable=False)
    Work_accident = Column(BIGINT, nullable=False)
    promotion_last_5years = Column(BIGINT, nullable=False)
    department = Column(TEXT, nullable=False)
    salary = Column(TEXT, nullable=False)
    left = Column(BIGINT, nullable=False)


if __name__ == "main":
    # Create an engine that stores data in the local directory's
    # sqlalchemy_example.db file.
    engine = create_engine('sqlite:///sqlalchemy_example.db')

    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)
