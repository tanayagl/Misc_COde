import csv
import math
import time
import sys

def get_limits(path,input_question_distribution):
    excel = open(path,"r")
    dict_topic_limits ={}
    lines=excel.readlines()
    for line in lines:
        columns = line.split(',')
        dict_topic_limits[columns[1].strip('[""""]')]={"assessment":columns[0].strip(),"Lower_limit":int(columns[2].strip())*input_question_distribution[columns[0].strip()]/20,"Upper_limit":int(columns[3].strip())*input_question_distribution[columns[0].strip()]/20}

    return dict_topic_limits

def check_limits(topic_floor,topic_decimal,dict_topic_limits,total_questions,dict_topic_count):
    print(dict_topic_limits)
    status = 0
    limit_fails=[]
    cross_limit={}
    for key in dict_topic_count:
        if (topic_floor[key] < dict_topic_limits[key]["Lower_limit"]):
            limit_fails.append(key)
            print("TEST CANNOT BE CREATED because following topics have questions less than lower limit \n"+str(limit_fails))
            return -1,cross_limit,topic_decimal
        elif(topic_floor[key]>=dict_topic_limits[key]["Upper_limit"]):
                print("running")
                cross_limit[key]= topic_floor[key]
                #topic_floor[key]=dict_topic_limits[key]["Upper_limit"]
    if bool(cross_limit):
        status,topic_floor,topic_decimal = max_limit_reached_stats(cross_limit,topic_floor,topic_decimal,topic_limits,total_questions,dict_topic_count)
    if status == -1:
        return -1,cross_limit,topic_decimal
    return 0,topic_floor,topic_decimal

def max_limit_reached_stats(cross_limit,topic_floor,topic_decimal,topic_limits,total_questions,dict_topic_count):
    update_limit = topic_floor.copy()
    update_question_count = 0
    updated_sum_tag = {}
    status=0
    updated_topic_count = dict_topic_count.copy()
    for topic in cross_limit:
        updated_topic_count.pop(topic)
        total_questions = total_questions - topic_limits[topic]["Upper_limit"]
    update_question_count = sum(updated_topic_count.values())
    # for topic in cross_limit:
    #     update_question_count = update_question_count - updated_sum_tag[topic]
    #     total_questions = total_questions - topic_limits[topic]["Upper_limit"] 
    ratio = 0.00
    for topic in updated_topic_count:
        ratio = 0.00 if update_question_count==0 else updated_topic_count[topic]*total_questions/update_question_count
        decimal_value = float(str(ratio-int(ratio))[1:])
        floor = math.floor(ratio)
        update_limit[topic] = floor
        topic_decimal[topic] = decimal_value
    for topic in cross_limit:
        update_limit[topic] = topic_limits[topic]["Upper_limit"]
        topic_decimal[topic] = 0.00
    if(bool(updated_topic_count)):
        status,update_limit,topic_decimal = check_limits(update_limit,topic_decimal,topic_limits,total_questions,updated_topic_count)
    if( total_questions > 0 and update_question_count==0):
        print("Humse na ho paaye")
        status = -1
        return status,update_limit,topic_decimal
    return status,update_limit,topic_decimal

def get_question_bank(path):
    excel = open(path,"r")
    # reader = csv.reader(excel, delimiter=',')
    array_question_bank = []
    lines = excel.readlines()
    for line in lines:     
        columns = line.split(',')
        array_question_bank.append({"QID": columns[0].strip(),"assessment":columns[1].strip(),"topic":columns[2].strip('[""""]'),"tag":columns[3].strip().strip('[""""]')})        
    return array_question_bank

# Get child count, for the list of each parent from the question
def get_child_count(array_question_bank,parent_list,qb_parent_header,qb_child_header):    
    dict_parent_child_count = {}
    for parent in parent_list:
        dict_child_count = {}
        for question in array_question_bank:    
            qb_parent = question[qb_parent_header]
            qb_child = question[qb_child_header]
            if(qb_parent == parent):
                if qb_child in dict_child_count :
                    dict_child_count[qb_child] = dict_child_count[qb_child] + 1   
                else:
                    dict_child_count[qb_child] = 1
        dict_parent_child_count[parent] = dict_child_count
    return dict_parent_child_count
    
# extract question, calc ratio, total ques
def stats(dict_topic_count,total_questions):
    topic_decimal = {}
    topic_floor = dict_topic_count.copy()
    total_topic_question = 0
    for topic in dict_topic_count: 
        total_topic_question = total_topic_question + dict_topic_count[topic]
    ratio = 0.00
    for topic in dict_topic_count:
        ratio = 0.00 if total_questions==0 else dict_topic_count[topic]*total_questions/total_topic_question
        decimal_value = float(str(ratio-int(ratio))[1:])
        floor = math.floor(ratio)
        topic_floor[topic] = floor
        topic_decimal[topic] = decimal_value
    return topic_floor,topic_decimal

