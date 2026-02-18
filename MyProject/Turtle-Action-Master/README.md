## 📋 주요 기능 및 설계 명세

<table>
  <thead>
    <tr>
      <th>분류</th>
      <th>기능명</th>
      <th>동작 및 로그</th>
      <th>안전 설계</th>
      <th>예외 처리</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="2"><b>수동 제어</b></td>
      <td>이동 버튼</td>
      <td rowspan="2">stop_all_control 호출로 제어권 회수</td>
      <td></td>
    </tr>
    <tr>
      <td>정지 버튼</td>
      <td>Stop command 및 누적거리 출력</td>
      <td>-</td>
      <td>-</td>
    </tr>
    
    <tr>
      <td rowspan="2"><b>자동 제어</b></td>
      <td>오토 모드</td>
      <td>원형 주행 반복 로그 출력</td>
      <td>활성화 시 타 모드 즉시 해제</td>
      <td>-</td>
    </tr>
    <tr>
      <td>홈 귀환</td>
      <td>3m 주기 피드백 및 도착 확인</td>
      <td>서버 미연결 시 예외 알림</td>
      <td>-</td>
    </tr>
  </tbody>
</table>
