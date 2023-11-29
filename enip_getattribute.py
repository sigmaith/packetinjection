#메모리값 변조
#연결되지 않은 명시적 메시징 연결 방식 

#ENIP 서버 IP주소 10.0.1.10으로 접속해 서비스 목록과 ID를 조회하는 명령어
#조회 대상 장치의 ip주소: address 10.0.1.10
python3 -m cpppo.server.enip.list_services -vv -a 10.0.1.10 --list-identity

#enip 기반 장치에서 속성(attribute) 값을 조회하는 명령어
#plc의 요소를 식별하는 경로 구분
#'vendor': 제조 업체 식별자, 즉 class id
#'product':제품 식별자, 즉 service id
#'instance':객체 식별자, 즉 instance id
#'attribute':속성 식별자, 즉 attribute id
python3 -m cpppo.server.enip.get_attribute'@4/101/3' '@4/102/3'

#enip 기반 장치에서 속성 값을 쓰는 명령어
python3 -m cpppo.server.enip.get_attribute '@4/102/3=(INT)15' -S -a 10.0.1.10


python3 -m cpppo.server.enip.get_attribute '@4/102/3' -S -a 10.0.1.10


#zero configuration protocol? 봉주르 구현(소프트웨어에 의존적인 취약점), 아바이 구현
#protocol 취약점
#패킷을 보내기 전에 tcpdump를 동작시켜서 공격대상과의 패킷교환을 캡처할 수 있게 구현->이런 라이브러리가 있나??
#저장된 pcap, pcapng 파일 저장 자동화
# ->> 라이브러리가 있다
# 이 파일의 스크립트가 터미널에서 실행시키게 하는 것도 라이브러리가 있나..??


#tcpdump 익히기
























