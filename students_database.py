import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime as dt

# Work with students database in Udacity website
# Find some insights and make some analysis


def read_csv(filename):
    """Read cvs files as dict()"""
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)


def get_int(i):
    """Get int number from str"""
    if i == '':
        return 0
    else:
        return int(i)


def parse_date(date):
    """Parse str to data object in yy-mm-dd"""
    if date == '':
        return None
    else:
        return dt.strptime(date, '%Y-%m-%d')


def within_one_week(join_date, engagement_date):
    """Get if time is within one week"""
    time_delta = parse_date(engagement_date) - parse_date(join_date)
    return time_delta.days < 7


def remove_free_trial_cancels(data):
    """Remove free trial cancels"""
    new_data = []
    for data_point in data:
        if data_point['account_key'] in paid_students:
            new_data.append(data_point)
    return new_data


def sum_by_field(data, field):
    """Sum some data for each account using daily_engagement database"""
    summed_data = defaultdict(list)
    for engagement in daily_engagement:
        if engagement['account_key'] in data.keys():
            summed_data[engagement['account_key']].append(float(engagement[field]))
    for key, value in summed_data.items():
        summed_data[key] = sum(value)
    return summed_data


def find_total_days(data):
    """Check if student visit lessons in some days"""
    summed_data = defaultdict(list)
    for engagement in daily_engagement:
        if engagement['account_key'] in data.keys():
            if engagement['num_courses_visited'] != '0':
                summed_data[engagement['account_key']].append(1)
    for key, value in summed_data.items():
        summed_data[key] = sum(value)
    return summed_data


def group_data(data, key_name):
    """Groups data by key_name"""
    grouped_data = defaultdict(list)
    for data_point in data:
        key = data_point[key_name]
        grouped_data[key].append(data_point)
    return grouped_data


def describe_data(data):
    print('Mean:', np.mean(data))
    print('Standard deviation:', np.std(data))
    print('Minimum:', np.min(data))
    print('Maximum:', np.max(data))


#Open and read files
enrollments = read_csv('enrollments.csv')
daily_engagement = read_csv('daily_engagement.csv')
project_submissions = read_csv('project_submissions.csv')

#Find unique students
unique_enrolled_students = set()
for enrollment in enrollments:
    unique_enrolled_students.add(enrollment['account_key'])
unique_engagement_students = set()
for engagement_record in daily_engagement:
    unique_engagement_students.add(engagement_record['account_key'])
unique_project_submitters = set()
for submission in project_submissions:
    unique_project_submitters.add(submission['account_key'])

#Check for more problems
num_problem_students = 0
for enrollment in enrollments:
    student = enrollment['account_key']
    if (student not in unique_engagement_students and
            enrollment['join_date'] != enrollment['cancel_date']):
        num_problem_students += 1

#Find udacity account keys
udacity_accounts =[]
for enrollment in enrollments:
    if enrollment['is_udacity'] == 'True':
        udacity_accounts.append(enrollment['account_key'])

#Find udacity enrollments
udacity_enrollments = []
for enrollment in enrollments:
    if enrollment['account_key'] in udacity_accounts:
        udacity_enrollments.append(enrollment)

#Find udacity engagements
udacity_engagements = []
for engagement in daily_engagement:
    if engagement['account_key'] in udacity_accounts:
        udacity_engagements.append(engagement)

#Find udacity submissions
udacity_submissions = []
for submission in project_submissions:
    if submission['account_key'] in udacity_accounts:
        udacity_submissions.append(submission)

#Find non udacity enrollments
non_udacity_enrollments = []
for enrollment in enrollments:
    if enrollment['account_key'] not in udacity_accounts:
        non_udacity_enrollments.append(enrollment)

# Find udacity engagements
non_udacity_engagement = []
for engagement in daily_engagement:
    if engagement['account_key'] not in udacity_accounts:
        non_udacity_engagement.append(engagement)

# Find udacity submissions
non_udacity_submissions = []
for submission in project_submissions:
    if submission['account_key'] not in udacity_accounts:
        non_udacity_submissions.append(submission)

#Find paid students
paid_students = {}
for enrollment in non_udacity_enrollments:
    if (not enrollment['is_canceled'] or
            get_int(enrollment['days_to_cancel']) > 7):
        account_key = enrollment['account_key']
        enrollment_date = enrollment['join_date']
        if (account_key not in paid_students or
                enrollment_date > paid_students[account_key]):
            paid_students[account_key] = enrollment_date

#Get database only for paid students
paid_enrollments = remove_free_trial_cancels(non_udacity_enrollments)
paid_engagement = remove_free_trial_cancels(non_udacity_engagement)
paid_submissions = remove_free_trial_cancels(non_udacity_submissions)

#Find paid data base in first week
paid_engagement_in_first_week = []
for engagement_record in paid_engagement:
    account_key = engagement_record['account_key']
    join_date = paid_students[account_key]
    engagement_record_date = engagement_record['utc_date']

    if within_one_week(join_date, engagement_record_date):
         paid_engagement_in_first_week.append(engagement_record)

#Subway project
subway_project_lesson_keys = ['746169184', '3176718735']
#Find students who pass this project
pass_subway_project = set()

for submission in paid_submissions:
    project = submission['lesson_key']
    rating = submission['assigned_rating']

    if ((project in subway_project_lesson_keys) and
            (rating == 'PASSED' or rating == 'DISTINCTION')):
        pass_subway_project.add(submission['account_key'])

#Divide students into non pass group and pass group
passing_engagement = []
non_passing_engagement = []

for engagement_record in paid_engagement_in_first_week:
    if engagement_record['account_key'] in pass_subway_project:
        passing_engagement.append(engagement_record)
    else:
        non_passing_engagement.append(engagement_record)

#Comapare two students groups
#Data for students who don`t
passing_engagement_by_account = group_data(passing_engagement,'account_key')
non_passing_engagement_by_account = group_data(non_passing_engagement,'account_key')

#Get minutes for students
passing_minutes = sum_by_field(passing_engagement_by_account, "total_minutes_visited")
non_passing_minutes = sum_by_field(non_passing_engagement_by_account, "total_minutes_visited")

print("Minutes for passing students")
describe_data(np.array(list(passing_minutes.values())))
print("Minutes for non-passing students")
describe_data(np.array(list(non_passing_minutes.values())))

#Get lessons for students
passing_lessons = sum_by_field(passing_engagement_by_account, "lessons_completed")
non_passing_lessons = sum_by_field(non_passing_engagement_by_account, "lessons_completed")

print("Lessons for passing students")
describe_data(np.array(list(passing_lessons.values())))
print("Lessons for non-passing students")
describe_data(np.array(list(non_passing_lessons.values())))

#Get days for students
passing_days = find_total_days(passing_engagement_by_account)
non_passing_days = find_total_days(non_passing_engagement_by_account)

print("Days for passing students")
describe_data(np.array(list(passing_days.values())))
print("Days for non-passing students")
describe_data(np.array(list(non_passing_days.values())))

#Making histograms
plt.hist(list(non_passing_days.values()), bins=8, rwidth= 0.9, label="Passing students")
plt.legend()
plt.xlabel('Number of days')
plt.title("Compare students who pass project and who don`t")
plt.hist(list(passing_days.values()), bins=8, rwidth=0.9, label="Non-passing students")
plt.show()