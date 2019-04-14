#Computer Communication Project1
#Kagan Ozgun 150130055
#23/10/2017

from socket import *
import threading
from random import randint
import time
import datetime
import hashlib
import os

class Login:                                                         #class for login data class store student id and password
    student=" "
    password=" "
    def __init__(self, a, b):
        self.student = a
        self.password = b
    def get_student(self):
        return self.__student
    def set_student(self, a):
        self.__student = a
    def get_password(self):
        return self.__password
    def set_password(self, a):
        self.__password = a

class Question:                # question class for taking quiz questions and answer
    question =  " "
    answer = " "
    def __init__(self, q, ans):
        self.question = q
        self.answer = ans
        
class Bonus:             #bonus class for quiz result
    student = " "
    point = 0
    time = 0
    def __init__(self, s, p, t):
        self.student = s
        self.point = p
        self.time = t
    
class ThreadedServer():

    def signUp(self, connectionSocket):                                     #signup method do the signup operations
        login_file=open("login.bin", "a+")                                   #open file for take record of registered student file is not human readable because include hash value
        ts = time.time()                                                                                                            #timestamps
        st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
        StrSt = str(st)
        connectionSocket.send(StrSt + "\nSign Up Page\n")                                               #get id from user
        connectionSocket.send("Enter your student number")
        student_id= connectionSocket.recv(1024)
        if student_id in login_file.read():                                                                            #check if this id is registered before
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
            StrSt = str(st)
            connectionSocket.send(StrSt+"\nThis student all ready registered contact with your teaching assistant.\nType exit for teminating program.")
        else:
            login_file.write(student_id)                                                         # if not registred before take password
            login_file.write(" - ")
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
            StrSt = str(st)
            connectionSocket.send(StrSt+"\nEnter password")
            password= connectionSocket.recv(1024)
            obj = hashlib.new('ripemd160')
            obj.update(password)
            ciphertext = str(obj.digest())                         #hash password for security
            login_file.write(ciphertext)                       # write password to file
            login_file.write("\n")          
            login_file.close()
            connectionSocket.send("Successfully registered.\n")

    def attendance(self,connectionSocket, addr, targetObj):             #attendance method
        attendance=open("attendance.txt", "a+")                             #create file for take attendance information human readable
        attLines = attendance.read()
        attLinesList = attLines.split("\n")
        attnumber = []                                                 
        for o in range(0, len(attLinesList)):
             tmp = attLinesList[o].split(" - ")
             attnumber.append(tmp[0])
        signed = False
        for k in range(0, len(attnumber)):                                        #check current user is signed attendance before
            if attnumber[k] == targetObj.student:
                signed = True
                break;
        if signed == False:                                                                 #if not signed 
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
            StrSt = str(st)
            connectionSocket.send(StrSt+"\nPlease type code below\n")               #send specific code for user to complate signed attendance
            key = str(randint(100000, 999999))
            connectionSocket.send(key)
            check = connectionSocket.recv(1024)
            if (check == key):                                                     #if key is correct save user student id , ip and port
                attendance.write(targetObj.student)                     #ip and port for checking if student signed by on own computer or another student computer
                attendance.write(" - ")
                strAddr = str(addr)
                attendance.write(strAddr)                                   # save attendance value in file
                attendance.write("\n")
                attendance.close()
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
                StrSt = str(st)
                connectionSocket.send(StrSt+"\nYou signed attendance\n")
                connectionSocket.send("Type exit for terminate the program\nType 3 for quiz\n")
            else:
                connectionSocket.send("Wrong attendance code\n")                       #this port for give error info to user
        else:
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
            StrSt = str(st)
            connectionSocket.send(StrSt+"\nyou allready signed attendance\nType exit for terminate the program or Type 3 for quiz")
        option= connectionSocket.recv(1024)
        return option
                        
    def quiz(self, connectionSocket, targetObj):
        flag = False
        quizResult = open("QuizResult.txt", "a+")                   #open a quiz result file
        results = quizResult.read()
        quizResult.close()
        Qresults = results.split("\n")
        for z in range(0, len(Qresults)):
            tmp = Qresults[z].split(" - ")
            if tmp[0] == targetObj.student:                         #check is student solve quiz before
                flag = True
        if flag == False:                                           #is not solve before start quiz
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
            StrSt = str(st)
            connectionSocket.send(StrSt+"\nYou have 30 minutes to finish quiz. During quiz do not press ctrl+z, or ctrl+c \nYou have one chance to enter quiz\nIf you ready press 0 to start quiz")
            start = connectionSocket.recv(1024)
            if start[0] == "0":                                         #take input for is user ready for quiz or not
                totalPoint = 0
                questionFile = open("Quizquestions.txt", "r")              #open question file for taking quiz questions
                allQuestions = questionFile.read()
                questionFile.close()
                QuestionsList = allQuestions.split("***///***")
                qObjList = []                                                                   #split data for taking question and answer separetaly
                for g in range(0, len(QuestionsList)):
                    Temp = QuestionsList[g].split("@@@@@")
                    question = Temp[0]
                    ans = Temp[1]
                    kgn = ans.split("\n")
                    qObj = Question(question,kgn[1])
                    qObjList.append(qObj)
                    ts = time.time()
                    st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
                FlagTime = False
                while(len(qObjList) > 0):
                    n = time.time()
                    clk = (n - ts)
                    if(clk > 1800):                                                    #check quiz time is over 30min or not if time is over break quiz
                        FlagTime = True
                        break;
                    at = datetime.datetime.fromtimestamp(clk).strftime('%M:%S')
                    StrClk = str(at)
                    random = randint(0, len(qObjList)-1)                  #select quiz question randomly
                    connectionSocket.send(qObjList[random].question+"\nTime :"+StrClk+"\n")
                    answer = connectionSocket.recv(1024)
                    answer = answer.lower()
                    if answer == qObjList[random].answer:                           #check answer is true if true give 10 point
                        totalPoint = totalPoint + 10
                    del qObjList[random]
                if(FlagTime == True):
                    connectionSocket.send("Time out\n")
                quizResult = open("QuizResult.txt", "a+")      #print result of the quiz to file
                quizResult.write(targetObj.student)
                quizResult.write(" - ")
                result = str(totalPoint)
                quizResult.write(result)
                quizResult.write(" - ")
                Sclk = str(clk)
                quizResult.write(Sclk)
                quizResult.write("\n")
                quizResult.close()
                self.bonus()                                    #start bonus method for give bonus points
        else:
            connectionSocket.send("You all ready solve the quiz\n")
        
        
        
    
    def signIn(self, connectionSocket, addr):                      
        login_file=open("login.bin", "r")
        login_file.seek(0)
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
        StrSt = str(st)
        connectionSocket.send(StrSt+"\nSign In Page\n")
        connectionSocket.send("Enter your student number")
        student_id= connectionSocket.recv(1024)
        student_list = []
        lines = login_file.read()
        linesList = lines.split("\n")
        for j in range(0, len(linesList)-1):                     #find user in login file 
            oneLine = linesList[j]
            data = oneLine.split(" - ")
            StuObj = Login(data[0], data[1])
            student_list.append(StuObj)
        login_file.close()
        signUpF = False
        for i in range(0, len(student_list)):
            if student_list[i].student == student_id:                        #if user is registered
                signUpF = True
                targetObj = student_list[i]
                ts = time.time()
                st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
                StrSt = str(st)
                connectionSocket.send(StrSt+"\nEnter password")                     #take password
                password= connectionSocket.recv(1024)
                obj2 = hashlib.new('ripemd160')                                  #hash password to compare in password in db
                obj2.update(password)
                ciphertext2 = str(obj2.digest())
                if targetObj.password == ciphertext2:                                      #if password true signin user
                    ts = time.time()
                    st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
                    StrSt = str(st)
                    connectionSocket.send(StrSt+"\nlogin success\n")
                    connectionSocket.send("Press 2 for sign attandence\nPress 3 for quiz") #options for user attendance or quiz
                    option= connectionSocket.recv(1024)
                    if option[0] == "2":                                      #if select attendance call attendance method
                        option = self.attendance(connectionSocket, addr, targetObj)
                    if(option[0] =="3" ):                                 #if select  quiz call quiz method
                        self.quiz(connectionSocket, targetObj)
                       
                else:
                    connectionSocket.send("Wrong Password\n")              #some error messages for client
                    break
        if signUpF == False:
            connectionSocket.send("You are not sign up please sign up\n")
           

    def bonus(self):
        quizRes = open("QuizResult.txt", "r")                  #open quizresult for collect results
        quizRes.seek(0)
        result_list = []
        lines = quizRes.read()
        resultList = lines.split("\n")
        for j in range(0, len(resultList)-1):
            oneLine = resultList[j]
            data = oneLine.split(" - ")
            BonusObj = Bonus(data[0], int(data[1]), float(data[2]))               #take data to object list
            result_list.append(BonusObj)
        quizRes.close()
        BonusRes = open("QuizResultWithBonus.txt", "w+")                        #open bonus result for save point with bonus
        SortedList = sorted(result_list,  key=lambda bonus: bonus.time)
        for k in range(0, len(SortedList)):                                      #if student in %25 of class give 20 point bonus
            if k < len(SortedList)/4:
                SortedList[k].point = SortedList[k].point +20
            elif k < len(SortedList)/2:
                SortedList[k].point = SortedList[k].point +10               #if student in %25-%50 give 10 point 
            elif k < (len(SortedList)*3)/4:
                SortedList[k].point = SortedList[k].point +5                        #if student between %50-%75 give 5 point bonus
        for kgn in range(0, len(SortedList)):
            BonusRes.write(SortedList[kgn].student+" - "+str(SortedList[kgn].point)+" - "+str(SortedList[kgn].time)+"\n")                #write points with bonus to file
        BonusRes.close()
        

    def main(self, connectionSocket, addr):
        while True:
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S   %d-%m-%Y')
            StrSt = str(st)
            connectionSocket.send(StrSt + "\nWelcome to system\nLogin Page\n1 for sign up\n0 for sign in\nType exit for terminate\n")            #welcome message and timestamp
            message= connectionSocket.recv(1024)                                                                                                                            #get operations
            if message[0]=="1":
                self.signUp(connectionSocket)                                #and call signin or signup
            elif message[0]=="0":
                self.signIn(connectionSocket, addr)
            elif message=="exit":
                connectionSocket.close()

    def __init__(self,serverPort):
        
        try:                                                                                                                            #create Tcp connecion
            serverSocket=socket(AF_INET,SOCK_STREAM)

        except:
    
            print "Socket cannot be created!!!"
            exit(1)
            
        print "Socket is created..."

        try:
            serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        except:
    
            print "Socket cannot be used!!!"
            exit(1)

        print "Socket is being used..."

        try:
            serverSocket.bind(('',serverPort))
        except:
        
            print "Binding cannot de done!!!"
            exit(1)

        print "Binding is done..."

        try:
            serverSocket.listen(45)
        except:
    
            print "Server cannot listen!!!"
            exit(1)

        print "The server is ready to receive"                            #if server ready to use

        while True:
            connectionSocket,addr=serverSocket.accept()                #accept client connection
            threading.Thread(target = self.main,args = (connectionSocket, addr)).start()   #call main and start threads

if __name__=="__main__":
    serverPort=12000
    ThreadedServer(serverPort)
	
