"""
Test out that we are able to query the database
"""

from HRmodel import *
from database_operations import *


if __name__ == "__main__":

    dept = get_employee_by_id(333).department
    print("Get employee 333's department: {}".format(str(dept)))

    max_id = get_max_id()
    print ("The maximum employee ID is: {}".format(str(max_id)))

    employees = get_employees_by_max_id(400)
    df = employee_group_to_df(employees)
    print (df.head())
