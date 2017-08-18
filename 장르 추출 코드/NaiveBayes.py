# coding=cp949
'''
Created on 2017. 8. 15.

@author: DJ
'''
import csv
import numpy as np

from sklearn.naive_bayes import GaussianNB

# 트레이닝 셋 생성
def loadTrainSet(filename, r, trainingSet=[], indexSet=[]):
    # csv 파일 로드
    with open(filename, 'rb') as csvfile:
        lines = csv.reader(csvfile)
        # 리스트 형식으로 변환
        dataset = list(lines)
        # 나이, 성별, 긍정 감정차, 부정 감정차의 값을 숫자로 변환
        for x in range(len(dataset)):
            for y in range(r):
                # 첫번째 행은 나이이므로 int로 설정
                if(y == 0):
                    dataset[x][y] = int(dataset[x][y])
                # 나머지는 float
                else:
                    dataset[x][y] = float(dataset[x][y])
                # 라벨링 부분 추출
                if (y == r - 1):
                    indexSet.append(int(dataset[x][r]))
            # 라벨링 부분은 따로 추출해서 필요 없으므로 삭제
            dataset[x].pop(4)
            # 배열 삽입
            trainingSet.append(dataset[x])
            
            
# 테스트 셋 생성  (미래의 Input)
def loadTestSet(filename, r, testSet=[]):
    # csv 파일 로드
    with open(filename, 'rb') as csvfile:
        lines = csv.reader(csvfile)
        # 리스트 형식으로 변환
        dataset = list(lines)
        # 단일 대상에 대한 결과 값을 추출 해야하기에 열 고정
        x = 0
        for y in range(r):
            # 첫번째 행은 나이이므로 int로 설정
            if(y == 0):
                dataset[x][y] = int(dataset[x][y])
            # 나머지는 float
            else:
                dataset[x][y] = float(dataset[x][y])
        # 배열 삽입
        testSet.append(dataset[x])


# 장르코드를 장르명으로 변환
def GenreFinder(predict):
    # 코드 읽기
    code = predict[0]
    # 코드에 해당하는 코드명 반환, 존재하지 않으면 'Unknown' 반환
    return {116:'Ballad', 13:'Pop', 131:'Indie', 14:'R&B', 17:'Rock', 24:'Soundtrack',
            3:'Dance', 35:'Electronic', 7:'Hip-Hop', 8:'Jazz', 80:'Folk', 99:'Trot'}.get(code, 'Unknown')


# 메인 함수
def main():
    # 데이터 생성 준비
    trainingSet=[]
    testSet=[]
    indexSet=[]
    
    # csv 로드
    loadTrainSet('Train01.csv', 4, trainingSet, indexSet)
    loadTestSet('Test01.csv', 4, testSet)
    
    # 다차원 배열로 변경
    testSet = np.array(testSet)
    trainingSet = np.array(trainingSet)
    
    # SVM 함수 로드
    GNB = GaussianNB()

    # 장르 예측
    predict = GNB.fit(trainingSet,indexSet).predict(testSet)
    genre = GenreFinder(predict)
    
    #장르 출력
    print("<Naive Bayes>")
    print genre
    
main()