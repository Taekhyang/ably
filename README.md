## Ably

#### 로컬 실행방법

- `cd app` 커맨드로 app 디렉토리로 이동 후  `./start.sh` 커맨드로 uvicorn asgi 서버를 띄우는 쉘 스크립트를 실행시킵니다.


#### 사용 기술

- 개발언어로는 Python3, 프레임워크로는 FastAPI 비동기 프레임워크를 사용했습니다.
- DB 는 로컬환경 실행에 맞게 sqlite3 를 사용했습니다.

#### 구현 스펙

<A. 휴대폰번호 인증 후 회원가입 로직 상세>
1. 이메일/휴대폰번호 중복체크
   - 서버에서 해당 이메일/휴대폰번호로 `users` 테이블을 확인하여 가입된 유저가 있는지 체크합니다.
2. 휴대폰 번호 입력 후 인증번호 전송
   - 서버에서 입력한 휴대폰번호로 랜덤한 6자리의 숫자를 전송합니다.
   - sqlite3 db 의 `temp_sms_auth` 테이블에 어떤 클라이언트에서 요청이 왔는지 구분하기 위한 
     `session_id`와 "휴대폰번호", "문자전송시각"을 저장합니다.
   - 최종적으로 클라이언트에 `session_id` 를 리턴합니다.     

3. 인증번호 검증
   - 클라이언트는 전송받은 인증코드와 휴대폰번호를 서버에서 받은
     `session_id` 와 함께 서버로 전달합니다.
   - 서버는 `session_id` 로 `temp_sms_auth` 테이블을 조회하여
    인증코드와 휴대폰번호가 일치하는지 검증합니다.
   - 검증이 완료되면 `temp_sms_auth` 테이블의 `is_verified` 컬럼값을
     `true` 로 변경합니다.
   - 최종적으로 클라이언트에 인증이 완료되었다는 메시지를 리턴합니다.
    
4. 회원가입
   - 클라이언트에서 이메일, 닉네임, 전화번호, 비밀번호, 이름 그리고
     `session_id` 를 서버로 전송합니다.
   - 서버는 각 필드의 유효성을 검사한 뒤 `session_id` 를 통해 `temp_sms_auth`
    테이블의 `is_verified` 컬럼이 `true` 인지 검사합니다.
   - `true` 가 맞다면, 비밀번호를 bcrypt 방식으로 salt 를 추가해 해싱한 후 utf8 로 디코딩 한 뒤 
     `users` 테이블에 나머지 개인정보와 함께 저장합니다.      
   - 회원가입 성공 후 jwt 엑세스토큰, 리프레시토큰에 user_id 를 담아 발행 후 리턴합니다.
   - 리턴 후 FastAPI 의 background task 기능을 통해 백그라운드 모드로 `temp_sms_auth` 
    테이블의 row 를 `session_id` 로 삭제합니다. 이 row 는 이제 더이상 필요가 없기 때문입니다.
     (참고로 전화번호 인증과정 중 이탈하면 쓸데없는 row 가 계속 쌓이기 때문에 이 row 들은 
     디비 스케줄링 작업 또는 프로세스 배치작업으로 삭제해주면 됩니다.)
     
<B. 로그인 후 프로필정보 확인 로직 상세>
1. 로그인
    - 클라이언트에서 회원정보의 unique 한 식별자들 (이메일, 휴대폰번호) 중 하나의 정보 + 비밀번호를
    서버에 전달하면, 서버는 식별자로 `users` 테이블에서 회원이 있는지 확인합니다.
    - 이후 해당 user 의 비밀번호 해시값과 입력받은 user 의 비밀번호 해시값을 비교한 뒤 일치하면
    jwt 토큰을 발행합니다.
      
2. 프로필정보 확인
    - 클라이언트는 프로필정보확인 API 에 요청을 보낼 때 (인증이 필요한 API 요청마다), 발급받은 jwt 액세스토큰을 `Authorization` 헤더에 
    "`bearer <access_token>`" 형태로 담아 서버에 전송합니다.  
    - 서버는 `access_token` body 에 담긴 `user_id` 를 검사하여, 매칭되는 유저의 프로필정보(이름, 이메일, 휴대폰번호, 닉네임)을 리턴합니다. 

<C. 비밀번호 리셋 로직 상세>
1. 휴대폰번호 인증
    - <A. 휴대폰번호 인증 후 회원가입 로직 상세> 의 2번, 3번 과정을 거칩니다.
      
2. 비밀번호 변경
    - 클라이언트는 새로 변경할 비밀번호 와 `session_id` 를 전달합니다.
    - 서버는 `session_id` 로 `temp_sms_auth` 테이블을 조회한 뒤 
      `is_verified`의 값이 `true` 인지 확인합니다.
    - 맞다면 비밀번호를 bcrypt 로 해시하여 utf8 로 디코딩한 값을 기존의 `password` 값 위에 업데이트 합니다.
    - 이후 A-4 방식과 같이 background task 방식으로 session_id 을 통해 `temp_sms_auth` 의 row 를 삭제합니다. 


#### 최종 구현 API 목록

- 이메일 중복체크 `GET /api/v1/users/email/duplicate-check`
- 휴대폰번호 중복체크 `GET /api/v1/users/phone/duplicate-check`
- 문자전송 `GET  /api/v1/users/sms-auth/send`
- 문자전송 인증코드 체크 `POST /api/v1/users/sms-auth/verify`
- 회원가입 `POST /api/v1/users/singup`
- 회원 프로필 보기 `GET /api/v1/users/profile`
- 로그인 `POST /api/v1/users/login`
- 비밀번호 변경 `PUT /api/v1/users/password`


#### 특별히 신경 쓴 부분

- Layered Architecture 를 적용하여 DB model, schema, service 와 api 를 분리하여 책임 소재를 나누었습니다.
- DB service 단에서 트랜잭션 단위를 묶어주고 성공시 commit, 실패시 rollback 하는 @Transactional 데코레이터를 생성하였습니다.    
- Python3 의 Contextvar 을 활용하여 비동기 요청 처리 시 
  thread-local 이 아닌 context-local 단위(request 요청 단위)로 session 을 구성되게 하였습니다.
  이는 같은 request 내에서 처리되는 여러개의 @Transactional 작업들을 하나의 트랜잭션으로 묶어줍니다. 따라서
  같은 request 내 여러개 중 하나의 트랜잭션 작업에서 에러가 발생하면 에러가 같은 세션을 공유하는 다른 트랜잭션 작업으로
  propagate 되어 rollback 됩니다. 
- 테스트 코드, background task 에서 사용될 수 있는 standalone_session 을 만들었습니다.
- timestamp_mixin 을 추가하여 created_at, updated_at 을 공통으로 가지는 모델에 적용가능하게 했습니다.
- pydantic 의 BaseModel 을 활용하여 request, response 스키마를 검사하는 레이어를 만들었습니다. 이는
  비즈니스 로직을 좀 더 깔끔하게 할 수 있는 장점이 있습니다.
- 유저 대기시간이 필요없는 부분은 먼저 필요한 응답을 리턴한 후 FastAPI 의 background task 로 처리했습니다.  
- middleware 을 활용하여 error handling 과 sqlalchemy async session 생성작업을 편리하게 하였습니다.
- FastAPI 의 dependency injection 을 활용하여 유저의 permission 을 체크하는 로직을 추가하였습니다. 해당 기능을 통해
  비즈니스 로직에 들어가는 공통된 코드를 줄일 수 있어 매우 효과적입니다.