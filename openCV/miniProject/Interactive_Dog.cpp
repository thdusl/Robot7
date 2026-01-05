#include <windows.h>
#include <mmsystem.h>
#pragma comment(lib, "winmm.lib")

#include "opencv2/opencv.hpp"
#include <iostream>
#include <ctime>

//상태 관리 구조체
struct Square {
	cv::Point position; //사각형의 중심 좌표(x,y)
	int squareLength;
	bool active; //화면에 표시되는지 확인
	Square() {
		//기본값으로 초기화
		this->position = cv::Point();
		this->squareLength = 40;
		this->active = true; //초기값 활성화
	}
};

//축 변환 리셋
static cv::Mat resetAffineTransform(cv::Mat dst)
{
	cv::Point2f center(dst.cols / 2.0f, dst.rows / 2.0f);
	cv::Mat M = cv::getRotationMatrix2D(center, 0, 1.0); //뒤틀린 축 원래대로 변환
	cv::warpAffine(dst, dst, M, dst.size(), cv::INTER_LINEAR, cv::BORDER_CONSTANT);
	return dst;
}
//원형 마스크
static cv::Mat getCircleMask(cv::Size si)
{
	cv::Mat mask = cv::Mat::zeros(si, CV_8UC1);;
	int radius = cvRound(si.width / 2.3); //사각을 더 둥그렇게 만들기 위함

	cv::circle(mask, cv::Point(si.width / 2, si.height/ 2), radius, cv::Scalar(255), -1, cv::LINE_AA); //흰색 원 생성
	return mask;
}

//축이동
static cv::Mat getEventAffine(cv::Mat src)
{
	cv::Point2f srcPts[3], dstPts[3];
	srcPts[0] = cv::Point2f(0, 0);
	srcPts[1] = cv::Point2f(src.cols -1 , 0);
	srcPts[2] = cv::Point2f(src.cols - 1, src.rows -1);

	//랜덤 변수
	int pointRange = 10;

	dstPts[0] = cv::Point2f(rand() % pointRange, rand() %pointRange);
	dstPts[1] = cv::Point2f(src.cols -1 - (rand() % pointRange), rand() % pointRange);
	dstPts[2] = cv::Point2f(src.cols -1 - (rand() % pointRange), src.rows - 1-(rand() % pointRange));

	return cv::getAffineTransform(srcPts, dstPts); //float 타입만 받는 getAffineTransform 함수
}