def print_dict(dict):
    for i in dict:
        print(i,dict[i])
    print("\n")

def update_decimal_bucket(topic_decimal,assessment):
    if(assessment not in decimal_bucket):
        decimal_bucket[assessment] = {}
    if bool(decimal_bucket[assessment]):
        for topic in (decimal_bucket[assessment]):
            decimal_bucket[assessment][topic] = topic_decimal[topic] + decimal_bucket[assessment][topic]
    else:
        decimal_bucket[assessment] = topic_decimal.copy()
    return decimal_bucket

def brahmastra(topic_decimal, topic_floor,assessment,total_questions):
    decimal_bucket = update_decimal_bucket(topic_decimal,assessment) 
    topic_question_distribution = topic_floor.copy()
    ques_sum = 0
    for i in topic_floor:
        ques_sum = topic_floor[i]+ques_sum
    remaining_question = total_questions-ques_sum
    count = 0
    for i in range(0,int(remaining_question)):
        topic = max(decimal_bucket[assessment], key=decimal_bucket[assessment].get)
        topic_question_distribution[topic] = topic_question_distribution[topic] + 1 
        decimal_bucket[assessment][topic] = 0 if topic_decimal[topic] - 1 < 0 else topic_decimal[topic] - 1 
        count+=1
    return topic_question_distribution
    
def export_question(fw,question_distribution,qb_header):
    for topic in question_distribution:
        question_count = question_distribution[topic] 
        for i in range(0,question_count):
            question_found = False
            for question in question_bank:    
                if(question[qb_header]==topic):
                    question_found = True
                    fw.write(str(question["QID"])+","+str(topic)+"\n")
                    print(str(question["QID"])+","+str(topic)+"\n")
                    question_bank.remove(question)
                    question_distribution[topic] = question_distribution[topic] - 1    
                    break       
            if(question_found==False):
                return -1
    return 0        
                
assessment_areas = ["Logical Reasoning/ Data Interpretation","Verbal Ability","Quantitative Aptitude"]
# question_bank = get_question_bank("C:/Users/hp/Desktop/MyCodes/python codes/test_maker/QB.csv")


input_question_distribution = {"Logical Reasoning/ Data Interpretation": 20, "Verbal Ability": 0,"Quantitative Aptitude": 0}
topic_limits=get_limits("C:/Users/hp/Desktop/MyCodes/python codes/test_maker/limitss.csv",input_question_distribution)
status = -1
test_count = 0
Filename = "Export"+str(time.time()) 
fw = open(Filename,"w")
topic_question_distribution = {}
topic_floor = {}
topic_decimal = {}
decimal_bucket = {}
st_floor = {}
st_decimal = {}
dict_topic_st_count = {}
st_question_distribution = {}
dict_parent_child_count = {}
total_test=30

question_bank = get_question_bank("QB.csv")
dict_assessment_topic_count = get_child_count(question_bank,input_question_distribution.keys(),"assessment","topic")
for assessment in input_question_distribution :
    dict_topic_st_count[assessment] = get_child_count(question_bank,dict_assessment_topic_count[assessment].keys(),"topic","tag")
    total_questions = input_question_distribution[assessment]
    topic_floor[assessment],topic_decimal[assessment] = stats(dict_assessment_topic_count[assessment],total_questions)
    status,topic_floor[assessment],topic_decimal[assessment] = check_limits(topic_floor[assessment],topic_decimal[assessment],topic_limits,total_questions,dict_assessment_topic_count[assessment])
    if not status == 0:
        break
if status == 0:
    for i in range(total_test):
        fw.write(str("Test")+str(test_count)+"\n")
        test_count+=1
        for assessment in input_question_distribution:
            total_questions = input_question_distribution[assessment]
            topic_question_distribution[assessment] = brahmastra(topic_decimal[assessment],topic_floor[assessment],assessment,total_questions)
            for topic in topic_question_distribution[assessment]:
                st_floor[topic],st_decimal[topic] = stats(dict_topic_st_count[assessment][topic],topic_question_distribution[assessment][topic])
                st_question_distribution[topic] = brahmastra(st_decimal[topic],st_floor[topic],topic,topic_question_distribution[assessment][topic])
                status = export_question(fw,st_question_distribution[topic],"tag")
            if status==-1:
                break
        if(status ==-1):
            break
    print("Test Distributed. Test "+Filename +"\n total test created are "+str(test_count))
else:
    print("Test cannot be Distributed. Question less than lower limit")
fw.close()