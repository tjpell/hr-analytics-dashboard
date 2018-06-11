"""
Support the backend of the employee churn prediction model.
"""

from flask import flash, Flask, redirect, render_template, request, url_for

from HRmodel import *
from forms import *
from database_operations import *


app = Flask(__name__)
app.secret_key = 'some_secret'  # this should be replaced later on with a big, secure hash


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')


@app.route('/train', methods=['GET', 'POST'])
def base_train():
    train_model_form = RetrainModelForm()
    return render_template('train.html', train_model_form=train_model_form)


@app.route('/new_model', methods=['GET', 'POST'])
def report_model():
    train_model_form = RetrainModelForm(request.form)
    if request.method == 'POST' and train_model_form.validate():
        emp_id = train_model_form.emp_id.data

        if emp_id < 340:
            flash("We're sorry, it looks like that is too small of an employee ID.")
            return redirect('/train')

        # collect employee info
        employees = get_employees_by_max_id(emp_id)
        employee_df = employee_group_to_df(employees)

        # train model and report fit
        train_df, test_df = train_test_split(employee_df, train_size=0.8)
        train_df, d = proc_df(train_df)
        test_df, _ = proc_df(test_df)

        try:
            GB = train_model(train_df)
        except ValueError:
            flash("We're sorry, it looks like was not an approptiate employee ID, and all \
                    employees from this segment have left the company.")
            return redirect('/train')

        test_score = round(GB.score(test_df[FEATURES], test_df['left']), 4)

        # Save model info for later reference, tracking creation date. In future, also include test score
        now = str(datetime.datetime.now()).replace(" ", "_")
        dump_pickle(GB, 'models/GB_{}.pkl'.format(now))
        dump_pickle(d, 'encodings/le_{}.pkl'.format(now))

        return render_template('new_model.html', test_score=test_score, emp_id=str(emp_id))

    flash("We're sorry, it looks like there wsa an error in your form.")
    return redirect('/train')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    id_form = EmployeeIdForm()
    new_emp_form = NewEmployeeForm()
    return render_template('predict.html', id_form=id_form, new_emp_form=new_emp_form)


@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    emp_id_form = EmployeeIdForm(request.form)
    new_emp_form = NewEmployeeForm(request.form)
    if request.method == 'POST' and emp_id_form.validate():
        emp_id = emp_id_form.emp_id.data
        employee = get_employee_by_id(emp_id)

        if employee is None:
            flash("We're sorry, it looks like that employee isn't in the system.")
            return redirect('/predict')

        test_df = employee_to_df(employee)
        pred, proba, info = predict_employee_churn(test_df)
        info = df_row_to_dict(info)

    elif request.method == 'POST' and new_emp_form.validate():
        emp_id = "custom"

        # get all the data from the form
        satisfaction_level = float(new_emp_form.satisfaction_level.data)
        last_evaluation = float(new_emp_form.last_evaluation.data)
        number_project = float(new_emp_form.number_project.data)
        average_montly_hours = int(new_emp_form.average_montly_hours.data)
        time_spend_company = int(new_emp_form.time_spend_company.data)
        Work_accident = bool(new_emp_form.Work_accident.data)
        promotion_last_5years = bool(new_emp_form.promotion_last_5years.data)
        department = str(new_emp_form.department.data)
        salary = str(new_emp_form.salary.data)

        # consider using fuzzy matching for the string fields.
        test_df = df_new_emp(
            clip_numeric(satisfaction_level, 0, 1),
            clip_numeric(last_evaluation, 0, 1),
            clip_numeric(number_project, min_val=0),
            clip_numeric(average_montly_hours, min_val=0),
            clip_numeric(time_spend_company, min_val=0),
            Work_accident,
            promotion_last_5years,
            fuzzy_match(department, DEPARTMENT_OPTIONS),
            fuzzy_match(salary, SALARY_OPTIONS)
        )
        pred, proba, info = predict_employee_churn(test_df)
        info = df_row_to_dict(info)

    if request.method == 'POST' and (emp_id_form.validate() or new_emp_form.validate()):
        # totally valid request, move along
        return render_template('prediction.html', pred=str(pred).lower(), proba=proba, info=info, emp_id=str(emp_id))

    # information was missing from one of the above entry fields if we've made it this far
    flash("We're sorry, it looks like you missed one of the fields.")
    return redirect('/predict')


if __name__ == '__main__':
    # for testing purposes
    app.run(host='0.0.0.0', port=8080)
