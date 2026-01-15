import cv2
import numpy as np
from tensorflow import keras # 학습모델 불러오기
from PIL import ImageFont, ImageDraw, Image #한글 글자 출력용
import time #시간 제어용
import os #폴더 생성용

folder_name = "training_number_data"
if not os.path.exists(folder_name): #exists는 폴더나 파일이 있는지 체크하는 함수
    os.mkdir(folder_name)

def draw_korean_text(img, text, font_size, color, y_offset=0):
    # OpenCV 이미지(Numpy)를 PIL 이미지로 변환
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 한글 폰트 설정 (윈도우 기본 맑은 고딕)
    font = ImageFont.truetype("malgun.ttf", font_size)
    # 그리기 객체 생성 및 글씨 쓰기
    draw = ImageDraw.Draw(img_pil)

    # 글자 영역 계산 (left, top, right, botton)
    text_box = draw.textbbox((0,0), text, font=font)
    text_w = text_box[2] - text_box[0]
    text_h = text_box[3] - text_box[1]
    h, w = img.shape[:2] #이미지 중앙좌표

    # 중앙 정렬 좌표 계산
    x = (w - text_w) // 2
    y = (h - text_h) // 2 + y_offset

    draw.text((x,y), text, font=font, fill=color)
    # PIL이미지를 다시 OpenCV 이미지(Numpy)로 되돌리기
    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("웹캡은 열 수 없습니다.")
    exit()

#학습시킨 모델 불러오기
load_model = keras.models.load_model("my_second_DNN_model.keras")

IMG_PASSWORD = ['3','3','2','1']
captured_numbers = []

# 변수 초기화
result = "?" #현재 입력된 숫자
status_msg = "카메라에 숫자를 보여주세요." # 안내문구
status_list_msg = "" # 숫자목록
success_img = cv2.imread("mask_smile.bmp") # 성공 이미지
success_img = cv2.resize(success_img, (300, 300))
success_start_time = 0 # 성공 유지 타이머
isSuccessPassword = False #패스워드 성공 유무
isWaitingAnswer = False # 정답 수정 유무
isWaitingConfirm = False # Y/N 최종 확인 유무
input_num = "" #임시 저장 숫자
ans_num = "" #정답 숫자