//이미지 무작위 좌표 생성 함수
static cv::Point getRandomPosition(int width, int height, int squareLength)
{
	if (squareLength >= width || squareLength >= height) {
		return cv::Point(width / 2, height / 2);
	}
	//공이 잘리지 않게 랜덤 범위 설정
	int x = rand() % (width - squareLength) + squareLength / 2;
	int y = rand() % (height - squareLength) + squareLength / 2;
	//전달
	return cv::Point(x, y);
}
//이벤트 랜덤 실행
static cv::Mat getRandomEvent(cv::Mat src)
{
	int EventNumber = rand() % 8;

	//체크용 변수들
	static bool isCircleMode = false; //원형 체크
	static bool isFlipMode = false; //이미지 반전 체크
	static bool isAffineMode = false; //축이동 체크
	static float resizeLevel = 1.0f; //크기변환 배율
	static int redColorLevel = 0; //색깔변환
	static bool isColorInvertMode = false; //색반전 체크
	static int morphLevel = 0; //모폴로지 0:일반, 1:팽창, 2:침식

	cv::Mat next_dst = src.clone();

	switch (EventNumber)
	{
	case 1: //원으로 변경
	{
		isAffineMode = false; //축이동 모드 해제
		isCircleMode = true;
		break;
	}
	case 2: //상하반전
	{
		isFlipMode = !isFlipMode;
		break;
	}
	case 3: //축이동
	{
		isCircleMode = false; //원 모드 해제
		isAffineMode = true;
		break;
	}
	case 4: //크기변환
	{
		++resizeLevel;
		if (resizeLevel > 6.0f) resizeLevel = 1;
		break;
	}
	case 5: //색깔변환
	{
		++redColorLevel;
		if (redColorLevel > 3) redColorLevel = 0;
		if (redColorLevel == 3) {
			PlaySound(TEXT("dog_barking.wav"), NULL, SND_FILENAME | SND_ASYNC);
		}
		break;
	}
	case 6: //색반전 및 음향효과
	{
		isColorInvertMode = !isColorInvertMode;
		if (isColorInvertMode) {
			PlaySound(TEXT("dog_barking.wav"), NULL, SND_FILENAME | SND_ASYNC);
		}
		break;
	}
	case 7: //모폴로지연산
	{
		++morphLevel;
		if (morphLevel > 2) morphLevel = 0;
		if (morphLevel == 2) {
			PlaySound(TEXT("dog_barking.wav"), NULL, SND_FILENAME | SND_ASYNC);
		}
		break;
	}
	default:
	{
		isCircleMode = false;
		isFlipMode = false;
		resizeLevel = 1.0f;
		isColorInvertMode = false;
		break;
	}
	}//end of switch
	
	//최종 적용 (순서중요: 색상-> 형태->기하변환)
	if (isColorInvertMode) { //색반전
		next_dst = ~next_dst;
	}
	if (redColorLevel > 0) { //빨간필터
		int redNum = 25 + (redColorLevel * 10);
		next_dst += cv::Scalar(0, 0, redNum);
	}
	if (morphLevel == 1) { //모폴로지
		cv::dilate(next_dst, next_dst, cv::Mat(), cv::Point(-1, -1), 2);
	}
	else if (morphLevel == 2) { 
		cv::erode(next_dst, next_dst, cv::Mat(), cv::Point(-1, -1), 2);
	}
	if (isFlipMode) //상하대칭
	{
		cv::flip(next_dst, next_dst, 0);
	}
	if (resizeLevel > 1.0f) {  //크기변환
		cv::resize(next_dst, next_dst, cv::Size(), resizeLevel, resizeLevel, cv::INTER_LINEAR);
	}
	if (isAffineMode) { //축이동
		cv::warpAffine(next_dst, next_dst, getEventAffine(next_dst), next_dst.size(),
			cv::INTER_CUBIC, cv::BORDER_CONSTANT, cv::Scalar(0));
	}

	//최종 원형 깎기
	if (isCircleMode) {
		next_dst = resetAffineTransform(next_dst);
		cv::Mat clean = cv::Mat::zeros(next_dst.size(), next_dst.type());
		next_dst.copyTo(clean, getCircleMask(next_dst.size()));
		next_dst = clean;
	}

	return next_dst;
}

