"""
Keep track of all of the forms used to request predictions and retrain the model in an out of the way place
"""

from wtforms import Form, BooleanField, FloatField, IntegerField, StringField, validators


class EmployeeIdForm(Form):
    """
    Handle backend communications for the button associated with generating predictions based on Employee ID
    """
    emp_id = IntegerField('Employee ID', [
        validators.DataRequired()
    ])


class RetrainModelForm(Form):
    """
    Handle backend communications for the button associated with retraining the model based on Employee ID
    """
    emp_id = IntegerField('Most Recent Employee ID to Consider', [
        validators.DataRequired()
    ])


class NewEmployeeForm(Form):
    """
    Handle backend communications for the button associated with generating predictions on a hypothetical employee
    """
    satisfaction_level = FloatField('Satisfaction Level, ranging from 0 to 1', [
        validators.DataRequired()#,
        # validators.number_range(0, 1)
    ])
    last_evaluation = FloatField('Last Evaluation, ranging from 0 to 1', [
        validators.DataRequired()#,
        #validators.number_range(0, 1)
    ])
    number_project = IntegerField('Number of Projects, at least zero', [
        validators.DataRequired()#,
        #validators.number_range(min=0)
    ])
    average_montly_hours = IntegerField('Average Monthly Hours, at least zero', [
        validators.DataRequired()#,
        #validators.number_range(min=0)
    ])
    time_spend_company = IntegerField('Time Spent at Company, at least zero', [
        validators.DataRequired()#,
        #validators.number_range(min=0)
    ])
    Work_accident = StringField('Work Accident, True or False', [
        validators.DataRequired(),
        validators.any_of(["True", "False", "true", "false", "0", "1"])
        # ideally, this is a BooleanField
    ])
    promotion_last_5years = StringField('Promotion Within Last 5 Years, True or False', [
        validators.DataRequired(),
        validators.any_of(["True", "False", "true", "false", "0", "1"])
        # ideally, this is a BooleanField
    ])
    department = StringField('Depatrment', [
        validators.DataRequired()
    ])
    salary = StringField('Salary Band', [
        validators.DataRequired()
    ])
