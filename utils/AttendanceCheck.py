from datetime import datetime
import pandas as pd
import numpy as np

rootdir = 'D:/Github/Face-Recognition-Class-Attendance-System/'

filenames = ['Auxiliary_Info.xlsx', 
             'Classroom_Course_Schedule.xlsx',
             'Classroom_Info.xlsx', 
             'College_Class_Info.xlsx', 
             'Attendance_Logs.xlsx']

au_info = pd.read_excel(rootdir + filenames[0])


def calculate_current_teach_week(semester_first_week_date='2021-3-08 08:00:00'):
    """
    计算当前日期所属教学周，实现思路是：当前日期所属一年中的周 - 每学期的第一周
    ----
    param: semester_first_week_date: 学期第一周的日期，例如 '2021-3-08 08:00:00'

    return: 当前教学周
    """
    # 获取指定日期属于当年的第几周, 返回字符串
    semester_first_week = datetime.strptime(semester_first_week_date, '%Y-%m-%d %H:%M:%S').strftime('%W')
    # 获取当前日期是一年中的第几周, 返回字符串
    current_year_week = datetime.now().strftime('%W')
    # 计算当前日期所属的教学周
    # ( ) 中的减一表示第一周之前的周数
    # 最后加一是因为计算周数是从索引00开始的，所以需要加1
    current_teach_week = int(current_year_week) - (int(semester_first_week) - 1) + 1

    return current_teach_week
    
    
def holiday_judgment(judg_time=datetime.now(), holidays=au_info['Holiday Date']):
    """
    判断是否为假期
    ----
    param: judg_time: 需要被判断的时间
    param: holidays: 当前学期的假期列表
    return: 
            如果有课，则返回考勤时间设置；
            如果没课，则返回None，并提示空教室。
    """
    
    # 因为表中有 NaT类型，这在遍历时会导致错误，因此需要先过滤掉NaT值
    # 不包含 NaT 的索引
    indexes_without_nat = [(type(holiday) != type(pd.NaT)) for holiday in au_info['Holiday Date']]
    # 不包含 NaT 的假期列表
    holidays_pure = list(holidays[indexes_without_nat])

    # 获取完整的时间格式
    now = datetime.now()
    # 相同的功能
    judg_time_ymd = now.date()

    # 是否为假期的标志位
    is_now_holiday = False

    # 遍历假期列表
    for holiday in holidays_pure:
        # 截取当前假期的年月日
        holiday_month_day = datetime(holiday.year, holiday.month, holiday.day)
        if judg_time_ymd - holiday_month_day == 0:
            is_now_holiday = True

    if is_now_holiday:
        print(f'[INFO] {judg_time_ymd} is Holiday!')
    else:
        print(f'[INFO] {judg_time_ymd} is not Holiday!')

    return is_now_holiday
        
    
def attendance_check(set_time = '19:00:00'):
    """
    考勤状态判断，根据指定的时间判断考勤状态
    手动设定考勤时间（简单）
    - 1）正常：考勤时间设定之前的一小时内签到
    - 2）迟到：上课之后45分钟内
    - 3）其他：上课超过45分钟
    - 4）旷课：上课时间未到
    - 5）请假：通过销假系统自动读取，或者老师手动填写
    ----
    param set_time: = '19:00:00'
    """
    ####################### 自定义参数 #####################
    # 正常：考勤时间设定之前的一小时内（3600s）签到
    normal_span = 60 * 60  # seconds
    # 设定一节课时长
    course_time = 95  # minutes
    # 设定上课多长时间认为是迟到
    late_span = 45
    ########################################################
    
    # 获取完整的时间格式
    now = datetime.now()
    # 分别获取当前的年，月，日，时，分，秒，均为int类型
    judg_time = now
    now_y = judg_time.year
    now_m = judg_time.month
    now_d = judg_time.day

    # 定义考勤标识符
    att_state = '正常'
    
    # 格式化考勤时间
    att_time = datetime.strptime(f'{now_y}-{now_m}-{now_d} {set_time}', '%Y-%m-%d %H:%M:%S')
    # 计算当前时间与设定时间的差值
    time_diff = now - att_time
    # print(time_diff)
    time_diff_days, time_diff_seconds = time_diff.days, time_diff.seconds
    # print(time_diff_days, time_diff_seconds)

    # 如果time_diff_days为负，说明还未到考勤时间，此时计算距离考勤的时间
    if time_diff_days < 0:
        # 一天的秒数减去time_diff_days
        time_span_att = 60 * 60 * 24 - time_diff_seconds
        

        if time_span_att < normal_span:
            att_state = '正常'
        else:
            print(f'[INFO] 无效！请在考勤时间设定之前的一小时内签到！距离考勤时间设定还有{round((time_span_att - 60*60)/60, 2)}分钟！')

    # 如果time_diff_days为正，说明考勤时间已过，此时判断是否为迟到或旷课
    else:
        
        # 上课45分钟内，算迟到
        if time_diff_seconds - late_span * 60 <= 0:
            att_state = '迟到'
        elif (time_diff_seconds > late_span * 60) and (time_diff_seconds <= course_time * 60):
            att_state = '其他'
            print('[INFO] 已经超过迟到时间范围，请联系老师处理!')
        else:
            att_state = '旷课'

    print(f'[INFO] 时间设定：{att_time}，考勤时间：{now}，考勤状态：{att_state}')
    
    return now, att_state