//카메라 및 실제 이벤트용 함수
void miniProject() CV_NOEXCEPT
{
	srand((unsigned int)time(0));
	cv::VideoCapture cap(0);
	if (!cap.isOpened()) {
		std::cerr << "웹캠이 없습니다.\n";
		return;
	}
	
	int width = cvRound(cap.get(cv::CAP_PROP_FRAME_WIDTH));
	int height = cvRound(cap.get(cv::CAP_PROP_FRAME_HEIGHT));
	double fps = cap.get(cv::CAP_PROP_FPS);
	//코덱 선택
	int fourcc = cv::VideoWriter::fourcc('D', 'I', 'V', 'X');
	int delay = cvRound(1000 / fps);
	//저장용 함수
	cv::VideoWriter outputVideo("test01.avi", fourcc, fps, cv::Size(width, height));

	cv::Mat prev_gray_frame; //바로 직전 프레임 저장 변수
	Square squareImg;

	int count = 0; //횟수
	cv::Mat img = cv::imread("dog2.jpg"); //이미지불러오기
	cv::Mat src_img; //자른 이미지
	cv::Mat dst_img; //복사용 이미지
	if (!img.empty()) {
		cv::resize(img, img, cv::Size(50, 60));
		int srcW = std::min(squareImg.squareLength, img.cols);
		int srcH = std::min(squareImg.squareLength, img.rows);
		src_img = img(cv::Rect(5, 5, srcW, srcH)).clone(); //깊은 복사
		dst_img = src_img.clone();
		squareImg.position = getRandomPosition(width, height, dst_img.cols);
	}

	while (true) {
		cv::Mat frame, gray_frame, diff, thresh;
		cap >> frame;
		if (frame.empty()) break;

		cv::flip(frame, frame, 1); //좌우 반전

		cv::cvtColor(frame, gray_frame, cv::COLOR_BGR2GRAY); //전처리, 색상제거
		cv::GaussianBlur(gray_frame, gray_frame, cv::Size(15, 15), 0); //노이즈 제거

		//첫 실행 시 비교할 것이 없으므로 저장 후 다음 루프로 이동
		if (prev_gray_frame.empty()) {
			gray_frame.copyTo(prev_gray_frame);
			continue;
		}

		//움직임 감지
		cv::absdiff(prev_gray_frame, gray_frame, diff); //프레임 비교 (차이 구하기)
		cv::threshold(diff, thresh, 25.0, 255.0, cv::THRESH_BINARY); //차이 25 이상이면 흰색으로 만들어 움직임 영역 확대

		if (squareImg.active) {
			//원본 이미지 길이
			int srcW = src_img.cols;
			//실제 출력되는 이미지 길이 (캠보단 작게)
			int dstW = std::min(dst_img.cols, width);
			int dstH = std::min(dst_img.rows, height);

			int x = cv::max(0, cv::min(squareImg.position.x - dstW / 2, width - dstW));
			int y = cv::max(0, cv::min(squareImg.position.y - dstH / 2, height - dstH));
			cv::Rect gameRect(x, y, dstW, dstH);

			cv::Mat roi = thresh(gameRect); //전체 화면에서 이미지 사각형 영역 떼어냄
			int movePixels = cv::countNonZero(roi); //roi 안에서 흰색픽셀(움직임)의 개수를 카운트

			//이미지 전체 면적 계산
			int area = dstW * dstH;
			//이미지 면적에 따라 움직임 판단 기준 다르게 설정
			float touchThreshold = 0.15f;
			if (dstW >= srcW * 4) {
				touchThreshold = 0.05f;
			}
			else if (dstW >= srcW * 2) {
				touchThreshold = 0.10f;
			}

			//움직임이 touchThreshold만큼 발생하면 터치로 판단
			if (movePixels > area * touchThreshold) {
				std::cerr << "터치 " << ++count << "\r\n";
				//랜덤효과 적용
				dst_img = getRandomEvent(src_img); 
				//카운트 점수 올라가고, 위치 이동
				int nextDstW = dst_img.cols;
				squareImg.position = getRandomPosition(width, height, nextDstW);
				
				//새로 업데이트
				dstW = dst_img.cols;
				dstH = dst_img.rows;

				//gameRect 새로고침
				x = cv::max(0, cv::min(squareImg.position.x - dstW / 2, width - dstW));
				y = cv::max(0, cv::min(squareImg.position.y - dstH / 2, height - dstH));
				gameRect = cv::Rect(x, y, dstW, dstH);
			}


			//캡에 이미지 그리기
			if (!dst_img.empty()) {
				//공백 제거용 마스크 생성
				cv::Mat mask;
				cv::cvtColor(dst_img, mask, cv::COLOR_BGR2GRAY);
				cv::threshold(mask, mask, 1, 255, cv::THRESH_BINARY); //기준점을 정해서 이진법(흑백 구분)

				dst_img.copyTo(frame(gameRect), mask);
			}
		}
		//출력 - 글자
		cv::putText(frame, "count: " + std::to_string(count),
			cv::Point(20, 30), cv::FONT_HERSHEY_PLAIN, 2,
			cv::Scalar(255, 255, 255), 2);

		cv::imshow("Game", frame);
		gray_frame.copyTo(prev_gray_frame); //현재 화면을 이전 화면으로 업데이트하여 다음 프레임과 비교 준비

		//최종 frame을 동영상으로 저장
		if (outputVideo.isOpened()) outputVideo.write(frame);
		if (cv::waitKey(10) == 27) break; //esc누르면 게임 종료
	}
	cap.release();
	outputVideo.release(); 
	cv::destroyAllWindows();
}
