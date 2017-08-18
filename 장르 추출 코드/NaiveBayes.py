# coding=cp949
'''
Created on 2017. 8. 15.

@author: DJ
'''
import csv
import numpy as np

from sklearn.naive_bayes import GaussianNB

# Ʈ���̴� �� ����
def loadTrainSet(filename, r, trainingSet=[], indexSet=[]):
    # csv ���� �ε�
    with open(filename, 'rb') as csvfile:
        lines = csv.reader(csvfile)
        # ����Ʈ �������� ��ȯ
        dataset = list(lines)
        # ����, ����, ���� ������, ���� �������� ���� ���ڷ� ��ȯ
        for x in range(len(dataset)):
            for y in range(r):
                # ù��° ���� �����̹Ƿ� int�� ����
                if(y == 0):
                    dataset[x][y] = int(dataset[x][y])
                # �������� float
                else:
                    dataset[x][y] = float(dataset[x][y])
                # �󺧸� �κ� ����
                if (y == r - 1):
                    indexSet.append(int(dataset[x][r]))
            # �󺧸� �κ��� ���� �����ؼ� �ʿ� �����Ƿ� ����
            dataset[x].pop(4)
            # �迭 ����
            trainingSet.append(dataset[x])
            
            
# �׽�Ʈ �� ����  (�̷��� Input)
def loadTestSet(filename, r, testSet=[]):
    # csv ���� �ε�
    with open(filename, 'rb') as csvfile:
        lines = csv.reader(csvfile)
        # ����Ʈ �������� ��ȯ
        dataset = list(lines)
        # ���� ��� ���� ��� ���� ���� �ؾ��ϱ⿡ �� ����
        x = 0
        for y in range(r):
            # ù��° ���� �����̹Ƿ� int�� ����
            if(y == 0):
                dataset[x][y] = int(dataset[x][y])
            # �������� float
            else:
                dataset[x][y] = float(dataset[x][y])
        # �迭 ����
        testSet.append(dataset[x])


# �帣�ڵ带 �帣������ ��ȯ
def GenreFinder(predict):
    # �ڵ� �б�
    code = predict[0]
    # �ڵ忡 �ش��ϴ� �ڵ�� ��ȯ, �������� ������ 'Unknown' ��ȯ
    return {116:'Ballad', 13:'Pop', 131:'Indie', 14:'R&B', 17:'Rock', 24:'Soundtrack',
            3:'Dance', 35:'Electronic', 7:'Hip-Hop', 8:'Jazz', 80:'Folk', 99:'Trot'}.get(code, 'Unknown')


# ���� �Լ�
def main():
    # ������ ���� �غ�
    trainingSet=[]
    testSet=[]
    indexSet=[]
    
    # csv �ε�
    loadTrainSet('Train01.csv', 4, trainingSet, indexSet)
    loadTestSet('Test01.csv', 4, testSet)
    
    # ������ �迭�� ����
    testSet = np.array(testSet)
    trainingSet = np.array(trainingSet)
    
    # SVM �Լ� �ε�
    GNB = GaussianNB()

    # �帣 ����
    predict = GNB.fit(trainingSet,indexSet).predict(testSet)
    genre = GenreFinder(predict)
    
    #�帣 ���
    print("<Naive Bayes>")
    print genre
    
main()