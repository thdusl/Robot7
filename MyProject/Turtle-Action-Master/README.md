## 주요 기능 및 설계 명세 (미완)

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
      <td>4방향 이동 버튼(수동모드)</td>
      <td>
        방향버튼 클릭 시 선속도/각속도를 누적하여 전송<br>
        <code>manual mode: x=0.00, z=0.00</code>
      </td>
      <td>stop_all_control 호출로 제어권 회수</td>
      <td>-</td>
    </tr>
    <tr>
      <td rowspan="2"><b>자동 제어</b></td>
      <td>auto 체크박스(오토모드)</td>
      <td>
        -체크박스 활성화 시 회오리 궤적을 그리며 무한 주행<br>
        -1초 주기 로그 출력<br>
        <code>auto mode: x=0.00, z=-0.50</code>
      </td>
      <td>
        -체크박스 활성화 시 귀환 설정이 활성화 되어있다면 즉각 해제<br>
        <code>[EVENT_HOME] Home Return Aborted!</code><br>
        -체크박스 해제 시 모든 속도를 0.00으로 초기화하고 물리적 정지 명령 전송
      </td>
      <td>오토모드 중 새로운 액션(수동제어, 원점 귀환) 유입시 체크박스 강제 해제</td>
    </tr>
    <tr>
      <td>HOME 버튼(원점귀환)</td>
      <td>
        -action_server를 통해 현재 위치에서 (0,0)좌표로 자동주행<br>
        -3m 주기 피드백 로그 출력
        <code>[EVENT_HOME] Returning to Home...</code><br>
        <code>Distance remaining: 0.00m</code><br>
        -원점 도착 시 멈춰있던 수동모드 로그 출력
      </td>
      <td>주행중 중단 명령 시 cancel_goal_async를 실행하고 goal_handle을 초기화하여 리소스 정리</td>
      <td>
        서버 미연결 시 예외 알림
        <code>[EVENT_HOME] Goal Rejected</code>
      </td>
    </tr>
    <tr>
      <td rowspan="2"><b>시스템 관리</b></td>
      <td>통합 제어권 회수</td>
      <td>stop_all_control를 사용하여, 새로운 명령(수동모드/오토모드/원점귀환) 발생 시 기존에 발생한 액션(오토모드/원점귀환)을 중단 </td>
      <td></td>
      <td></td>
    </tr>
    <tr>
      <td>누적거리 측정(STOP 버튼)</td>
      <td>
        -STOP 버튼 클릭 시 서비스를 호출하여 전체 주행 거리를 계산<br>
        <code>Final Distance:0.00m</code> <br>
        -STOP 버튼 클릭 시 모든 속도를 0.0으로 초기화하고 물리적 정지 명령 전송<br>
        <code>[EVENT_STOP] Stop command sent.</code>
      </td>
    </tr>
  </tbody>
</table>