while True:
    ret, frame = cap.read() # 리턴값과 프레임
    if not ret:
        print("프레임을 가져올 수 없습니다.")
        break
    flip_frame = cv2.flip(frame,1) # y축을 기준으로 뒤집기(거울반전)
    #중앙을 읽을 프레임 / 높이와 폭만 보면 되서 색은 안쓴다는 의미로 _
    height, width, _ = frame.shape
    center_x, center_y = width //2, height//2 # x와 y의 중심점
    # roi 영역 만들기 (정중앙 빨간 사각형)
    roi = flip_frame[center_y - 150:center_y + 150, center_x - 150:center_x + 150]
    cv2.rectangle(flip_frame, (center_x - 150, center_y - 150), (center_x + 150, center_y + 150), (0, 0, 255), 2)


    #화면 캡처를 위한 키값 받기
    key = cv2.waitKey(1) & 0xFF
    if key in [ord('c'), ord('C')]:
        status_msg = "인식 중... 잠시만 기다리세요"
        # 인식을 시작하기 전에 현재 프레임을 화면에 강제로 보여줌
        temp_frame = draw_korean_text(flip_frame, status_msg, 25, (255,255,255), -220)
        cv2.imshow("Webcam", temp_frame)
        cv2.waitKey(1) # 글씨를 보여줄 수 있게 강제 딜레이

        gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) # 이진화를 하기 위함

        gray_image = np.flip(gray_image, 1) # 반전 시켜서 넣어줌
        # cv2.imwrite("gray_image.png", gray_image) # 사진 저장
        cv2.imshow("gray_image", gray_image)
        gaussian_blur = cv2.GaussianBlur(gray_image, (5, 5), 3) #가우시안 블러(영상의 노이즈 제거)

        #2진화
        _, otsu_thread = cv2.threshold(gaussian_blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        #### Morph
        kernel = np.ones((5, 5), np.uint8)
        # 글자를 두껍게 함 / 침식 방법으로 확장시킴
        erosion = cv2.erode(otsu_thread, kernel, iterations=3)

        # 이미지 자르기
        img = erosion.copy()
        h, w = img.shape[:2]
        crop_size = 240
        cx, cy = w//2, h//2

        # 좌우 중심 맞추기
        half = crop_size // 2
        x1, x2 = cx - half, cx + half
        y1, y2 = cy - half, cy + half

        # 경계면 설정
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)

        cropped_img = img[y1:y2, x1:x2]

        # 이미지 반전
        reversed_img = cv2.bitwise_not(cropped_img)
        cv2.imshow("reversed_img", reversed_img) #체크용

        # 이미지 사이즈 조절
        resize_img = cv2.resize(reversed_img, (28, 28))
        # 가장자리 검게 색칠
        resize_img[0:3, :] = 0   # 상단
        resize_img[-3:, :] = 0   # 하단
        resize_img[:, 0:3] = 0   # 좌측
        resize_img[:, -3:] = 0   # 우측
        cv2.imshow("resize_img", resize_img)  #체크용

        # 이미지 저장
        cv2.imwrite("IMAGE_FOR_TEST.png", resize_img)

        #이미지 인식
        test_img = resize_img.copy()
        # 모델이 원하는 (1, 28, 28)모양으로 변경
        test_img = test_img.reshape(1, 28, 28)
        # 인식(Predict)
        prediction = load_model.predict(test_img)
        result = np.argmax(prediction) # 가장 확률 높은 숫자 선택

        captured_numbers.append(str(result)) #비밀번호 문자열로 추가
        status_list_msg = ", ".join(captured_numbers)

        if len(captured_numbers) >= 4:
            if captured_numbers[-4:] == IMG_PASSWORD:
                print("비밀번호 성공")
                isSuccessPassword = True
                success_start_time = time.time() #성공시간 기록

                status_msg = "비밀번호 인식 성공!"
                status_list_msg=""
                captured_numbers = []
            else:
                print("비밀번호 실패")
                status_msg = "비밀번호 실패! 다시 시도해주세요."
                status_list_msg=""
                captured_numbers = []
        else:
            status_msg = "비밀번호 입력중"
        print(f"인식된 숫자는 [ {result} ] 입니다!")

    elif key in [ord('z'), ord('Z')]:# 단순 실수
        if len(captured_numbers) > 0 : #리스트가 존재할 때
            captured_numbers.pop() # 마지막 인식값 제거
            result = "?"
            status_list_msg = ", ".join(captured_numbers)
            status_msg = "마지막 숫자를 삭제했습니다."
        else:
            status_msg = "인식된 숫자가 존재하지 않습니다."

    elif key in [ord('x'), ord('X')]: # 인식 학습
        if len(captured_numbers) > 0 : #리스트가 존재할 때
            wrong_num = captured_numbers[-1]
            status_msg = f"인식오류({wrong_num})! 키보드(0-9)로 정답을 알려주세요."
            status_list_msg = ", ".join(captured_numbers)
            isWaitingAnswer = True
        else:
            status_msg = "인식된 숫자가 존재하지 않습니다."

    elif ord ('0') <= key <= ord('9') and isWaitingAnswer:
        input_num = chr(key) # 키 입력받기
        status_msg = f"입력하신 {input_num}이(가) 맞습니까?(Y/N)"
        isWaitingAnswer = False
        isWaitingConfirm = True

    elif isWaitingConfirm:
        if key in [ord('y'), ord('Y')]:
            captured_numbers.pop() # 마지막 인식값 제거
            captured_numbers.append(input_num) #리스트에 넣기
            result = input_num
            if 'resize_img' in locals(): # 파일이 존재하는지 체크
                cv2.imwrite(f"{folder_name}/{input_num}_{int(time.time())}.png", resize_img) #파일저장
            status_msg = "수정이 완료되었습니다."
            status_list_msg = ", ".join(captured_numbers)
            isWaitingConfirm = False
        elif key in [ord('n'), ord('N')]:
            status_msg = "취소되었습니다."
            isWaitingConfirm = False

    elif key == 27:
        break

    if isSuccessPassword: #비밀번호 성공하면
        if time.time() - success_start_time < 5: #성공 순간부터 5초
            flip_frame[center_y - 150:center_y + 150, center_x - 150:center_x + 150] = success_img
        else:
            isSuccessPassword = False

    # 글자먼저, 이후 전체 모양을 화면 출력
    flip_frame = draw_korean_text(flip_frame, status_msg, 25, (255,255,255), -220)
    flip_frame = draw_korean_text(flip_frame,
                                  f"현재 입력: {result} / 인식 c / 인식정정 x / 삭제 z",
                                  25, (255,255,255), -180)
    flip_frame = draw_korean_text(flip_frame, status_list_msg, 25, (255,255,255), 170)

    cv2.imshow("Webcam", flip_frame)


cap.release()
cv2.destroyAllWindows()
