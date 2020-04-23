from bs4 import BeautifulSoup
import xlwt
import csv
import math

def get_limits(path):
    excel = open(path,"r")
    dict_topic_limits ={}
    lines=excel.readlines()
    for line in lines:
        columns = line.split(',')
        dict_topic_limits[columns[0].strip('[""""]')]={"Lower_limit":int(columns[1].strip()),"Upper_limit":int(columns[2].strip())}
    return dict_topic_limits

def check_limits(topic_count,dict_topic_limits):
    print(dict_topic_limits)
    limit_fails=[]
    for key in topic_count:
        if (topic_count[key] < dict_topic_limits[key]["Lower_limit"]):
            limit_fails.append(key)
            for i in range (len(limit_fails)):
                print("TEST CANNOT BE CREATED because"+str(limit_fails[i])+"have questions less than lower limit")
        elif(topic_count[key>dict_topic_limits[key]["Upper_limit"]]):
                print("running")

def get_question_bank(path):
    excel = open(path,"r")
    # reader = csv.reader(excel, delimiter=',')
    array_question_bank = []
    topic=[]
    dict_topic_count = {}
    lines = excel.readlines()
    for line in lines:     
        columns = line.split(',')
        array_question_bank.append({"QID": columns[0].strip(),"assessment":columns[1].strip(),"topic":columns[2].strip('[""""]'),"tag":columns[3].strip()})        
    return array_question_bank

def get_topic_count(array_question_bank,current_assesment):    
    dict_topic_count = {}
    for question in array_question_bank:    
            topic = question["topic"]
            qb_assesment = question["assessment"]
            if(qb_assesment == current_assesment):
                if topic in dict_topic_count :
                    dict_topic_count[topic] = dict_topic_count[topic] + 1   
                else:
                    dict_topic_count[topic] = 1
    return dict_topic_count
    
# extract question, calc ratio, total ques
def stats(dict_topic_count,total_questions,dict_topic_decimal):
    total_topic_question = 0
    # dict_topic_decimal={}
    for i in dict_topic_count: 
        total_topic_question = total_topic_question + dict_topic_count[i]
    # print (sum)
    ratio = 0.0
    for i in dict_topic_count:
        ratio = dict_topic_count[i]*total_questions/total_topic_question
        ceiling= math.ceil(ratio)
        decimal_value=round((ratio*10)%10)/10
        floor = math.floor(ratio)
        dict_topic_count[i] = floor
        if i in dict_topic_decimal:
            dict_topic_decimal[i] = decimal_value + dict_topic_decimal[i]
        else:
            dict_topic_decimal[i] = decimal_value
    #print_dict(dict_topic_count)
    return dict_topic_count,dict_topic_decimal

def print_dict(dict):
    for i in dict:
        print(i,dict[i])
    print("\n")


def brahmastra(topic_decimal, topic_floor):
    ques_sum=0
    for i in topic_floor:
        ques_sum = topic_floor[i]+ques_sum
    remaining_question = total_questions-ques_sum
    count = 0
    # dict_sorted = {value:key for key, value in topic_decimal.items()}

    for i in range(0,remaining_question):
        # if count == remaining_question:
        #     break
        topic = max(topic_decimal, key=topic_decimal.get)
        topic_floor[topic] = topic_floor[topic] + 1 
        topic_decimal[topic] = 0 if topic_floor[topic] - 1 < 0 else topic_floor[topic] - 1 
        count+=1
    return topic_decimal,topic_count

def export_question():
    print()


assessment_areas = ["Logical Reasoning/ Data Interpretation","Verbal Ability","Quantitative Aptitude"]
question_bank = get_question_bank("C:/Users/hp/Desktop/MyCodes/python codes/test_maker/QB.csv")
topic_limits=get_limits("C:/Users/hp/Desktop/MyCodes/python codes/test_maker/limits.csv")
question_distribution = { assessment_areas[0]: 15, assessment_areas[1] : 30,assessment_areas[2]: 20}
decimal_bucket={assessment_areas[0]:{}, assessment_areas[1]:{ }, assessment_areas[2]:{},}

for assessment in question_distribution :
    
    total_questions = question_distribution[assessment]
    topic_count = get_topic_count(question_bank,assessment)
    # check_limits(topic_count,topic_limits)
    topic_question_distribution,decimal_bucket[assessment] = stats(topic_count,total_questions,decimal_bucket[assessment])
    decimal_bucket[assessment],topic_question_distribution = brahmastra(decimal_bucket[assessment],topic_question_distribution)
    print_dict(decimal_bucket)
    print_dict(topic_question_distribution)