import csv
import math
import time

def get_limits(path):
    excel = open(path,"r")
    dict_topic_limits ={}
    lines=excel.readlines()
    for line in lines:
        columns = line.split(',')
        dict_topic_limits[columns[1].strip('[""""]')]={"assessment":columns[0].strip(),"Lower_limit":int(columns[2].strip()),"Upper_limit":int(columns[3].strip())}
    return dict_topic_limits

def check_limits(topic_floor,topic_decimal,dict_topic_limits):
    print(dict_topic_limits)
    limit_fails=[]
    for key in topic_floor:
        if (topic_floor[key] < dict_topic_limits[key]["Lower_limit"]):
            limit_fails.append(key)
            print("TEST CANNOT BE CREATED because following topics have questions less than lower limit \n"+str(limit_fails))
        elif(topic_floor[key]>dict_topic_limits[key]["Upper_limit"]):
                print("running")
                topic_floor[key]=dict_topic_limits[key]["Upper_limit"]
                topic_decimal[key]=0.00
    return topic_floor,topic_decimal

def get_question_bank(path):
    excel = open(path,"r")
    # reader = csv.reader(excel, delimiter=',')
    array_question_bank = []
    lines = excel.readlines()
    for line in lines:     
        columns = line.split(',')
        array_question_bank.append({"QID": columns[0].strip(),"assessment":columns[1].strip(),"topic":columns[2].strip('[""""]'),"tag":columns[3].strip()})        
    return array_question_bank

def get_topic_count(array_question_bank,input_question_distribution):    
    dict_assessment_topic_count = {}
    for assessment in input_question_distribution.keys():
        dict_topic_count = {}
        for question in array_question_bank:    
                topic = question["topic"]
                qb_assesment = question["assessment"]
                if(qb_assesment == assessment):
                    if topic in dict_topic_count :
                        dict_topic_count[topic] = dict_topic_count[topic] + 1   
                    else:
                        dict_topic_count[topic] = 1
        dict_assessment_topic_count[assessment] = dict_topic_count
    return dict_assessment_topic_count
    
# extract question, calc ratio, total ques
def stats(dict_topic_count,total_questions):
    topic_decimal = {}
    topic_floor = dict_topic_count.copy()
    total_topic_question = 0
    for i in dict_topic_count: 
        total_topic_question = total_topic_question + dict_topic_count[i]
    ratio = 0.00
    for i in dict_topic_count:
        ratio = dict_topic_count[i]*total_questions/total_topic_question
        decimal_value = float(str(ratio-int(ratio))[1:])
        floor = math.floor(ratio)
        topic_floor[i] = floor
        topic_decimal[i] = decimal_value
    return topic_floor,topic_decimal

def print_dict(dict):
    for i in dict:
        print(i,dict[i])
    print("\n")

def update_decimal_bucket(topic_decimal,assessment):
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
    
    for i in range(0,remaining_question):
        topic = max(decimal_bucket[assessment], key=decimal_bucket[assessment].get)
        topic_question_distribution[topic] = topic_question_distribution[topic] + 1 
        decimal_bucket[assessment][topic] = 0 if topic_decimal[topic] - 1 < 0 else topic_decimal[topic] - 1 
        count+=1

    return topic_question_distribution
def export_question(fw,topic_question_distribution):
    for topic in topic_question_distribution:
        question_count = topic_question_distribution[topic] 
        for i in range(0,question_count):
            question_found = False
            for question in question_bank:    
                if(question["topic"]==topic):
                    question_found = True
                    fw.write(str(question["QID"])+","+str(topic)+"\n")
                    print(str(question["QID"])+","+str(topic)+"\n")
                    question_bank.remove(question)
                    topic_question_distribution[topic] = topic_question_distribution[topic] - 1    
                    break       
            if(question_found==False):
                return -1
    return 0        
                
assessment_areas = ["Logical Reasoning/ Data Interpretation","Verbal Ability","Quantitative Aptitude"]
# question_bank = get_question_bank("C:/Users/hp/Desktop/MyCodes/python codes/test_maker/QB.csv")
# topic_limits=get_limits("C:/Users/hp/Desktop/MyCodes/python codes/test_maker/limits.csv")

# topic_limits = get_limits
input_question_distribution = { assessment_areas[0]: 15, assessment_areas[1] : 30,assessment_areas[2]: 20}
status = -1
test_count = 0
fw = open("Export"+str(time.time()),"w")
topic_question_distribution = {}
topic_floor = {}
topic_decimal = {}
decimal_bucket = {}
question_bank = get_question_bank("QB.csv")
dict_assessment_topic_count = get_topic_count(question_bank,input_question_distribution)

for assessment in input_question_distribution :
    decimal_bucket[assessment] = {}
    total_questions = input_question_distribution[assessment]
    topic_floor[assessment],topic_decimal[assessment] = stats(dict_assessment_topic_count[assessment],total_questions)
    
while(1==1):
    fw.write(str("Test")+str(test_count)+"\n")
    test_count+=1
    for assessment in input_question_distribution:
        total_questions = input_question_distribution[assessment]
        topic_question_distribution[assessment] = brahmastra(topic_decimal[assessment],topic_floor[assessment],assessment,total_questions)
        status = export_question(fw,topic_question_distribution[assessment])
        # print_dict(decimal_bucket)
        # print_dict(topic_question_distribution)
        if status==-1:
            break
    if(status ==-1):
        print("Test Distributed. Test Excel")
        break
fw.close()