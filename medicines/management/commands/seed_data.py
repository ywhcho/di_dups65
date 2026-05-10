"""
Management command to seed sample medicine data.
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from medicines.models import Medicine, DrugInfo
from board.models import Post
from django.contrib.auth.models import User


MEDICINES = [
    {'htname': '타이레놀', 'ingred': '아세트아미노펜', 'company': '한국얀센'},
    {'htname': '게보린', 'ingred': '아세트아미노펜, 이소프로필안티피린, 카페인', 'company': '삼진제약'},
    {'htname': '판피린티', 'ingred': '아세트아미노펜, 클로르페니라민말레산염, 카페인', 'company': '동아제약'},
    {'htname': '부루펜', 'ingred': '이부프로펜', 'company': '삼일제약'},
    {'htname': '애드빌', 'ingred': '이부프로펜', 'company': '한국화이자제약'},
    {'htname': '낙센', 'ingred': '나프록센', 'company': '한국로슈'},
    {'htname': '탁센', 'ingred': '나프록센', 'company': '유한양행'},
    {'htname': '이지엔6', 'ingred': '이부프로펜', 'company': '대웅제약'},
    {'htname': '써스펜', 'ingred': '아세트아미노펜', 'company': '영일제약'},
    {'htname': '펜잘', 'ingred': '아세트아미노펜, 카페인', 'company': '종근당'},
]

DRUGINFOS = [
    {
        'htname': '타이레놀',
        'ingred': '아세트아미노펜',
        'ee': '해열, 진통',
        'ud': '성인 1회 500mg, 1일 3~4회, 4~6시간 간격',
        'nb': '알코올 복용자는 주의. 하루 최대 4,000mg 초과 금지.',
        'company': '한국얀센',
    },
    {
        'htname': '게보린',
        'ingred': '아세트아미노펜, 이소프로필안티피린, 카페인',
        'ee': '두통, 치통, 생리통, 해열',
        'ud': '성인 1회 1정, 1일 3회',
        'nb': '15세 미만 소아에게 투여하지 않는다. 음주 시 복용 금지.',
        'company': '삼진제약',
    },
    {
        'htname': '판피린티',
        'ingred': '아세트아미노펜, 클로르페니라민말레산염, 카페인',
        'ee': '감기, 코감기, 두통 완화',
        'ud': '성인 1회 2정, 1일 3회 식후 복용',
        'nb': '졸음을 유발할 수 있어 운전 및 기계 조작 주의.',
        'company': '동아제약',
    },
    {
        'htname': '부루펜',
        'ingred': '이부프로펜',
        'ee': '해열, 소염, 진통',
        'ud': '성인 1회 200~400mg, 1일 3회 식후',
        'nb': '소화기 장애 주의. 공복 복용 금지.',
        'company': '삼일제약',
    },
    {
        'htname': '애드빌',
        'ingred': '이부프로펜',
        'ee': '두통, 근육통, 생리통, 치통, 해열',
        'ud': '성인 1회 200~400mg, 4~6시간 간격, 1일 최대 1200mg',
        'nb': '위장 출혈 위험. 아스피린 알레르기 환자 금지.',
        'company': '한국화이자제약',
    },
    {
        'htname': '낙센',
        'ingred': '나프록센',
        'ee': '류마티스 관절염, 골관절염, 진통',
        'ud': '성인 1회 250~500mg, 1일 2회',
        'nb': '심혈관 위험 증가 가능. 장기 복용 주의.',
        'company': '한국로슈',
    },
    {
        'htname': '탁센',
        'ingred': '나프록센',
        'ee': '관절염, 근육통, 두통, 생리통',
        'ud': '성인 1회 250mg, 필요시 500mg, 1일 2회',
        'nb': '소화불량 주의. 신장 질환 환자 의사 상담 필요.',
        'company': '유한양행',
    },
    {
        'htname': '이지엔6',
        'ingred': '이부프로펜',
        'ee': '두통, 근육통, 생리통, 치통',
        'ud': '성인 1회 200mg, 필요시 400mg, 1일 3회',
        'nb': '소화기 궤양 환자 주의. 음주 후 복용 금지.',
        'company': '대웅제약',
    },
    {
        'htname': '써스펜',
        'ingred': '아세트아미노펜',
        'ee': '두통, 치통, 생리통, 근육통, 해열',
        'ud': '성인 1회 325~650mg, 4~6시간 간격',
        'nb': '간 질환 환자 주의. 과량 복용 금지.',
        'company': '영일제약',
    },
    {
        'htname': '펜잘',
        'ingred': '아세트아미노펜, 카페인',
        'ee': '두통, 편두통, 치통, 생리통',
        'ud': '성인 1회 1~2정, 1일 3회',
        'nb': '임산부 주의. 카페인 과민자 주의.',
        'company': '종근당',
    },
    {
        'htname': '알리 500mg',
        'ingred': '나프록센나트륨',
        'ee': '소염, 진통, 해열',
        'ud': '성인 1회 500mg, 1일 2회',
        'nb': '심혈관 질환자 주의.',
        'company': '동아제약',
    },
    {
        'htname': '모트린',
        'ingred': '이부프로펜',
        'ee': '해열, 소염, 진통',
        'ud': '성인 1회 400mg, 1일 3회',
        'nb': '임산부 3분기 복용 금지.',
        'company': '한국MSD',
    },
]


class Command(BaseCommand):
    help = '샘플 의약품 데이터를 DB에 삽입합니다.'

    def handle(self, *args, **options):
        # Medicine 데이터 삽입
        for data in MEDICINES:
            Medicine.objects.get_or_create(
                htname=data['htname'],
                defaults={'ingred': data['ingred'], 'company': data['company']}
            )
        self.stdout.write(self.style.SUCCESS(f'Medicine 데이터 {len(MEDICINES)}개 삽입 완료'))

        # DrugInfo 데이터 삽입
        for data in DRUGINFOS:
            DrugInfo.objects.get_or_create(
                htname=data['htname'],
                defaults={
                    'ingred': data['ingred'],
                    'ee': data['ee'],
                    'ud': data['ud'],
                    'nb': data['nb'],
                    'company': data['company'],
                }
            )
        self.stdout.write(self.style.SUCCESS(f'DrugInfo 데이터 {len(DRUGINFOS)}개 삽입 완료'))

        # 샘플 게시글 (관리자 계정이 있을 경우)
        if User.objects.filter(is_superuser=True).exists():
            admin = User.objects.filter(is_superuser=True).first()
            sample_posts = [
                ('의약품 정보 시스템 오픈 안내', '안녕하세요. 의약품 중복 사용 검토 전문 사이트가 오픈하였습니다.\n많은 이용 바랍니다.'),
                ('중복 성분 확인 방법 안내', '1. 상단 메뉴에서 "의약품 중복성분 보기"를 클릭하세요.\n2. 약품명을 검색하여 목록에 추가하세요.\n3. 2개 이상 선택 후 "중복성분보기" 버튼을 누르세요.'),
                ('자주 묻는 질문 (FAQ)', 'Q: 동일 성분의 약을 함께 복용해도 되나요?\nA: 동일 성분의 약을 중복 복용하면 과다 복용의 위험이 있습니다. 반드시 의사 또는 약사에게 상담하세요.'),
            ]
            for title, content in sample_posts:
                Post.objects.get_or_create(
                    title=title,
                    defaults={'content': content, 'author': admin}
                )
            self.stdout.write(self.style.SUCCESS('샘플 게시글 삽입 완료'))

        self.stdout.write(self.style.SUCCESS('모든 샘플 데이터 삽입 완료!'))
