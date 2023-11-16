import cv2
import mediapipe as mp 
import time  

class handDetector():  #class is created 

    def __init__(self, mode = False, MaxHands = 3, complexity=1, detectioncon= 0.5 ,trackcon=0.5):  #here class is defined with methods and self is used for refering to the instance of class when used by objects 
        self.mode = mode                             #all of these are objects of the class
        self.MaxHands = MaxHands                        #all of these are objects of the class
        self.detectioncon= detectioncon         #all of these are objects of the class
        self.trackcon= trackcon
        self.complexity = complexity 


        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.MaxHands, self.complexity, self.detectioncon,self.trackcon)  # these are instances of mediapipe used in class 
        self.mpDraw = mp.solutions.drawing_utils 


    def findHands(self, img, draw= True):                 # this find the hands and connect the landmarks 
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handlmks in self.results.multi_hand_landmarks:
                if draw:
                     self.mpDraw.draw_landmarks(img, handlmks,self.mpHands.HAND_CONNECTIONS)
                    

        return img # return img to the main funcion 


    def findPos(self, img, handNum = 0, draw = True):   # this finds the position and draws circle around the landmarks 
        lmList = []

        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNum]
            for id, lm in enumerate(myHand.landmark):
                h,w,c = img.shape
                cx ,cy = int(lm.x*w), int(lm.y*h)
                lmList.append([id,cx,cy])
                if draw:
                    cv2.circle(img,(cx,cy), 10, (255,0,255), cv2.FILLED)
        return lmList    #return the landmarks to the main 


def main():
    cap = cv2.VideoCapture(0)
    pTime = 0 
    cTime = 0 
    detector = handDetector()

    while True :
        success, img = cap.read()
        img = detector.findHands(img)
        lmList =  detector.findPos(img)
        if len(lmList) != 0:
            print(lmList[4])  # chosse to take location of specific landmarks 

        cTime = time.time()
        fps = (1/(cTime-pTime))   
        pTime = cTime 

        cv2.putText(img, str(int(fps)), (10,70), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 0,255), 3) #this displays fps @ img as str which has int values at position 10,70 aat some font with scale 3 color purple and thickness 3 

        cv2.imshow("webcam", img)
        
        key = cv2.waitKey(1)
        if key == ord('q'):
            break 

if __name__ == "__main__":
    main()
