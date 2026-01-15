import os
from collections import Counter
import matplotlib.pyplot as plt

folder_name = "training_number_data"
labels = []
x = []
y = []

#파일 목록 체크
if os.path.exists(folder_name):
    files = os.listdir(folder_name) #파일 가져오기
    for file in files:
        labels.append(file.split("_")[0])

    counts = Counter(labels)

    print(f"전체 오답 데이터 개수 : {len(files)}장\n")
    print("---숫자별 분포---")
    for i in range (10):
        num = str(i)
        print(f"숫자{num} : {counts.get(num,0)}장")
        x.append(num)
        y.append(counts.get(num,0))
    plt.bar(x, y)
    plt.show()
